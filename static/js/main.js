document.addEventListener('DOMContentLoaded', () => {
    console.log('页面加载完成');
    const prolificIdContainer = document.getElementById('prolific-id-container');
    const chatInterface = document.getElementById('chat-interface');
    const prolificIdInput = document.getElementById('prolific-id');
    const confirmIdButton = document.getElementById('confirm-id');
    const displayProlificId = document.getElementById('display-prolific-id');
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    let currentConversationId = null;
    let currentProlificId = null;

    if (!prolificIdContainer || !chatInterface || !prolificIdInput || !confirmIdButton || 
        !displayProlificId || !chatMessages || !userInput || !sendButton) {
        console.error('找不到必要的DOM元素');
        return;
    }

    // 处理Prolific ID确认
    confirmIdButton.addEventListener('click', () => {
        const prolificId = prolificIdInput.value.trim();
        if (!prolificId) {
            alert('请输入有效的Prolific ID');
            return;
        }
        
        // 保存Prolific ID
        currentProlificId = prolificId;
        displayProlificId.textContent = prolificId;
        
        // 切换界面
        prolificIdContainer.style.display = 'none';
        chatInterface.style.display = 'flex';
        
        // 加载历史消息
        loadChatHistory();
    });

    // 发送消息
    sendButton.addEventListener('click', () => {
        console.log('发送按钮被点击');
        sendMessage();
    });

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            console.log('Enter键被按下');
            sendMessage();
        }
    });

    async function sendMessage() {
        const message = userInput.value.trim();
        console.log('准备发送消息:', message);
        if (!message) return;

        // 禁用输入和发送按钮
        userInput.disabled = true;
        sendButton.disabled = true;

        // 显示用户消息
        appendMessage(message, 'user');
        userInput.value = '';

        try {
            console.log('发送请求到服务器...');
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message,
                    conversation_id: currentConversationId,
                    prolific_id: currentProlificId
                }),
            });

            console.log('收到服务器响应:', response.status);
            const data = await response.json();
            console.log('响应数据:', data);
            
            if (data.status === 'success') {
                appendMessage(data.response, 'assistant');
                currentConversationId = data.conversation_id;
            } else {
                appendMessage('抱歉，发生错误：' + data.response, 'assistant');
            }
        } catch (error) {
            console.error('发送消息时出错:', error);
            appendMessage('抱歉，发生错误：' + error.message, 'assistant');
        } finally {
            // 重新启用输入和发送按钮
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus();
        }
    }

    function appendMessage(message, sender) {
        console.log('添加消息:', sender, message);
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function loadChatHistory() {
        try {
            console.log('加载历史消息...');
            const response = await fetch('/history');
            const messages = await response.json();
            console.log('历史消息:', messages);
            
            if (messages.length > 0) {
                // 获取最新的对话ID
                const lastMessage = messages[messages.length - 1];
                currentConversationId = lastMessage[0];  // conversation_id
                
                messages.forEach(msg => {
                    const [_, role, content] = msg;
                    appendMessage(content, role);
                });
            }
        } catch (error) {
            console.error('加载历史消息失败：', error);
        }
    }
}); 