const API_BASE = window.location.origin === "http://localhost:5173" || window.location.origin.includes("localhost") ? "http://localhost:8080/api" : "/api";

export interface InsightBase {
  evidence: string;
  confidence_score: number;
}

export interface SummaryInsight extends InsightBase {
  summary: string;
}

export interface RiskFlag extends InsightBase {
  indicator: string;
  value: string;
  status: string;
}

export interface Medication extends InsightBase {
  name: string;
  dosage: string;
  schedule: string;
}

export interface DoctorReport extends InsightBase {
  clinical_impression: string;
  plan: string;
}

export interface SimplificationResponse {
  id: string;
  summary: SummaryInsight;
  risk_flags: RiskFlag[];
  medication_timeline: Medication[];
  doctor_report: DoctorReport;
}

export const simplifyReport = async (file: File): Promise<SimplificationResponse> => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/simplify`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to process report");
  }

  return response.json();
};
