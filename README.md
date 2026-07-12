# 工商注册流程 AI 化 Demo

本项目用于本地演示香港工商注册案件的资料收集、AI 预审、人工复核和客户确认流程。仓库不得存放真实客户资料或 API 密钥。

## 本地启动

前置条件：Docker Desktop、Node.js 22+、Python 3.12+。

```powershell
Copy-Item .env.example .env
docker compose up --build
```

启动后访问：

- Web: http://localhost:5173
- API: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

## 测试

```powershell
cd apps/api
python -m uv run pytest -q

cd ../web
npm test -- --run
```

当前默认使用模拟 OCR 与 LLM 适配器，后续模块将加入真实服务配置。
