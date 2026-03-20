const API_BASE = window.location.origin === "http://localhost:5173" ? "http://localhost:8080" : "";

export interface SimplificationResponse {
  id: string;
  summary: string;
  risk_flags: {
    indicator: string;
    value: string;
    status: string;
  }[];
  medication_timeline: {
    name: string;
    dosage: string;
    schedule: string;
  }[];
  doctor_report: string;
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
