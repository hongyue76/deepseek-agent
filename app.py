import os
import json
import requests
from flask import Flask, request, render_template, Response, jsonify
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
app = Flask(__name__)

# 获取API密钥
API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

# 法律专业系统提示词 - 详细优化版
LEGAL_SYSTEM_PROMPT = """
你是一名专业的法律AI顾问，精通中国法律体系。请严格遵循以下要求：

1. **法律依据**：
   - 回答必须基于现行有效的中国法律法规
   - 引用具体法律条文时注明完整出处（法律名称+条款号）
   - 优先引用最新修订版本的法律

2. **回答结构**：
   [法律分析]
     根据《相关法律名称》第X条：...
   [实践建议]
     在实际操作中，建议您...
   [风险提示]
     需要注意的风险包括...
   [后续步骤]
     您可以采取的下一步行动...

3. **专业要求**：
   - 区分事实描述和法律意见
   - 当问题涉及具体案件时，必须提醒用户咨询执业律师
   - 对于不确定的问题，明确说明知识局限
   - 涉及不同法律领域时，明确说明适用法律范围

4. **免责声明**：
   每个回答必须以以下内容结束：
   "注：以上分析仅供参考，不构成正式法律意见。具体案件请咨询专业律师，并以其意见为准。"

5. **特别领域**：
   - 劳动法：优先引用《劳动合同法》《劳动争议调解仲裁法》
   - 民法：优先引用《民法典》
   - 刑法：优先引用《刑法》及最新司法解释
   - 婚姻家庭：引用《民法典》婚姻家庭编
   - 公司商事：引用《公司法》《合伙企业法》

请确保回答专业、准确、实用。
"""


def call_deepseek(prompt, is_legal_mode=False):
    """调用DeepSeek API（带错误处理）"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 根据模式构造消息
    messages = []

    if is_legal_mode:
        # 法律模式：添加系统提示词
        messages.append({"role": "system", "content": LEGAL_SYSTEM_PROMPT})
        messages.append({"role": "user", "content": prompt})
    else:
        # 普通模式
        messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "stream": True,
        "temperature": 0.3 if is_legal_mode else 0.7,  # 法律模式更严谨
        "max_tokens": 2048
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            stream=True,
            timeout=60
        )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"API调用错误: {str(e)}")
        return None
    except Exception as e:
        print(f"意外错误: {str(e)}")
        return None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效的JSON数据"}), 400

        user_input = data.get("message", "")
        mode = data.get("mode", "general")  # 默认为通用模式
        is_legal_mode = (mode == "legal")

        if not user_input or len(user_input.strip()) == 0:
            return jsonify({"error": "输入不能为空"}), 400

        # 流式返回响应
        def generate():
            api_response = call_deepseek(user_input, is_legal_mode)
            if not api_response:
                yield "data: {\"error\":\"API服务不可用\"}\n\n"
                return

            try:
                for line in api_response.iter_lines():
                    if line:
                        decoded = line.decode('utf-8').strip()
                        if decoded.startswith('data:'):
                            yield f"{decoded}\n\n"
            except requests.exceptions.ChunkedEncodingError as e:
                print(f"流处理中断: {str(e)}")
                yield "data: {\"error\":\"响应流中断，请重试\"}\n\n"
            except Exception as e:
                print(f"流处理错误: {str(e)}")
                yield f"data: {{\"error\":\"流处理错误: {str(e)}\"}}\n\n"

        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        print(f"服务器错误: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500


# Favicon处理
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


# 健康检查端点
@app.route('/health')
def health_check():
    return jsonify({
        "status": "ok",
        "version": "1.1.0",
        "legal_mode_supported": True
    })


if __name__ == "__main__":
    # 自动创建static目录
    static_dir = os.path.join(app.root_path, 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    app.run(host='0.0.0.0', port=5000, debug=True)