import React from 'react';
import type { DiagnosticReport, StatusEnum } from '../types';
import { Download, FileText, CheckCircle2, AlertTriangle, XCircle, RefreshCw } from 'lucide-react';

interface ReportViewerProps {
  report: DiagnosticReport | null;
  historicalReports: Array<{ filename: string; size_kb: number; created_at: string }>;
  onRefreshReports?: () => void;
}

export const ReportViewer: React.FC<ReportViewerProps> = ({
  report,
  historicalReports,
  onRefreshReports
}) => {
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

  if (!report && historicalReports.length === 0) {
    return (
      <div className="glass-panel" style={{ padding: '3.5rem 2rem', textAlign: 'center' }}>
        <FileText size={40} color="var(--text-dim)" style={{ marginBottom: '1rem' }} />
        <h3 style={{ fontSize: '1.2rem', color: 'var(--text-main)', marginBottom: '0.5rem' }}>No Diagnostic Reports Generated Yet</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', maxWidth: '500px', margin: '0 auto' }}>
          Select a workload and launch a Quick or Full Diagnostic run to generate an official commercial PDF inspection report.
        </p>
      </div>
    );
  }

  // Derive latest PDF filename if report is present
  const latestPdfFilename = historicalReports[0]?.filename;

  return (
    <div>
      {/* Active or Selected Report */}
      {report && (
        <div className="glass-panel" style={{ padding: '1.75rem', marginBottom: '1.5rem' }}>
          {/* Header */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, padding: '0.18rem 0.5rem', borderRadius: '5px', background: 'var(--primary-light)', color: 'var(--primary)', border: '1px solid var(--border-focus)' }}>
                  {report.report_id}
                </span>
                {report.is_simulation && (
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, padding: '0.18rem 0.5rem', borderRadius: '5px', background: 'var(--status-caution-bg)', color: 'var(--status-caution)', border: '1px solid var(--status-caution-border)' }}>
                    SIMULATION REPORT
                  </span>
                )}
              </div>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-main)' }}>
                Executive Diagnostic Assessment
              </h2>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                Target: {report.hardware.manufacturer} {report.hardware.device_model} • {report.test_level} ({report.created_at})
              </p>
            </div>

            {latestPdfFilename && (
              <a
                href={`/api/reports/download/${latestPdfFilename}`}
                download
                className="btn-primary"
                style={{ textDecoration: 'none' }}
              >
                <Download size={16} /> Download Official PDF Report
              </a>
            )}
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

          {/* Anomalies List */}
          <div style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
              Observed Findings & Recommendations
            </h3>
            {report.anomalies.length === 0 ? (
              <div style={{ background: 'var(--status-pass-bg)', border: '1px solid var(--status-pass-border)', borderRadius: '10px', padding: '0.85rem 1rem', color: 'var(--status-pass)', fontSize: '0.85rem' }}>
                <b>[SYSTEM OK]</b> No hardware anomalies or severe thermal degradation flags detected during test sequence.
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

          {/* Benchmark Results Table */}
          <div>
            <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
              Benchmark Performance Metrics
            </h3>
            <div style={{ overflowX: 'auto', border: '1px solid var(--border-card)', borderRadius: '10px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ background: 'var(--bg-card-sub)', color: 'var(--text-secondary)', textAlign: 'left', borderBottom: '1px solid var(--border-card)' }}>
                    <th style={{ padding: '0.65rem 0.85rem' }}>Benchmark Suite</th>
                    <th style={{ padding: '0.65rem 0.85rem' }}>Throughput / Score</th>
                    <th style={{ padding: '0.65rem 0.85rem' }}>Degradation</th>
                    <th style={{ padding: '0.65rem 0.85rem' }}>Status</th>
                    <th style={{ padding: '0.65rem 0.85rem' }}>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {report.benchmarks.map((b) => (
                    <tr key={b.benchmark_id} style={{ borderBottom: '1px solid var(--border-card)' }}>
                      <td style={{ padding: '0.65rem 0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>{b.display_name}</td>
                      <td style={{ padding: '0.65rem 0.85rem', fontFamily: 'var(--font-mono)', color: 'var(--accent)', fontWeight: 600 }}>
                        {b.score} pts
                      </td>
                      <td style={{ padding: '0.65rem 0.85rem', color: b.degradation_pct && b.degradation_pct > 20 ? 'var(--status-fail)' : 'var(--text-muted)' }}>
                        {b.degradation_pct !== undefined ? `${b.degradation_pct}%` : '—'}
                      </td>
                      <td style={{ padding: '0.65rem 0.85rem' }}>{getStatusBadge(b.status)}</td>
                      <td style={{ padding: '0.65rem 0.85rem', color: 'var(--text-muted)', fontSize: '0.78rem' }}>{b.details}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Historical Generated Reports List */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem', flexWrap: 'wrap', gap: '0.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)' }}>
            Historical PDF Inspection Reports
          </h3>
          {onRefreshReports && (
            <button
              onClick={onRefreshReports}
              className="btn-secondary"
              style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
            >
              <RefreshCw size={13} /> Refresh List
            </button>
          )}
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
          {historicalReports.map((hr) => (
            <div
              key={hr.filename}
              className="spec-subcard"
              style={{
                padding: '0.75rem 1rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '0.5rem'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <FileText size={18} color="var(--primary)" />
                <div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-main)' }}>
                    {hr.filename}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                    Generated: {hr.created_at} • Size: {hr.size_kb} KB
                  </div>
                </div>
              </div>

              <a
                href={`/api/reports/download/${hr.filename}`}
                download
                className="btn-secondary"
                style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem', textDecoration: 'none' }}
              >
                <Download size={14} /> Download PDF
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
