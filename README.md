<div align="center">

# 🌊 RippleProof

### AI-Powered Policy Change Intelligence

**Detect policy changes. Trace their impact. Repair affected systems. Verify the result.**

<br/>

[![Live Demo](https://img.shields.io/badge/🌐_LIVE_DEMO-Launch_RippleProof-000000?style=for-the-badge)](https://ripple-proof.vercel.app/)
[![Demo Video](https://img.shields.io/badge/▶_DEMO_VIDEO-Watch_Now-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/PuTn0-4_17Y)
[![GitHub](https://img.shields.io/badge/GitHub-Source_Code-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/alishasajjad/RippleProof)

<br/>

![Next.js](https://img.shields.io/badge/Next.js-Frontend-000000?logo=nextdotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-Frontend-000000?logo=vercel&logoColor=white)
![Railway](https://img.shields.io/badge/Railway-Backend-0B0D0E?logo=railway&logoColor=white)

<br/>

> **From Policy Change to Executable Proof.**

</div>

---

## 📌 Overview

**RippleProof** is an AI-powered policy change intelligence platform designed to help organizations understand, trace, repair, and verify the real operational impact of business policy changes.

Updating a policy document does not guarantee that the systems, code, rules, and organizational artifacts implementing that policy have also been updated.

RippleProof addresses this gap.

The platform transforms natural-language policy changes into structured contracts, analyzes affected organizational artifacts, identifies stale implementations, generates evidence-backed repair proposals, keeps a human reviewer in control, and performs deterministic verification against the updated policy.

The result is a persistent and auditable evidence trail:

```text
Policy Change
      ↓
Semantic Analysis
      ↓
Impact Detection
      ↓
Evidence
      ↓
Repair Proposal
      ↓
Human Approval
      ↓
Deterministic Verification
      ↓
Executable Proof
```

---

## 🎯 The Problem

Organizations continuously update policies, business rules, compliance requirements, and operational procedures.

However, a critical problem remains:

> **A policy can change on paper while the systems enforcing it continue using the old rule.**

Consider a customer refund policy.

### Previous Policy

```text
Customers may request a refund within 30 days of purchase.
```

### Updated Policy

```text
Customers may request a refund within 14 days of purchase.
```

An existing system may still contain:

```python
def is_refund_eligible(purchase_age_days):
    return purchase_age_days <= 30
```

The official policy now requires **14 days**, while the implementation still allows **30 days**.

This creates a gap between:

```text
Policy Intent ≠ Operational Behavior
```

RippleProof is designed to detect, repair, and verify this gap.

---

## 💡 The RippleProof Approach

RippleProof treats a policy update as an executable change-management workflow rather than simply a document modification.

The platform follows seven core stages:

### 1️⃣ Understand

Interpret the old and new policy using semantic analysis.

### 2️⃣ Structure

Transform the policy change into a machine-readable policy contract.

### 3️⃣ Trace

Analyze organizational artifacts to identify affected implementations.

### 4️⃣ Explain

Produce evidence showing why an artifact conflicts with the updated policy.

### 5️⃣ Repair

Generate a targeted repair proposal.

### 6️⃣ Review

Keep a human reviewer responsible for approving the proposed change.

### 7️⃣ Verify

Run deterministic tests and preserve the results as evidence.

---

## ✨ Core Features

### 🧠 AI-Powered Semantic Policy Analysis

RippleProof interprets natural-language policy changes and extracts their operational meaning using LLM-powered semantic analysis.

---

### 📑 Machine-Readable Policy Contracts

Policy changes are transformed into structured representations containing information such as:

- Subject
- Policy attribute
- Previous rule
- Updated rule
- Operators
- Values
- Units
- Change type
- Risk domain
- Boundary values

This makes policy changes easier to analyze programmatically.

---

### 🔎 Impact Detection

Uploaded organizational artifacts are analyzed against the updated policy.

RippleProof determines:

- Whether an artifact is affected
- Which rule it currently implements
- Whether that implementation is stale
- The severity of the impact
- Confidence in the finding
- The relationship between the artifact and policy
- Evidence supporting the finding

---

### 📋 Evidence-Backed Reasoning

RippleProof does not only report that something is wrong.

Each impact can include evidence explaining **where the conflict exists and why it matters**.

This makes findings easier for reviewers to understand and audit.

---

### 🛠️ Repair Proposals

When RippleProof detects a stale implementation, it can generate a targeted repair.

For example:

```diff
 def is_refund_eligible(purchase_age_days):
-    return purchase_age_days <= 30
+    return purchase_age_days <= 14
```

The proposed change directly reflects the updated policy requirement.

---

### 👤 Human-in-the-Loop Approval

RippleProof intentionally keeps humans in control.

Proposed repairs are not treated as automatically trusted changes.

A reviewer can inspect:

- Detected impact
- Supporting evidence
- Proposed modification
- Patch rationale

before approving the repair.

---

### ✅ Deterministic Verification

After approval, RippleProof verifies the repaired implementation against policy boundaries.

This creates a separation between:

```text
AI Reasoning
     ↓
Human Decision
     ↓
Deterministic Proof
```

---

### 🧾 Persistent Evidence & Event History

RippleProof preserves the lifecycle of each analysis run.

Stored evidence can include:

- Policy contract
- Uploaded artifacts
- Impact findings
- Evidence
- Repair proposals
- Approval state
- Verification tests
- Verification results
- Semantic analysis metadata
- Run timestamps
- Event history

---

### 📊 Evaluation & Benchmarking

RippleProof includes evaluation capabilities to measure system behavior independently of an LLM simply claiming that an answer is correct.

This supports a more evidence-oriented approach to AI-assisted software systems.

---

### 👥 Identity & Team Support

The platform includes authenticated user and team functionality to support controlled access to policy analysis workflows.

---

## 🎬 Demo Scenario

The current RippleProof demo uses a **Customer Refund Policy**.

### Policy Change

```text
OLD RULE: Refunds are allowed within 30 days.

NEW RULE: Refunds are allowed within 14 days.
```

### Existing Artifact

```python
def is_refund_eligible(purchase_age_days):
    return purchase_age_days <= 30
```

### RippleProof Detection

RippleProof identifies that the artifact is still enforcing the previous policy.

The implementation is marked as stale because:

```text
Implemented threshold: 30 days
Required threshold:    14 days
```

### Proposed Repair

```diff
 def is_refund_eligible(purchase_age_days):
-    return purchase_age_days <= 30
+    return purchase_age_days <= 14
```

### Verification

After human approval, RippleProof tests important policy boundaries.

| Purchase Age | Expected Result |
|:---:|:---:|
| 0 days | ✅ Eligible |
| 13 days | ✅ Eligible |
| 14 days | ✅ Eligible |
| 15 days | ❌ Not Eligible |
| 30 days | ❌ Not Eligible |
| 31 days | ❌ Not Eligible |

All verification results are preserved as part of the run evidence.

---

# 🏗️ System Architecture

RippleProof separates the user interface, policy intelligence services, verification logic, and persistence layer.

```mermaid
flowchart TB

    USER["👤 User / Human Reviewer"]

    subgraph FRONTEND["Frontend — Next.js / Vercel"]
        UI["RippleProof Web Interface"]
        AUTH["Authentication"]
        RUNS["Policy Analysis & Runs"]
        DASH["Dashboard & Evaluation"]
    end

    subgraph BACKEND["Backend — FastAPI / Railway"]
        API["REST API"]
        POLICY["Policy Engine"]
        SEMANTIC["LLM Semantic Analysis"]
        IMPACT["Impact Detection"]
        REPAIR["Repair / Patch Engine"]
        VERIFY["Deterministic Verification"]
        EVALUATION["Evaluation Engine"]
        AUDIT["Persistence & Event Tracking"]
    end

    subgraph DATA["Data Layer"]
        DB[("PostgreSQL")]
        ARTIFACTS["Organizational Artifacts"]
    end

    USER --> UI

    UI --> AUTH
    UI --> RUNS
    UI --> DASH

    AUTH --> API
    RUNS --> API
    DASH --> API

    API --> POLICY

    POLICY --> SEMANTIC
    SEMANTIC --> IMPACT

    ARTIFACTS --> IMPACT

    IMPACT --> REPAIR

    REPAIR -->|"Human Approval"| VERIFY

    VERIFY --> EVALUATION

    API --> AUDIT
    IMPACT --> AUDIT
    REPAIR --> AUDIT
    VERIFY --> AUDIT
    EVALUATION --> AUDIT

    AUDIT --> DB
```

---

## 🔄 End-to-End Workflow

### Step 1 — Define the Policy Change

The user provides:

```text
Policy Name
Previous Policy
Updated Policy
```

---

### Step 2 — Upload Organizational Artifacts

The user uploads the artifact or implementation potentially affected by the policy change.

---

### Step 3 — Generate the Policy Contract

RippleProof converts the natural-language change into structured semantics.

Conceptually:

```json
{
  "policy_name": "Customer Refund Policy",
  "field": "refund_period",
  "operator": "<=",
  "old_value": 30,
  "new_value": 14,
  "unit": "days",
  "change_type": "reduction"
}
```

---

### Step 4 — Analyze Impact

The semantic analysis layer compares the updated policy with the uploaded artifact.

It identifies implementations that may still enforce the old rule.

---

### Step 5 — Generate Evidence

RippleProof records the relevant artifact evidence and explains why the implementation conflicts with the updated policy.

---

### Step 6 — Propose a Repair

A targeted patch is generated to align the affected artifact with the new policy.

---

### Step 7 — Human Review

The reviewer examines the impact, evidence, rationale, and proposed patch.

The repair proceeds only after approval.

---

### Step 8 — Deterministic Verification

RippleProof verifies the implementation against policy boundary values.

For the refund example:

```text
14 → True
15 → False
```

This proves that the implementation now respects the new threshold.

---

### Step 9 — Preserve Evidence

The complete lifecycle is stored:

```text
Policy
  ↓
Contract
  ↓
Impact
  ↓
Evidence
  ↓
Patch
  ↓
Approval
  ↓
Verification
  ↓
Event History
```

---

## 🧠 AI + Deterministic Verification

One of RippleProof's central design principles is:

> **AI can reason about meaning, but correctness should be independently verifiable whenever possible.**

LLMs are useful for interpreting semantic relationships between natural-language policies and organizational artifacts.

However, RippleProof does not treat an LLM response alone as proof that an implementation is correct.

Instead, the system combines:

```text
        LLM
         │
         ▼
Semantic Understanding
         │
         ▼
Impact + Evidence
         │
         ▼
Repair Proposal
         │
         ▼
   Human Review
         │
         ▼
Deterministic Verification
         │
         ▼
  Persistent Evidence
```

This approach separates **semantic reasoning** from **verification**.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| 🎨 Frontend | Next.js |
| ⚙️ Backend API | FastAPI |
| 🐍 Backend Language | Python |
| 💻 Frontend Language | TypeScript |
| 🗄️ Database | PostgreSQL |
| 🔗 ORM | SQLAlchemy |
| 🧠 Intelligence Layer | LLM-powered semantic analysis |
| 📋 Data Validation | Pydantic |
| 🔐 Authentication | JWT-based authentication |
| ✅ Verification | Deterministic boundary testing |
| 🌐 Frontend Hosting | Vercel |
| 🚂 Backend Hosting | Railway |
| 🚀 API Server | Uvicorn |

---

## 📂 Project Structure

```text
RippleProof/
│
├── backend/
│   │
│   ├── app/
│   │   ├── core/
│   │   │
│   │   ├── identity/
│   │   │   ├── models.py
│   │   │   └── router.py
│   │   │
│   │   ├── schemas/
│   │   │
│   │   ├── services/
│   │   │   ├── custom_run_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── demo_service.py
│   │   │   ├── evaluation_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── persistence_service.py
│   │   │   ├── policy_engine.py
│   │   │   └── upload_service.py
│   │   │
│   │   ├── db.py
│   │   ├── middleware.py
│   │   └── main.py
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   │
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   └── package.json
│
└── README.md
```

---

# 🚀 Live Application

RippleProof is deployed as a full-stack web application.

<div align="center">

### 🌐 Try RippleProof

[![Launch RippleProof](https://img.shields.io/badge/Launch_RippleProof-Live_Application-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://ripple-proof.vercel.app/)

**Frontend:** Vercel  
**Backend:** Railway  
**Database:** PostgreSQL

</div>

---

# 🎥 Product Demo

Watch the complete RippleProof workflow — from a natural-language policy change to verified implementation evidence.

<div align="center">

## ▶️ Watch RippleProof in Action

[![RippleProof - AI-Powered Policy Change Intelligence](https://img.youtube.com/vi/PuTn0-4_17Y/maxresdefault.jpg)](https://youtu.be/PuTn0-4_17Y)

### [▶ Watch the Full Demo on YouTube](https://youtu.be/PuTn0-4_17Y)

</div>

### 🎬 The Demo Covers

- 🔐 User registration and authentication
- 📝 Policy change submission
- 📂 Organizational artifact upload
- 🧠 LLM-powered semantic analysis
- 🔎 Impact detection
- 📋 Evidence-backed reasoning
- 🛠️ Repair proposal generation
- 👤 Human review and approval
- ✅ Deterministic verification
- 🧾 Persistent run evidence
- 📊 Evaluation and benchmarking

> **Demo Case:** A Customer Refund Policy changes from **30 days to 14 days**, while an existing code artifact still enforces the previous 30-day rule.

---

## ⚙️ Local Development

### Prerequisites

Make sure the following are installed:

- Python 3.13+
- Node.js
- PostgreSQL
- Git

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/alishasajjad/RippleProof.git
cd RippleProof
```

---

### 2️⃣ Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

#### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
source .venv/bin/activate
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Configure Backend Environment

Configure the required environment variables locally.

Example database configuration:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
```

Configure the required LLM provider credentials and application secrets according to your environment.

> ⚠️ Never commit real credentials or production secrets to GitHub.

---

### 4️⃣ Start the Backend

```bash
uvicorn app.main:app --reload
```

The local backend will normally be available at:

```text
http://127.0.0.1:8000
```

---

### 5️⃣ Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
```

Configure the frontend environment to communicate with the backend.

For local development, use the local FastAPI backend where appropriate:

```text
http://127.0.0.1:8000
```

Start the frontend:

```bash
npm run dev
```

Then open:

```text
http://localhost:3000
```

---

## 🔐 Environment & Security

RippleProof uses environment-based configuration for sensitive deployment values.

Secrets should **never** be committed directly to the repository.

Examples include:

```text
DATABASE_URL
LLM API credentials
JWT / authentication secrets
Backend service URLs
Production configuration
```

Production credentials should be managed using the environment-variable and secret-management capabilities of the deployment platform.

The application architecture also keeps repair actions under explicit human review before deterministic verification.

---

## 🧪 Verification Philosophy

RippleProof separates the policy-change lifecycle into distinct responsibilities.

| Stage | Responsibility |
|---|---|
| 🧠 **Analysis** | Understand what the policy change means |
| 🔎 **Impact Detection** | Determine what may be affected |
| 📋 **Evidence** | Explain why an artifact conflicts with the new rule |
| 🛠️ **Repair** | Propose the required implementation change |
| 👤 **Human Review** | Decide whether the repair should be approved |
| ✅ **Verification** | Test whether the approved implementation behaves correctly |
| 🧾 **Evidence Storage** | Preserve the lifecycle for traceability |

This design reduces dependence on opaque AI decisions and creates a more auditable policy-change workflow.

---

## 📊 Evidence Model

A completed RippleProof run can preserve multiple forms of evidence:

```text
┌───────────────────────────────┐
│        Policy Contract        │
├───────────────────────────────┤
│        Artifact Evidence      │
├───────────────────────────────┤
│        Impact Findings        │
├───────────────────────────────┤
│        Proposed Repair        │
├───────────────────────────────┤
│        Human Approval         │
├───────────────────────────────┤
│     Verification Results      │
├───────────────────────────────┤
│         Event History         │
└───────────────────────────────┘
```

This allows the final result to represent more than an AI-generated recommendation.

It becomes a traceable record of **what changed, what was affected, what was repaired, who approved it, and how the result was verified**.

---

## 📈 Future Scope

RippleProof can be extended into a broader enterprise policy intelligence platform.

Potential future capabilities include:

- 🔗 Multi-artifact dependency graphs
- 📦 Repository-level policy impact analysis
- 🔀 Automated pull-request generation
- ⚙️ CI/CD policy verification
- 📜 Policy version comparison
- 👥 Advanced enterprise approval workflows
- 🔐 Role-based access control
- 🧪 Policy-to-test generation
- 📄 Compliance evidence exports
- 🔔 Policy drift monitoring and notifications
- 🔌 Enterprise system integrations
- 🗺️ Policy lineage visualization
- 📊 Advanced risk and compliance dashboards
- 🤖 Multi-agent policy analysis workflows

---

## 🎯 Why RippleProof?

Most policy systems can answer:

> **“What changed?”**

RippleProof is designed to go further:

> **“What did this change affect?”**

Then:

> **“What needs to be repaired?”**

And ultimately:

> **“Can we prove that the policy change was actually implemented?”**

That distinction moves policy management from documentation toward **traceable implementation evidence**.

---

# 🔗 Project Links

<div align="center">

| Resource | Access |
|:---|:---|
| 🌐 **Live Application** | [Launch RippleProof](https://ripple-proof.vercel.app/) |
| 🎥 **Product Demo** | [Watch on YouTube](https://youtu.be/PuTn0-4_17Y) |
| 💻 **Source Code** | [GitHub Repository](https://github.com/alishasajjad/RippleProof) |

</div>

---

# 💻 Developer

<div align="center">

## Alisha Sajjad

**AI Engineer • Python Developer • Full-Stack Developer • Agentic AI Enthusiast**

Building intelligent systems at the intersection of  
**Artificial Intelligence, Software Engineering, Human Oversight, and Production-Ready AI.**

<br/>

[![GitHub](https://img.shields.io/badge/GitHub-alishasajjad-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/alishasajjad)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Alisha_Sajjad-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/devalishasajjad)

</div>

---

## 📄 License

No open-source license has currently been specified for this repository.

Unless a license is added, the source code remains subject to the repository owner's applicable copyright rights.

---

<div align="center">

# 🌊 RippleProof

### From Policy Change to Executable Proof.

**Understand the change. Trace the impact. Approve the repair. Verify the outcome.**

<br/>

[![Live Demo](https://img.shields.io/badge/Launch-Live_Demo-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://ripple-proof.vercel.app/)
[![YouTube](https://img.shields.io/badge/Watch-Product_Demo-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/PuTn0-4_17Y)

<br/>

⭐ **If you find RippleProof useful, consider starring the repository.**

<sub>Designed and developed by Alisha Sajjad.</sub>

</div>