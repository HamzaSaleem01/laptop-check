import React, { useState, useRef } from 'react';
import type { DiagnosticReport, StatusEnum, SystemHardwareSnapshot } from '../types';
import { 
  Download, CheckCircle2, AlertTriangle, XCircle, 
  Upload, Sparkles, Trash2, ArrowLeft 
} from 'lucide-react';
import { createMockReport } from '../mockData';

interface ReportViewerProps {
  report: DiagnosticReport | null;
  historicalReports: Array<{ filename: string; size_kb: number; created_at: string }>;
  onRefreshReports?: () => void;
  onLoadSnapshot?: (snapshot: SystemHardwareSnapshot) => void;
  onClearReport?: () => void;
  onGoToDownloads?: () => void;
}

export const ReportViewer: React.FC<ReportViewerProps> = ({
  report,
  historicalReports,
  onLoadSnapshot,
  onClearReport,
  onGoToDownloads
}) => {
  const [dragOver, setDragOver] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const getStatusBadge = (st: StatusEnum) => {
    switch (st) {
      case 'PASS':
        return <span className="badge-pass"><CheckCircle2 size={13} /> PASS</span>;
      case 'CAUTION':
        return <span className="badge-caution"><AlertTriangle size={13} /> CAUTION</span>;
      case 'FAIL':
        return <span className="badge-fail"><XCircle size={13} /> FAIL</span>;
      default:
        return <span className="badge-neutral">{st}</span>;
    }
  };

  const handleFile = (file: File) => {
    setUploadError(null);
    if (!file.name.endsWith('.json')) {
      setUploadError('Please select a valid .json report file (such as laptop_specs.json).');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target?.result as string;
        const parsed = JSON.parse(text);
        if (parsed.hardware && parsed.report_id) {
          // It's a full diagnostic report
          if (onLoadSnapshot) {
            onLoadSnapshot(parsed.hardware);
          }
        } else if (parsed.cpu || parsed.device_model || parsed.os) {
          // It's a SystemHardwareSnapshot
          if (onLoadSnapshot) {
            onLoadSnapshot(parsed);
          }
        } else {
          setUploadError('Unrecognized JSON format. File must contain laptop hardware or diagnostic report keys.');
        }
      } catch (err) {
        setUploadError('Invalid JSON file format. Could not parse.');
      }
    };
    reader.readAsText(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleLoadDemo = () => {
    if (onLoadSnapshot) {
      const demo = createMockReport('mid_range', 'Quick / Shop Safe');
      onLoadSnapshot(demo.hardware);
    }
  };

  // If no report is loaded, show the Upload / Drag-and-Drop Inspector
  if (!report) {
    return (
      <div style={{ maxWidth: '1000px', margin: '0 auto', paddingBottom: '3rem' }}>
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
            Diagnostic Report & Hardware Inspector
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', maxWidth: '650px', margin: '0 auto' }}>
            LaptopCheck does not display fake or hardcoded machine specifications. 
            Upload your generated <code style={{ color: 'var(--primary)' }}>laptop_specs.json</code> from your laptop to inspect genuine hardware metrics.
          </p>
        </div>

        {/* Upload Dropzone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          style={{
            background: dragOver ? 'var(--primary-light)' : 'var(--bg-card)',
            border: `2px dashed ${dragOver ? 'var(--primary)' : 'var(--border-card)'}`,
            borderRadius: '16px',
            padding: '3rem 2rem',
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            boxShadow: 'var(--card-shadow)',
            marginBottom: '2rem'
          }}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => {
              if (e.target.files && e.target.files.length > 0) {
                handleFile(e.target.files[0]);
              }
            }}
            accept=".json"
            style={{ display: 'none' }}
          />

          <div style={{
            width: '60px',
            height: '60px',
            borderRadius: '50%',
            background: 'var(--primary-light)',
            color: 'var(--primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1.25rem auto'
          }}>
            <Upload size={28} />
          </div>

          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
            Drop <span style={{ color: 'var(--accent)' }}>laptop_specs.json</span> here, or Browse
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', maxWidth: '480px', margin: '0 auto 1.5rem auto' }}>
            Supports JSON snapshots exported by LaptopCheck on Windows, macOS, or Linux.
          </p>

          <div style={{ display: 'inline-flex', gap: '0.75rem', flexWrap: 'wrap', justifyContent: 'center' }}>
            <span style={{
              background: 'var(--primary)',
              color: '#ffffff',
              padding: '0.55rem 1.25rem',
              borderRadius: '8px',
              fontSize: '0.85rem',
              fontWeight: 600
            }}>
              Choose File
            </span>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                handleLoadDemo();
              }}
              style={{
                background: 'transparent',
                color: 'var(--text-secondary)',
                border: '1px solid var(--border-card)',
                padding: '0.55rem 1.25rem',
                borderRadius: '8px',
                fontSize: '0.85rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem'
              }}
            >
              <Sparkles size={14} color="var(--primary)" />
              <span>Preview Demo Report</span>
            </button>
          </div>

          {uploadError && (
            <div style={{
              marginTop: '1.25rem',
              color: 'var(--status-fail)',
              background: 'var(--status-fail-bg)',
              border: '1px solid var(--status-fail-border)',
              borderRadius: '8px',
              padding: '0.65rem 1rem',
              fontSize: '0.85rem',
              display: 'inline-block'
            }}>
              {uploadError}
            </div>
          )}
        </div>

        {/* How to generate the file section */}
        <div className="glass-panel" style={{ padding: '1.75rem', borderRadius: '16px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.75rem' }}>
            Don't have a <code style={{ color: 'var(--primary)' }}>laptop_specs.json</code> file yet?
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem', lineHeight: 1.5 }}>
            Run the 100% read-only collector on your target laptop. It creates <code style={{ color: 'var(--primary)' }}>laptop_specs.json</code> locally in seconds without modifying any system files:
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', marginBottom: '1.25rem' }}>
            
            <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontWeight: 700, fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                🪟 WINDOWS (PowerShell)
              </div>
              <code style={{ fontSize: '0.78rem', color: 'var(--accent)', wordBreak: 'break-all' }}>
                powershell -c "irm https://laptopcheck.vercel.app/scan.ps1 | iex"
              </code>
            </div>

            <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontWeight: 700, fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                🍎 macOS & 🐧 LINUX (Terminal)
              </div>
              <code style={{ fontSize: '0.78rem', color: 'var(--accent)', wordBreak: 'break-all' }}>
                curl -fsSL https://laptopcheck.vercel.app/scan.sh | bash
              </code>
            </div>

          </div>

          {onGoToDownloads && (
            <button
              onClick={onGoToDownloads}
              className="btn-primary"
              style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}
            >
              <Download size={15} />
              <span>Go to Downloads Center</span>
            </button>
          )}
        </div>

      </div>
    );
  }

  // Active or Selected Report View
  const latestPdfFilename = historicalReports[0]?.filename;

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', paddingBottom: '3rem' }}>
      
      {/* Top Banner Actions */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <button
          onClick={onClearReport}
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-card)',
            color: 'var(--text-secondary)',
            padding: '0.45rem 0.85rem',
            borderRadius: '8px',
            fontSize: '0.82rem',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem'
          }}
        >
          <ArrowLeft size={14} />
          <span>Inspect Another Report / Back</span>
        </button>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {onClearReport && (
            <button
              onClick={onClearReport}
              style={{
                background: 'var(--status-fail-bg)',
                color: 'var(--status-fail)',
                border: '1px solid var(--status-fail-border)',
                padding: '0.45rem 0.85rem',
                borderRadius: '8px',
                fontSize: '0.82rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem'
              }}
            >
              <Trash2 size={13} />
              <span>Clear Report</span>
            </button>
          )}

          {latestPdfFilename && (
            <a
              href={`/api/reports/download/${latestPdfFilename}`}
              download
              className="btn-primary"
              style={{ textDecoration: 'none', padding: '0.45rem 0.85rem', fontSize: '0.82rem' }}
            >
              <Download size={14} /> Download PDF
            </a>
          )}
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '1.75rem', marginBottom: '1.5rem', borderRadius: '16px' }}>
        
        {/* Report Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, padding: '0.18rem 0.5rem', borderRadius: '5px', background: 'var(--primary-light)', color: 'var(--primary)', border: '1px solid var(--border-focus)' }}>
                {report.report_id}
              </span>
              {report.is_simulation && (
                <span style={{ fontSize: '0.75rem', fontWeight: 700, padding: '0.18rem 0.5rem', borderRadius: '5px', background: 'var(--status-caution-bg)', color: 'var(--status-caution)', border: '1px solid var(--status-caution-border)' }}>
                  DEMO / SIMULATION
                </span>
              )}
              <span style={{ fontSize: '0.75rem', color: 'var(--status-pass)', fontWeight: 600 }}>
                100% NON-DESTRUCTIVE SAFE VERIFICATION
              </span>
            </div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-main)' }}>
              Executive Diagnostic Assessment
            </h2>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Machine: {report.hardware.manufacturer} {report.hardware.device_model} • OS: {report.hardware.os.system} {report.hardware.os.release} • Created: {report.created_at}
            </p>
          </div>
        </div>

        {/* Component Assessment Grid */}
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
            System Component Health Matrix
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.75rem' }}>
            {Object.entries(report.summary_categories).map(([comp, st]) => (
              <div key={comp} className="spec-subcard" style={{ padding: '0.85rem', textAlign: 'center' }}>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '0.35rem', fontWeight: 600 }}>
                  {comp}
                </div>
                <div>{getStatusBadge(st)}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Workload Suitability Results */}
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
            Workload Suitability Verdicts
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
            {report.workload_evaluations.map(w => (
              <div key={w.profile_id} className="spec-subcard" style={{ padding: '1.15rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <h4 style={{ fontSize: '1.02rem', fontWeight: 700, color: 'var(--text-main)' }}>{w.profile_name}</h4>
                  {getStatusBadge(w.overall_status)}
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '0.75rem', lineHeight: '1.4' }}>
                  {w.suitability_summary}
                </p>
                <div style={{ borderTop: '1px solid var(--border-card)', paddingTop: '0.6rem' }}>
                  {w.criteria.map(c => (
                    <div key={c.key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem', padding: '0.22rem 0' }}>
                      <span style={{ color: 'var(--text-dim)' }}>{c.label}:</span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{c.actual_value} {c.unit}</span>
                        {getStatusBadge(c.status)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Observed Findings / Anomalies */}
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
            Observed Findings & Recommendations
          </h3>
          {report.anomalies.length === 0 ? (
            <div style={{ background: 'var(--status-pass-bg)', border: '1px solid var(--status-pass-border)', borderRadius: '10px', padding: '0.85rem 1rem', color: 'var(--status-pass)', fontSize: '0.85rem' }}>
              <b>[SYSTEM OK]</b> No hardware anomalies or severe degradation flags detected during inspection.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {report.anomalies.map((anom, idx) => (
                <div
                  key={idx}
                  style={{
                    background: anom.severity === 'CRITICAL' ? 'var(--status-fail-bg)' : 'var(--status-caution-bg)',
                    border: `1px solid ${anom.severity === 'CRITICAL' ? 'var(--status-fail-border)' : 'var(--status-caution-border)'}`,
                    borderRadius: '10px',
                    padding: '0.85rem 1rem'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                    <span style={{
                      fontSize: '0.7rem',
                      fontWeight: 700,
                      padding: '0.15rem 0.45rem',
                      borderRadius: '4px',
                      background: anom.severity === 'CRITICAL' ? 'var(--status-fail)' : 'var(--status-caution)',
                      color: '#ffffff'
                    }}>
                      {anom.severity} • {anom.component}
                    </span>
                    <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)' }}>
                      {anom.title}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                    {anom.description}
                  </p>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                    <b>Recommendation:</b> {anom.recommendation}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

    </div>
  );
};
