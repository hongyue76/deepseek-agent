from waitress import serve
from app import app

if __name__ == "__main__":
    print("服务器运行中: http://localhost:8080")
    serve(app, host="0.0.0.0", port=8080)