# MediBrief AI (Medical Report Simplifier) 🏥

MediBrief AI is a production-grade AI application designed to simplify complex medical reports into patient-friendly insights. It uses a **Multi-Step Prompting (MCP)** pipeline to extract data, identify risks, and generate helpful summaries for both patients and doctors.

## Core Features
1. **PDF Upload**: Securely upload medical report PDFs for processing.
2. **AI-Powered OCR**: Uses Google Document AI (with Tesseract fallback) for accurate text extraction.
3. **Structured MCP Pipeline**:
   - **Extraction**: Raw text to structured clinical JSON.
   - **Summary**: Simple, patient-friendly explanation.
   - **Risk Detection**: Automatic highlighting of abnormal values (e.g., High Sugar/BP).
   - **Medication Timeline**: Clear schedule and dosage information.
   - **Clinical Report**: Technical summary for healthcare professionals.
4. **Premium UI**: Modern, glassmorphism-based dark mode design.

## Architecture
- **Frontend**: React (Vite, TypeScript, Vanilla CSS).
- **Backend**: FastAPI (Python), Async processing.
- **AI**: Google Vertex AI (Gemini 1.5 Flash), Google Document AI.
- **Deployment**: Google Cloud Run (Dockerized).

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- Google Cloud Project with Billing enabled.
- (Optional) `tesseract-ocr` and `poppler-utils` for local OCR fallback.

### Environmental Variables
Create a `.env` file in the `backend/` directory:
```env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
DOCUMENT_AI_PROCESSOR_ID=your-processor-id (optional)
```

### Local Setup
1. **Create Virtual Environment (Recommended for macOS)**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Install Frontend Dependencies**:
   ```bash
   cd ../frontend
   npm install
   ```
3. **Run Locally**:
   ```bash
   # From the project root (MediMindAI)
   # Run Backend (Make sure venv is activated)
   python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload
   
   # In another terminal: Run Frontend
   cd frontend
   npm run dev
   ```

## Deployment to Google Cloud Run
We provide a deployment script to automate the process:
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## Testing
Run unit tests for the MCP pipeline:
```bash
pytest backend/tests/
```

## License
MIT