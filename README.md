# RippleProof

**Change one rule. Prove everything changed.**

RippleProof is a policy change impact and executable verification MVP built for the AI Builders Hackathon 2026.

## Phase 2 status

The project now includes:

- FastAPI backend with separated **Analyze** and **Verify** endpoints
- Deterministic policy contract and boundary-test engine
- 5 seeded NovaCommerce artifacts
- Semantic/rule-based impact findings
- Patch diffs with a human approval step in the UI
- Next.js 15 + TypeScript frontend
- Interactive React Flow dependency graph
- Before/after executable verification
- SHA-256 proof receipt

## 1. Run the backend

Open a terminal in `rippleproof/backend`.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend: http://127.0.0.1:8000

API docs: http://127.0.0.1:8000/docs

Run tests:

```powershell
pytest -q
```

## 2. Run the frontend

Open a second terminal in `rippleproof/frontend`.

```powershell
copy .env.local.example .env.local
npm install
npm run dev
```

Frontend: http://localhost:3000

## Flagship demo flow

1. Click **Analyze flagship change**.
2. RippleProof traces the refund-policy change from **30 days → 14 days**.
3. Inspect the dependency graph. The backend API should be the critical mismatch.
4. Review the proposed patches and click **Approve 4 patches**.
5. Click **Run verification**.
6. Six deterministic boundary tests should pass.
7. The Proof Receipt should show `VERIFIED` and an evidence SHA-256 hash.

## Core product principle

> LLMs interpret meaning. Deterministic tests establish proof.
