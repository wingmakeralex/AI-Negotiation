from flask import Flask, render_template, request, jsonify, redirect, url_for
import openai
import os
from dotenv import load_dotenv
from database import init_db, save_message, get_chat_history
import requests
import json

load_dotenv()

app = Flask(__name__)

# 从环境变量读取 API 密钥
# 注意：Vercel 环境变量中存储的应该是 "sk-proj-..." 这部分，不包含 "Bearer "
api_key_from_env = os.environ.get("OPENAI_API_KEY") 
if not api_key_from_env:
    print("错误：未在环境变量中找到 OPENAI_API_KEY")
    # 你可以在这里决定如何处理：是退出应用、返回错误，还是使用默认值（不推荐用于生产）
    # 为了部署，我们暂时设置一个无效的占位符，但 Vercel 上的环境变量必须设置正确
    OPENAI_API_KEY_HEADER = "Bearer invalid-key-please-set-in-vercel"
else:
    OPENAI_API_KEY_HEADER = f"Bearer {api_key_from_env}" # 添加 "Bearer " 前缀

# 不再需要下面这行硬编码的密钥
# OPENAI_API_KEY = "Bearer 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"

# 不再需要下面这行硬编码的 Endpoint
# OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"

# 也不再需要下面这行硬编码的 Model
# OPENAI_MODEL = 'gpt-3.5-turbo'

# 不再使用 openai 库的配置
# openai.api_key = api_key
# openai.api_base = "https://api.openai.com/v1"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat_page():
    prolific_id = request.args.get('prolific_id')
    if not prolific_id:
        return redirect(url_for('index'))
    return render_template('chat.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/admin/refresh')
def refresh():
    return redirect(url_for('admin'))

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    conversation_id = request.json.get('conversation_id')
    prolific_id = request.json.get('prolific_id')
    
    if not prolific_id:
        return jsonify({
            'response': '请先输入Prolific ID',
            'status': 'error'
        })
    
    try:
        # 初始化数据库（如果不存在）
        init_db(prolific_id)
        
        # 获取历史消息
        history = get_chat_history(conversation_id, prolific_id)
        
        # 构建消息历史
        messages = []
        for role, content, _ in history:
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_message})
        
        # 直接使用提供的格式发送请求
        headers = {
            "Authorization": OPENAI_API_KEY_HEADER,  # 使用从环境变量组合的 Header
            "Content-Type": "application/json"
        }
        
        data = {
            "model": OPENAI_MODEL,
            "messages": messages
        }
        
        print(f"请求 URL: {OPENAI_ENDPOINT}")
        print(f"请求头 Authorization: Bearer {api_key_from_env[:5]}..." if api_key_from_env else "Authorization Header not set properly!") 
        
        response = requests.post(
            OPENAI_ENDPOINT,
            headers=headers,
            json=data
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            error_message = f"API Error: {response.status_code} - {response.text}"
            print(f"Error details: {error_message}")
            return jsonify({
                'response': error_message,
                'status': 'error'
            })
        
        response_data = response.json()
        assistant_message = response_data['choices'][0]['message']['content']
        
        # 保存用户消息
        conversation_id = save_message("user", user_message, conversation_id, prolific_id)
        # 保存助手消息
        save_message("assistant", assistant_message, conversation_id, prolific_id)
        
        return jsonify({
            'response': assistant_message,
            'status': 'success',
            'conversation_id': conversation_id
        })
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(f"Error details: {error_message}")
        return jsonify({
            'response': error_message,
            'status': 'error'
        })

@app.route('/api/history')
def history():
    prolific_id = request.args.get('prolific_id')
    if not prolific_id:
        return jsonify([])
    messages = get_chat_history(prolific_id=prolific_id)
    return jsonify(messages)

if __name__ == '__main__':
    app.run(debug=True) 