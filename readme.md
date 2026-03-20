# MediBrief AI V2 - Enterprise Medical Report Simplifier

MediBrief AI V2 transforms complex medical PDFs into accessible, patient-friendly insights with source-text evidence mapping, confidence scoring, and strict JSON validation via Google Vertex AI.

## 🚀 Enterprise V2 Upgrades

- **Modular Clean Architecture**: Segregated into `api`, `core`, `models`, `repositories`, and `services`.
- **Strict Data Validation**: Pydantic v2 schemas enforce structure (Evidence & Confidence modeling).
- **Asynchronous Parallelism**: LLM Insights (Summary, Risks, Timeline, Physician Report) are processed concurrently via `asyncio`.
- **Google Cloud Native Integration**:
  - **Secret Manager** for dynamic API/App configurations.
  - **Cloud Logging** with formatted JSON and PII masking.
  - **Cloud Storage** bucket provisioning natively handles PDF signing/storage.
- **Enterprise-Grade Security**: Strict file checking (MIME signature checking via `libmagic`), Cloud Run rate-limiting (`slowapi`), and exception shielding.
- **WCAG Accessibility**: Full strict WCAG keyboard-accessible side-by-side dashboard with scalable responsive metrics.

---

## 🏗️ Architecture Stack

- **Frontend**: React (TypeScript), CSS Modules/Vanilla
- **Backend**: FastAPI (Python 3.12+)
- **Frontend**: React + TypeScript + Vite
- **AI/ML**: Vertex AI (Gemini 1.5 Flash), Google Document AI
- **Infrastructure**: Google Cloud Run, Artifact Registry, GCS
- **Monitoring**: Google Cloud Trace, Error Reporting, Cloud Logging
- **Security**: Secret Manager, IAM Service Accounts
**: Google Cloud Run (Serverless computing containerized)
- **CI/CD Testing**: PyTest, PyTest-Mock

---

## 💻 Local Development

1. **Clone the Repo**
2. **Setup Backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Environment `.env` (Backend):**
   ```env
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```
4. **Start API Server:**
   ```bash
   uvicorn main:app --reload --port 8080
   ```
5. **Start Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 🧪 Testing

Comprehensive unit and mock-driven tests guarantee safety during parallel pipeline runs. By simulating LLM output, CI testing validates strict Pydantic parsing:

```bash
cd backend
source venv/bin/activate
PYTHONPATH=. pytest tests/unit -v --cov=backend
```

*Note: The test suite securely mocks all Google Cloud external calls ensuring offline testing speed and 100% test reproducibility.*

---

## 🌍 Google Cloud Deployment

A robust `scripts/deploy.sh` script automates provisioning:

- Enables required IAM APIs.
- Creates Cloud Storage buckets with a 1-day retention auto-deletion lifecycle.
- Pushes Docker container strictly to Cloud Run mapping environmental secrets.

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

---

## ✨ AI Confidence & Evidence Mapping

MediBrief AI returns exact **Confidence Scores (0.0 to 1.0)** mapping precisely back to its parent source text block. A side-by-side PDF layout tracks hallucinations, protecting critical patient data.