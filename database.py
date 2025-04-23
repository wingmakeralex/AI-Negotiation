import os
import sqlite3
from datetime import datetime

def get_db_filename(prolific_id):
    # 使用固定的文件名
    return f'chat_history_{prolific_id}.db'

def get_db_connection(prolific_id):
    if os.getenv('DATABASE_URL'):
        # Heroku 环境
        import psycopg2
        DATABASE_URL = os.getenv('DATABASE_URL')
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(DATABASE_URL)
    else:
        # 本地环境使用 SQLite
        db_file = get_db_filename(prolific_id)
        return sqlite3.connect(db_file)

def save_to_txt(prolific_id, role, content):
    # 创建logs目录（如果不存在）
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 使用固定的文件名，每个用户一个文件
    filename = f'logs/chat_log_{prolific_id}.txt'
    
    # 格式化消息
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] {role}: {content}\n"
    
    # 写入文件
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(message)

def init_db(prolific_id):
    try:
        conn = get_db_connection(prolific_id)
        c = conn.cursor()
        
        # 创建表
        c.execute('''
            CREATE TABLE IF NOT EXISTS conversations
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             prolific_id TEXT NOT NULL,
             created_at DATETIME NOT NULL)
        ''')
        print(f"conversations 表创建成功 for {prolific_id}")
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             conversation_id INTEGER NOT NULL,
             role TEXT NOT NULL,
             content TEXT NOT NULL,
             timestamp DATETIME NOT NULL,
             FOREIGN KEY (conversation_id) REFERENCES conversations (id))
        ''')
        print(f"chat_messages 表创建成功 for {prolific_id}")
        
        conn.commit()
        conn.close()
        db_file = get_db_filename(prolific_id)
        print(f"数据库初始化完成: {db_file}")
        return db_file
    except Exception as e:
        print(f"数据库初始化过程中出错: {str(e)}")
        raise e

def save_message(role, content, conversation_id=None, prolific_id=None):
    if prolific_id is None:
        raise ValueError("prolific_id is required")
        
    conn = get_db_connection(prolific_id)
    c = conn.cursor()
    
    if conversation_id is None:
        # 创建新的对话
        c.execute('INSERT INTO conversations (prolific_id, created_at) VALUES (?, ?)', 
                 (prolific_id, datetime.now()))
        conversation_id = c.lastrowid
    
    c.execute('''
        INSERT INTO chat_messages (conversation_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (conversation_id, role, content, datetime.now()))
    
    conn.commit()
    conn.close()
    
    # 同时保存到txt文件
    save_to_txt(prolific_id, role, content)
    
    return conversation_id

def get_chat_history(conversation_id=None, prolific_id=None):
    if prolific_id is None:
        return []
        
    conn = get_db_connection(prolific_id)
    c = conn.cursor()
    
    if conversation_id is None:
        # 获取最新的对话ID
        c.execute('SELECT id FROM conversations ORDER BY created_at DESC LIMIT 1')
        result = c.fetchone()
        if result:
            conversation_id = result[0]
        else:
            return []
    
    c.execute('''
        SELECT role, content, timestamp 
        FROM chat_messages 
        WHERE conversation_id = ? 
        ORDER BY timestamp ASC
    ''', (conversation_id,))
    
    messages = c.fetchall()
    conn.close()
    return messages 