import React, { useState } from 'react';
import { simplifyReport, type SimplificationResponse, type InsightBase } from './services/api';
import './index.css';

const ConfidenceBadge: React.FC<{ score: number }> = ({ score }) => {
  const color = score > 0.8 ? '#4ade80' : score > 0.6 ? '#fbbf24' : '#f87171';
  return (
    <span 
        style={{ fontSize: '0.75rem', padding: '0.15rem 0.5rem', borderRadius: '12px', background: `${color}33`, color, border: `1px solid ${color}55`, marginLeft: '0.5rem', verticalAlign: 'middle', whiteSpace: 'nowrap' }} 
        aria-label={`AI Confidence Score: ${Math.round(score * 100)}%`}
        title="AI Confidence Score"
    >
      {Math.round(score * 100)}%
    </span>
  );
};

const EvidenceTooltip: React.FC<{ evidence: string }> = ({ evidence }) => {
  const [open, setOpen] = useState(false);
  
  if (!evidence || evidence === "System generated." || evidence === "N/A") return null;

  return (
    <div style={{ position: 'relative', display: 'inline-block', marginLeft: '0.5rem', verticalAlign: 'middle' }}>
      <button 
        type="button"
        onClick={() => setOpen(!open)}
        onBlur={() => setOpen(false)}
        style={{ background: 'var(--border-glass)', border: 'none', borderRadius: '50%', width: '18px', height: '18px', fontSize: '10px', color: 'var(--text-secondary)', cursor: 'pointer', outline: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        aria-expanded={open}
        aria-label="View source text evidence"
      >
        ?
      </button>
      {open && (
        <div 
          style={{ position: 'absolute', top: '25px', left: '50%', transform: 'translateX(-50%)', width: '250px', padding: '12px', background: 'rgba(30, 30, 40, 0.95)', border: '1px solid var(--border-glass)', borderRadius: '8px', zIndex: 100, fontSize: '0.85rem', color: 'var(--text-secondary)', backdropFilter: 'blur(10px)', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)' }} 
          role="tooltip" 
          aria-live="polite"
        >
          <strong style={{ color: 'var(--text-primary)', marginBottom: '0.5rem', display: 'block' }}>Source Evidence:</strong>
          <span style={{ fontStyle: 'italic' }}>"{evidence}"</span>
        </div>
      )}
    </div>
  );
};

const Header: React.FC = () => (
   <header style={{ textAlign: 'center', marginBottom: '2rem' }} className="animate-fade-in" role="banner">
    <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', background: 'linear-gradient(to right, #818cf8, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
      MediBrief AI Enterprise
    </h1>
    <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
      Intelligent, verifiable medical report simplification.
    </p>
  </header>
);

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [fileUrl, setFileUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<SimplificationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setFileUrl(URL.createObjectURL(selected));
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

  const resetState = () => {
    setResult(null);
    setFile(null);
    if (fileUrl) URL.revokeObjectURL(fileUrl);
    setFileUrl(null);
  };

  return (
    <div className="container" style={{ maxWidth: result ? '1400px' : '800px', transition: 'max-width 0.5s ease' }}>
      <Header />

      {!result ? (
        <main className="glass-card animate-fade-in" style={{ textAlign: 'center', margin: '0 auto' }} aria-busy={isLoading}>
          <h2 style={{ marginBottom: '1.5rem' }}>Upload Medical Report</h2>
          <div 
            style={{ border: '2px dashed var(--border-glass)', padding: '3rem', borderRadius: '12px', marginBottom: '2rem', cursor: 'pointer', transition: 'border-color 0.3s' }} 
            onClick={() => document.getElementById('file-upload')?.click()}
            onKeyDown={(e) => e.key === 'Enter' && document.getElementById('file-upload')?.click()}
            role="button"
            tabIndex={0}
            aria-label="File upload area"
          >
            <p style={{ color: 'var(--text-secondary)' }}>{file ? file.name : "Drag & drop PDF here or click to browse"}</p>
            <input id="file-upload" type="file" accept="application/pdf" style={{ display: 'none' }} onChange={handleFileChange} aria-hidden="true" />
          </div>
          {error && <p style={{ color: 'var(--danger)', marginBottom: '1rem' }} role="alert">{error}</p>}
          <button className="btn-primary" style={{ width: '100%' }} onClick={handleUpload} disabled={isLoading || !file} aria-disabled={isLoading || !file}>
            {isLoading ? <span className="loader" style={{ width: '24px', height: '24px' }}></span> : "Simplify Report"}
          </button>
        </main>
      ) : (
        <main className="animate-fade-in" style={{ display: 'grid', gridTemplateColumns: 'minmax(400px, 1fr) minmax(500px, 1fr)', gap: '2rem', alignItems: 'start' }}>
          
          {/* Left Pane: PDF Viewer */}
          <section className="glass-card" style={{ height: '80vh', padding: '1rem', display: 'flex', flexDirection: 'column' }} aria-label="Original Document">
             <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
               <h2 style={{ fontSize: '1.2rem' }}>Original Document</h2>
               <button className="btn-primary" style={{ padding: '0.4rem 1rem', fontSize: '0.9rem' }} onClick={resetState}>Upload New</button>
             </div>
             {fileUrl ? (
                 <object data={fileUrl} type="application/pdf" width="100%" height="100%" style={{ border: 'none', borderRadius: '8px', flexGrow: 1 }} aria-label="PDF Document Viewer">
                    <p>Your browser doesn't support PDF viewing. <a href={fileUrl} target="_blank" rel="noreferrer" style={{color: '#818cf8'}}>Download PDF</a>.</p>
                 </object>
             ) : (
                 <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)' }}>PDF Preview Unavailable</div>
             )}
          </section>

          {/* Right Pane: AI Insights */}
          <section style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxHeight: '80vh', overflowY: 'auto', paddingRight: '0.5rem' }} aria-label="AI Extracted Insights">
            
            {/* Summary */}
            <article className="glass-card">
              <h2 style={{ color: '#818cf8', marginBottom: '1rem', display: 'flex', alignItems: 'center' }}>
                Patient Summary
                <ConfidenceBadge score={result.summary.confidence_score} />
                <EvidenceTooltip evidence={result.summary.evidence} />
              </h2>
              <p style={{ fontSize: '1.1rem', lineHeight: 1.6 }}>{result.summary.summary}</p>
            </article>

            {/* Risk Flags */}
            <article className="glass-card">
              <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center' }}>⚠️ Identified Risk Flags</h3>
              {result.risk_flags.length === 0 ? (
                  <p style={{ color: 'var(--text-secondary)' }}>No risk flags detected.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {result.risk_flags.map((risk, i) => (
                    <div key={i} style={{ borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <p style={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                          {risk.indicator}
                          <ConfidenceBadge score={risk.confidence_score} />
                          <EvidenceTooltip evidence={risk.evidence} />
                        </p>
                        <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Value: {risk.value}</p>
                      </div>
                      <span style={{
                        padding: '0.3rem 0.8rem',
                        borderRadius: '999px',
                        fontSize: '0.85rem',
                        fontWeight: 600,
                        background: risk.status === 'High' || risk.status === 'Critical' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(34, 197, 94, 0.15)',
                        color: risk.status === 'High' || risk.status === 'Critical' ? '#fca5a5' : '#86efac',
                        border: `1px solid ${risk.status === 'High' || risk.status === 'Critical' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(34, 197, 94, 0.3)'}`
                      }}>
                        {risk.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </article>

            {/* Timeline */}
            <article className="glass-card">
              <h3 style={{ marginBottom: '1.5rem' }}>📅 Medication Timeline</h3>
               {result.medication_timeline.length === 0 ? (
                   <p style={{ color: 'var(--text-secondary)' }}>No medications detected.</p>
               ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {result.medication_timeline.map((med, i) => (
                    <div key={i} style={{ borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.75rem' }}>
                      <p style={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                        {med.name}
                        <ConfidenceBadge score={med.confidence_score} />
                        <EvidenceTooltip evidence={med.evidence} />
                      </p>
                      <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Dosage: {med.dosage} | Schedule: {med.schedule}</p>
                    </div>
                  ))}
                </div>
               )}
            </article>

            {/* Doctor Report */}
            <article className="glass-card">
              <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center' }}>
                👨‍⚕️ Clinical Impression
                <ConfidenceBadge score={result.doctor_report.confidence_score} />
                <EvidenceTooltip evidence={result.doctor_report.evidence} />
              </h3>
              <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
                <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>Impression:</p>
                <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', marginBottom: '1rem', whiteSpace: 'pre-wrap' }}>{result.doctor_report.clinical_impression}</p>
                <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>Plan:</p>
                <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', whiteSpace: 'pre-wrap' }}>{result.doctor_report.plan}</p>
              </div>
            </article>

          </section>
        </main>
      )}
    </div>
  );
};

export default App;
