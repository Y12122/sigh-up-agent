# 工商注册流程 AI 化 Demo

本项目演示香港工商注册案件的资料收集、OCR/LLM 预审、确定性规则、人工复核和客户确认。仓库中的姓名、证件号、地址与文件均为虚构脱敏数据。

## 启动

前置条件：Docker Desktop、Node.js 22+、Python 3.12+。

```powershell
Copy-Item .env.example .env
docker compose up -d --build
docker compose run --rm api uv run alembic upgrade head
docker compose run --rm api uv run python -m app.demo.seed
```

访问入口：

- Web：http://localhost:5173
- API 文档：http://localhost:8000/docs
- MinIO Console：http://localhost:9001

Web 顶部可在员工工作台与客户上传端之间切换。员工看板点击首个案件进入双栏审核台；客户上传端点击“保存并继续”进入确认单。

## Demo 数据

初始化命令可重复执行，不会重复创建固定演示案件：

```powershell
docker compose run --rm api uv run python -m app.demo.seed
```

清空全部 Demo 数据需要显式确认，生产环境会拒绝执行：

```powershell
docker compose run --rm api uv run python -m app.demo.reset --confirm
docker compose run --rm api uv run alembic upgrade head
```

PostgreSQL 数据保存在 Docker 命名卷 `business-registration-demo_postgres-data`，MinIO 文件保存在 `business-registration-demo_minio-data`。这些运行数据不进入 Git。

## AI 服务

默认配置使用 Mock OCR/LLM，保证无凭证时可稳定演示：

```dotenv
OCR_PROVIDER=mock
LLM_PROVIDER=mock
```

真实服务通过 HTTP 适配器接入，在 `.env` 中配置端点和密钥。不要把 `.env`、真实客户材料或供应商响应提交到仓库。

```dotenv
OCR_PROVIDER=http
OCR_ENDPOINT=https://provider.example/ocr
OCR_API_KEY=replace-locally
LLM_PROVIDER=http
LLM_ENDPOINT=https://provider.example/review
LLM_API_KEY=replace-locally
```

## 验证

```powershell
cd apps/api
python -m uv run pytest -q

cd ../web
npm run typecheck
npm test -- --run --maxWorkers=1
npm run build
npm run test:e2e
```

Playwright 使用本机 Microsoft Edge，覆盖 1440×900 桌面和 375×812 移动视口。

## 当前边界

- 后端案件、注册资料、文件、预审、规则、审核命令和确认单 API 已通过自动化与 PostgreSQL/MinIO 集成验证。
- Web 当前使用固定脱敏演示数据展示工作流，上传、审核和确认操作尚未动态绑定后端案件 API；Playwright 覆盖的是 UI 主流程，后端业务闭环由 API 测试覆盖。
- 未接入企业微信、邮箱、TPSI、RPA、支付和签署。
- 真实 OCR/LLM 服务需要按供应商协议配置端点，并使用脱敏测试材料验收。
