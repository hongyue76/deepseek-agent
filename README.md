# DeepSeek Web Agent

这是一个基于 Flask 的网页版 AI Agent，使用 DeepSeek API 提供智能对话服务。

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/deepseek-agent.git
cd deepseek-agent
```

### 2. 设置环境变量
创建 `.env` 文件并添加您的 DeepSeek API 密钥：
```env
DEEPSEEK_API_KEY=您的实际API密钥
```

> **重要提示**：您需要自己的 DeepSeek API 密钥：
> 1. 访问 [DeepSeek 控制台](https://platform.deepseek.com/)
> 2. 注册/登录账号
> 3. 创建 API 密钥
> 4. 复制密钥到 `.env` 文件

### 3. 安装依赖
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 4. 启动应用
```bash
python app.py
```

### 5. 访问应用
打开浏览器访问：http://localhost:5000

## 部署到公网
参考 [DEPLOY.md](DEPLOY.md) 了解如何部署到公网

## 贡献指南
欢迎提交 Pull Request！请确保：
- 不包含任何敏感信息（如 API 密钥）
- 更新测试用例
- 更新文档

## 许可
本项目采用 [MIT 许可证](LICENSE)
