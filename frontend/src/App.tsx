import React, { useState } from 'react';
import { simplifyReport, type SimplificationResponse } from './services/api';
import './index.css';

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<SimplificationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await simplifyReport(file);
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Error processing report');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <header style={{ textAlign: 'center', marginBottom: '4rem' }} className="animate-fade-in">
        <h1 style={{ fontSize: '3.5rem', marginBottom: '1rem', background: 'linear-gradient(to right, #818cf8, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          MediBrief AI
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.25rem' }}>
          Simplifying complex medical reports into patient-friendly insights.
        </p>
      </header>

      {!result && (
        <main className="glass-card animate-fade-in" style={{ textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
          <h2 style={{ marginBottom: '1.5rem' }}>Upload Medical Report</h2>
          <div style={{ border: '2px dashed var(--border-glass)', padding: '3rem', borderRadius: '12px', marginBottom: '2rem', cursor: 'pointer' }} onClick={() => document.getElementById('file-upload')?.click()}>
            <p style={{ color: 'var(--text-secondary)' }}>{file ? file.name : "Drag & drop PDF here or click to browse"}</p>
            <input id="file-upload" type="file" accept="application/pdf" style={{ display: 'none' }} onChange={handleFileChange} />
          </div>
          {error && <p style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</p>}
          <button className="btn-primary" style={{ width: '100%' }} onClick={handleUpload} disabled={isLoading || !file}>
            {isLoading ? <span className="loader" style={{ width: '24px', height: '24px' }}></span> : "Simplify Report"}
          </button>
        </main>
      )}

      {result && (
        <section className="animate-fade-in">
          <div className="glass-card" style={{ marginBottom: '2rem' }}>
            <h2 style={{ color: '#6366f1', marginBottom: '1rem' }}>Patient-Friendly Summary</h2>
            <p style={{ fontSize: '1.1rem' }}>{result.summary}</p>
          </div>

          <div className="grid">
            <div className="glass-card">
              <h3 style={{ marginBottom: '1.5rem' }}>⚠️ Risk Flags</h3>
              {result.risk_flags.map((risk, i) => (
                <div key={i} style={{ borderBottom: '1px solid var(--border-glass)', padding: '0.75rem 0', display: 'flex', justifyContent: 'space-between' }}>
                  <div>
                    <p style={{ fontWeight: 600 }}>{risk.indicator}</p>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Value: {risk.value}</p>
                  </div>
                  <span style={{
                    padding: '0.25rem 0.75rem',
                    borderRadius: '999px',
                    fontSize: '0.8rem',
                    height: 'max-content',
                    background: risk.status === 'High' || risk.status === 'Critical' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)',
                    color: risk.status === 'High' || risk.status === 'Critical' ? '#f87171' : '#4ade80'
                  }}>
                    {risk.status}
                  </span>
                </div>
              ))}
            </div>

            <div className="glass-card">
              <h3 style={{ marginBottom: '1.5rem' }}>📅 Medication Timeline</h3>
              {result.medication_timeline.map((med, i) => (
                <div key={i} style={{ borderBottom: '1px solid var(--border-glass)', padding: '0.75rem 0' }}>
                  <p style={{ fontWeight: 600 }}>{med.name} - {med.dosage}</p>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Schedule: {med.schedule}</p>
                </div>
              ))}
            </div>
          </div>

          <footer className="glass-card" style={{ marginTop: '2rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>👨‍⚕️ Doctor-Ready Clinical Report</h3>
            <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '8px', fontSize: '0.9rem' }}>
              {result.doctor_report}
            </pre>
          </footer>

          <div style={{ textAlign: 'center', marginTop: '2rem' }}>
            <button className="btn-primary" onClick={() => { setResult(null); setFile(null); }}>Upload Another Report</button>
          </div>
        </section>
      )}
    </div>
  );
};

export default App;
