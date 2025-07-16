import os
import json
import requests
from flask import Flask, request, render_template, Response, send_from_directory
from dotenv import load_dotenv
from flask_cors import CORS  # 添加CORS支持

load_dotenv()
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 获取API密钥
API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"


def call_deepseek(prompt):
    """调用DeepSeek API（带错误处理）"""
    print(f"调用DeepSeek API，输入内容: {prompt}")  # 调试日志
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            stream=True,
            timeout=30
        )
        response.raise_for_status()
        print(f"API响应状态: {response.status_code}")
        return response
    except Exception as e:
        print(f"API调用错误: {str(e)}")
        return None


@app.route("/")
def home():
    print("访问首页")
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    print("收到聊天请求")
    user_input = request.json.get("message")
    print(f"用户输入: {user_input}")

    if not user_input or len(user_input.strip()) == 0:
        print("空输入错误")
        return jsonify({"error": "空输入"}), 400

    # 流式返回响应
    def generate():
        api_response = call_deepseek(user_input)
        if not api_response:
            print("API响应为空")
            yield "data: {\"error\":\"API服务不可用\"}\n\n"
            return

        try:
            print("开始流式响应")
            for line in api_response.iter_lines():
                if line:
                    decoded = line.decode('utf-8').strip()
                    print(f"收到数据块: {decoded[:100]}...")  # 打印前100字符
                    if decoded.startswith('data:'):
                        yield f"{decoded}\n\n"
            print("流式响应完成")
        except Exception as e:
            print(f"流处理错误: {str(e)}")
            yield f"data: {{\"error\":\"流处理错误: {str(e)}\"}}\n\n"

    return Response(generate(), mimetype='text/event-stream')


# Favicon处理
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/test_cors")
def test_cors():
    return "CORS 模块加载成功！", 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)