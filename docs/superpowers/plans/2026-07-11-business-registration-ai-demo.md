# 工商注册流程 AI 化 Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建本地一键启动的工商注册 Demo，跑通建案、资料上传、AI 预审、人工复核、补件、确认单和客户确认闭环。

**Architecture:** React/TypeScript 客户端与员工端调用 FastAPI 模块化单体；PostgreSQL 保存业务状态，MinIO 保存私有文件，Redis/RQ 执行异步预审。OCR 与 LLM 使用统一适配器，真实服务和模拟服务遵循同一契约。

**Tech Stack:** React 19, TypeScript, Vite, Ant Design, TanStack Query, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, MinIO, Redis/RQ, pytest, Vitest, Playwright, Docker Compose

---

## File Map

- `compose.yaml`: 本地基础设施与应用编排。
- `Makefile`: `setup`、`dev`、`test`、`demo-reset` 统一入口。
- `apps/api/app/`: FastAPI 入口、共享配置和按业务能力划分的模块。
- `apps/api/app/cases/`: 案件、公司、人员、股东和状态机。
- `apps/api/app/documents/`: 文件验证、私有存储和下载审计。
- `apps/api/app/preflight/`: OCR/LLM 适配器、候选字段、规则和任务。
- `apps/api/app/confirmations/`: 确认单版本、锁定与失效。
- `apps/web/src/features/customer/`: 客户资料与上传流程。
- `apps/web/src/features/review/`: 案件看板和双栏审核台。
- `apps/web/src/features/confirmation/`: 确认单查看和确认。
- `tests/e2e/`: 浏览器主流程与脱敏样例。

### Task 1: Reproducible Project Skeleton

**Files:**
- Create: `compose.yaml`, `.env.example`, `Makefile`, `README.md`
- Create: `apps/api/pyproject.toml`, `apps/api/app/main.py`, `apps/api/app/config.py`, `apps/api/tests/test_health.py`
- Create: `apps/web/package.json`, `apps/web/src/main.tsx`, `apps/web/src/App.tsx`, `apps/web/src/App.test.tsx`

- [ ] **Step 1: Write failing health and shell tests**

```python
def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

```tsx
it("renders the employee shell", () => {
  render(<App />);
  expect(screen.getByText("工商注册工作台")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run tests and verify they fail**

Run: `cd apps/api; uv run pytest tests/test_health.py -q` and `cd apps/web; npm test -- --run`
Expected: FAIL because application entry points do not exist.

- [ ] **Step 3: Implement the minimal application shells**

```python
app = FastAPI(title="Business Registration AI")

@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

```tsx
export function App() {
  return <ConfigProvider><Layout><Header>工商注册工作台</Header></Layout></ConfigProvider>;
}
```

Configure Compose services `postgres`, `minio`, `redis`, `api`, and `web`; expose only development ports and document `make setup` and `make dev`.

- [ ] **Step 4: Verify the skeleton**

Run: `docker compose config`, `cd apps/api; uv run pytest -q`, `cd apps/web; npm test -- --run`
Expected: valid Compose configuration and all tests PASS.

- [ ] **Step 5: Commit and push the module**

```bash
git add .env.example Makefile README.md compose.yaml apps
git commit -m "build: scaffold local demo environment"
git push
```

### Task 2: Case Domain and Workflow State

**Files:**
- Create: `apps/api/app/db.py`, `apps/api/app/cases/models.py`, `schemas.py`, `service.py`, `router.py`, `states.py`
- Create: `apps/api/migrations/versions/001_cases.py`
- Test: `apps/api/tests/cases/test_cases.py`, `test_states.py`

- [ ] **Step 1: Write failing domain tests**

```python
def test_case_starts_waiting_for_upload(case_service):
    case = case_service.create(CreateCase(customer_name="测试客户"))
    assert case.status == CaseStatus.WAITING_UPLOAD
    assert len(case.customer_token) >= 32

def test_invalid_transition_is_rejected():
    with pytest.raises(InvalidTransition):
        transition(CaseStatus.WAITING_UPLOAD, CaseStatus.WAITING_CONFIRMATION)
```

- [ ] **Step 2: Verify failure**

Run: `cd apps/api; uv run pytest tests/cases -q`
Expected: FAIL because case types and transition policy are missing.

- [ ] **Step 3: Implement models, transition map, migration, and API**

```python
class CaseStatus(StrEnum):
    WAITING_UPLOAD = "waiting_upload"
    PREFLIGHT = "preflight"
    NEEDS_DOCUMENTS = "needs_documents"
    HUMAN_REVIEW = "human_review"
    WAITING_CONFIRMATION = "waiting_confirmation"
    COMPLETE = "complete"

ALLOWED = {
    CaseStatus.WAITING_UPLOAD: {CaseStatus.PREFLIGHT},
    CaseStatus.PREFLIGHT: {CaseStatus.NEEDS_DOCUMENTS, CaseStatus.HUMAN_REVIEW},
    CaseStatus.NEEDS_DOCUMENTS: {CaseStatus.PREFLIGHT},
    CaseStatus.HUMAN_REVIEW: {CaseStatus.NEEDS_DOCUMENTS, CaseStatus.WAITING_CONFIRMATION},
    CaseStatus.WAITING_CONFIRMATION: {CaseStatus.COMPLETE, CaseStatus.HUMAN_REVIEW},
}
```

Expose `POST /api/v1/cases`, `GET /api/v1/cases`, `GET /api/v1/cases/{id}` and customer-token lookup.

- [ ] **Step 4: Run migration and tests**

Run: `docker compose run --rm api alembic upgrade head` and `cd apps/api; uv run pytest tests/cases -q`
Expected: migration succeeds and tests PASS.

- [ ] **Step 5: Commit and push**

```bash
git add apps/api/app/cases apps/api/app/db.py apps/api/migrations apps/api/tests/cases
git commit -m "feat: add case domain and workflow states"
git push
```

### Task 3: Customer Registration Data

**Files:**
- Create: `apps/api/app/registration/models.py`, `schemas.py`, `service.py`, `router.py`
- Create: `apps/api/app/audit/models.py`, `service.py`
- Create: `apps/api/migrations/versions/002_registration.py`
- Test: `apps/api/tests/registration/test_fields.py`

- [ ] **Step 1: Write failing validation and audit tests**

```python
def test_shareholding_must_total_100(registration_service, case):
    result = registration_service.validate(case.id, shares=[Decimal("60"), Decimal("30")])
    assert result.errors[0].code == "shareholding_total"

def test_manual_change_creates_field_version(registration_service, case, reviewer):
    registration_service.update_field(case.id, "company.name_en", "ACME LIMITED", reviewer)
    assert registration_service.history(case.id, "company.name_en")[0].source == "reviewer"
```

- [ ] **Step 2: Verify failure**

Run: `cd apps/api; uv run pytest tests/registration -q`
Expected: FAIL because registration service does not exist.

- [ ] **Step 3: Implement company/person/shareholder data and versions**

Define Pydantic schemas with `company`, `directors`, `shareholders`, `registered_address`, and `contact`; store field changes in `field_versions` with source, actor, timestamp and prior value. Expose `GET` and `PATCH /api/v1/cases/{id}/registration`.

- [ ] **Step 4: Verify API and migration**

Run: `cd apps/api; uv run pytest tests/registration -q`
Expected: all tests PASS, including decimal share totals and version history.

- [ ] **Step 5: Commit and push**

```bash
git add apps/api/app/registration apps/api/app/audit apps/api/migrations apps/api/tests/registration
git commit -m "feat: manage versioned registration data"
git push
```

### Task 4: Secure Document Upload and Storage

**Files:**
- Create: `apps/api/app/documents/models.py`, `schemas.py`, `validation.py`, `storage.py`, `service.py`, `router.py`
- Create: `apps/api/migrations/versions/003_documents.py`
- Test: `apps/api/tests/documents/test_upload.py`, `test_access.py`

- [ ] **Step 1: Write failing security tests**

```python
def test_rejects_extension_mime_mismatch(client, case_token):
    response = client.post(upload_url(case_token), files={"file": ("id.pdf", b"MZ...", "application/pdf")})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_file_signature"

def test_download_records_audit_event(document_service, document, reviewer):
    document_service.open(document.id, reviewer)
    assert document_service.audit.latest().action == "document.viewed"
```

- [ ] **Step 2: Verify failure**

Run: `cd apps/api; uv run pytest tests/documents -q`
Expected: FAIL because upload routes and validation are absent.

- [ ] **Step 3: Implement private upload and access**

Accept JPEG, PNG and PDF after extension, MIME, magic-byte, size and count checks. Store with opaque keys `cases/{case_id}/{uuid}` in a private MinIO bucket. Expose customer upload, employee preview and download routes; never return a public object URL.

- [ ] **Step 4: Verify storage behavior**

Run: `cd apps/api; uv run pytest tests/documents -q`
Expected: valid samples upload, disguised executables fail, unauthorized tokens fail, access audit passes.

- [ ] **Step 5: Commit and push**

```bash
git add apps/api/app/documents apps/api/migrations apps/api/tests/documents
git commit -m "feat: add secure private document uploads"
git push
```

### Task 5: OCR and LLM Adapter Contracts

**Files:**
- Create: `apps/api/app/preflight/contracts.py`, `providers/base.py`, `providers/mock.py`, `providers/ocr.py`, `providers/llm.py`, `jobs.py`, `router.py`
- Create: `apps/api/tests/preflight/test_contracts.py`, `test_jobs.py`, `fixtures/provider_responses/`

- [ ] **Step 1: Write failing adapter contract tests**

```python
@pytest.mark.parametrize("provider", [MockOcrProvider(), DefaultOcrProvider(fake_transport)])
def test_ocr_provider_returns_candidates(provider, sample_id_card):
    result = provider.extract(sample_id_card)
    assert result.candidates[0].field_path == "directors[0].document_number"
    assert 0 <= result.candidates[0].confidence <= 1
    assert result.candidates[0].source.page == 1
```

- [ ] **Step 2: Verify failure**

Run: `cd apps/api; uv run pytest tests/preflight/test_contracts.py -q`
Expected: FAIL because provider contracts are missing.

- [ ] **Step 3: Implement provider-neutral results and task lifecycle**

```python
class FieldCandidate(BaseModel):
    field_path: str
    value: str
    confidence: float = Field(ge=0, le=1)
    source: SourceReference

class PreflightResult(BaseModel):
    candidates: list[FieldCandidate]
    findings: list[Finding]
    provider: str
```

Select providers through `OCR_PROVIDER` and `LLM_PROVIDER`; validate JSON responses, redact sensitive values from logs, persist queued/running/succeeded/failed states, and expose retry.

- [ ] **Step 4: Verify contracts and failure recovery**

Run: `cd apps/api; uv run pytest tests/preflight -q`
Expected: mock and recorded real-provider transports satisfy the same schema; timeout and invalid JSON become retryable failures.

- [ ] **Step 5: Commit and push**

```bash
git add apps/api/app/preflight apps/api/tests/preflight .env.example
git commit -m "feat: add pluggable AI preflight adapters"
git push
```

### Task 6: Deterministic Review Rules and Commands

**Files:**
- Create: `apps/api/app/preflight/rules.py`, `review_service.py`
- Test: `apps/api/tests/preflight/test_rules.py`, `test_review_commands.py`

- [ ] **Step 1: Write failing rule tests**

```python
def test_address_proof_older_than_three_months_is_missing():
    finding = check_address_proof(date(2026, 3, 31), today=date(2026, 7, 11))
    assert finding.code == "address_proof_expired"

def test_confirmed_ai_candidate_does_not_overwrite_customer_value(review_service):
    result = review_service.accept_candidate(field_with_customer_value, ai_candidate)
    assert result.requires_explicit_override is True
```

- [ ] **Step 2: Verify failure**

Run: `cd apps/api; uv run pytest tests/preflight/test_rules.py tests/preflight/test_review_commands.py -q`
Expected: FAIL because rules and commands are missing.

- [ ] **Step 3: Implement rule priority and review commands**

Implement required-material, calendar three-month, 30-character business scope, phone format, 100% share total and confidence threshold rules. Provide commands to accept/reject candidates, request documents, retry preflight and approve review. Deterministic blocking findings override LLM recommendations.

- [ ] **Step 4: Verify transitions and rules**

Run: `cd apps/api; uv run pytest tests/cases tests/preflight -q`
Expected: all rule matrices and allowed transitions PASS.

- [ ] **Step 5: Commit and push**

```bash
git add apps/api/app/preflight apps/api/tests/preflight
git commit -m "feat: enforce registration preflight rules"
git push
```

### Task 7: Customer Portal and Employee Review Workbench

**Files:**
- Create: `apps/web/src/api/client.ts`, `types.ts`
- Create: `apps/web/src/features/customer/CustomerFlow.tsx`, `MaterialChecklist.tsx`, `RegistrationForm.tsx`
- Create: `apps/web/src/features/review/CaseBoard.tsx`, `ReviewWorkbench.tsx`, `FieldReview.tsx`, `DocumentPreview.tsx`
- Test: colocated `*.test.tsx` files

- [ ] **Step 1: Write failing interaction tests**

```tsx
it("shows missing materials and uploads against the selected role", async () => {
  render(<MaterialChecklist caseToken="token" />);
  expect(await screen.findByText("还需补交 2 项")).toBeVisible();
  await userEvent.upload(screen.getByLabelText("上传地址证明"), pdfFile);
  expect(api.uploadDocument).toHaveBeenCalledWith(expect.objectContaining({ role: "director" }));
});

it("keeps source document beside the selected risky field", async () => {
  render(<ReviewWorkbench caseId="case-1" />);
  await userEvent.click(await screen.findByText("证件号"));
  expect(screen.getByLabelText("材料预览")).toHaveAttribute("data-page", "1");
});
```

- [ ] **Step 2: Verify failure**

Run: `cd apps/web; npm test -- --run`
Expected: FAIL because feature components do not exist.

- [ ] **Step 3: Implement the approved layouts**

Build a step-based customer flow with persistent completeness status and a dense employee board. Implement the approved split review view, inline confidence/source badges, deterministic error priority, retry states and responsive stacking on narrow screens.

- [ ] **Step 4: Verify UI quality**

Run: `cd apps/web; npm run lint && npm run typecheck && npm test -- --run`
Expected: all checks PASS; no overflow at 375px and 1440px component viewports.

- [ ] **Step 5: Commit and push**

```bash
git add apps/web/src
git commit -m "feat: build customer and review workflows"
git push
```

### Task 8: Versioned Confirmation Documents

**Files:**
- Create: `apps/api/app/confirmations/models.py`, `schemas.py`, `renderer.py`, `service.py`, `router.py`
- Create: `apps/api/migrations/versions/004_confirmations.py`
- Create: `apps/web/src/features/confirmation/ConfirmationView.tsx`
- Test: `apps/api/tests/confirmations/test_confirmations.py`, frontend component test

- [ ] **Step 1: Write failing confirmation tests**

```python
def test_key_field_change_invalidates_confirmation(confirmation_service, confirmed_case):
    confirmation_service.on_field_changed(confirmed_case.id, "company.name_en")
    assert confirmation_service.current(confirmed_case.id).status == "invalidated"
    assert confirmed_case.status == CaseStatus.HUMAN_REVIEW

def test_non_key_field_change_keeps_confirmation(confirmation_service, confirmed_case):
    confirmation_service.on_field_changed(confirmed_case.id, "contact.notes")
    assert confirmation_service.current(confirmed_case.id).status == "confirmed"
```

- [ ] **Step 2: Verify failure**

Run: `cd apps/api; uv run pytest tests/confirmations -q`
Expected: FAIL because confirmation service is missing.

- [ ] **Step 3: Implement immutable snapshots and customer confirmation**

Create canonical JSON snapshots, SHA-256 hashes, versioned PDF/Word renderer output and confirmation audit events. Only reviewed cases can generate confirmations; only the current version can be confirmed.

- [ ] **Step 4: Verify backend and frontend**

Run: `cd apps/api; uv run pytest tests/confirmations -q` and `cd apps/web; npm test -- --run ConfirmationView`
Expected: generation, confirmation, invalidation and re-confirmation tests PASS.

- [ ] **Step 5: Commit and push**

```bash
git add apps/api/app/confirmations apps/api/migrations apps/api/tests/confirmations apps/web/src/features/confirmation
git commit -m "feat: add versioned customer confirmations"
git push
```

### Task 9: Demo Seed, End-to-End Verification, and Handoff

**Files:**
- Create: `apps/api/app/demo/seed.py`, `reset.py`
- Create: `tests/e2e/demo-flow.spec.ts`, `tests/e2e/fixtures/`
- Modify: `README.md`, `Makefile`, `compose.yaml`

- [ ] **Step 1: Write the failing end-to-end scenario**

```ts
test("registration demo completes after a supplement", async ({ page }) => {
  const { employeeUrl, customerUrl } = await seedCase();
  await page.goto(customerUrl);
  await uploadRequiredMaterialsExceptAddress(page);
  await expect(page.getByText("还需补交 1 项")).toBeVisible();
  await page.goto(employeeUrl);
  await page.getByRole("button", { name: "退回补件" }).click();
  await page.goto(customerUrl);
  await page.getByLabel("上传地址证明").setInputFiles("tests/e2e/fixtures/address-proof.pdf");
  await completePreflightAndReview(page, employeeUrl);
  await confirmCurrentVersion(page, customerUrl);
  await expect(page.getByText("注册信息已确认")).toBeVisible();
});
```

- [ ] **Step 2: Verify failure**

Run: `npm run test:e2e -- demo-flow.spec.ts`
Expected: FAIL until seed/reset commands and full routing are wired.

- [ ] **Step 3: Add deterministic demo data and operator documentation**

Implement idempotent `make demo-seed` and destructive, explicitly confirmed `make demo-reset`. Add only synthetic fixtures. Document provider configuration, simulated fallback, demo script, security limitations and troubleshooting.

- [ ] **Step 4: Run the complete verification suite**

Run: `make test`, `docker compose up -d --build`, `make demo-seed`, `npm run test:e2e`, `docker compose ps`
Expected: all unit/integration/component/E2E tests PASS; every required service reports healthy.

- [ ] **Step 5: Inspect desktop and mobile screenshots**

Run: `npm run test:e2e -- --project=chromium --update-snapshots`
Expected: customer flow fits 375x812; review workbench fits 1440x900 without overlap, blank preview or clipped controls.

- [ ] **Step 6: Commit and push final Demo module**

```bash
git add README.md Makefile compose.yaml apps/api/app/demo tests/e2e
git commit -m "test: complete reproducible demo workflow"
git push
```

## Final Release Gate

- Run `git status --short` and require a clean worktree.
- Run `make test` and retain the passing summary.
- Run `git log --oneline origin/master..HEAD`; push only verified commits.
- Confirm the GitHub repository contains no `.env`, real identity document, customer data, object-storage data or provider response containing sensitive text.
- Tag the accepted Demo only after user acceptance; do not create a release tag during implementation.
