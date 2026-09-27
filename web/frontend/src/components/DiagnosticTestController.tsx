import React from 'react';
import { Play, Square, CheckCircle2, Clock, AlertTriangle, ShieldAlert, Thermometer, Flame, Gauge } from 'lucide-react';
import type { DiagnosticReport } from '../types';

interface TestControllerProps {
  testLevel: string;
  setTestLevel: (lvl: string) => void;
  isRunning: boolean;
  progress: number;
  currentStage: string;
  elapsedSecs: number;
  safetyLevel: string;
  latestSample: any;
  onStartTest: () => void;
  onStopTest: () => void;
  latestReport: DiagnosticReport | null;
  onViewReport: (report: DiagnosticReport) => void;
}

export const DiagnosticTestController: React.FC<TestControllerProps> = ({
  testLevel,
  setTestLevel,
  isRunning,
  progress,
  currentStage,
  elapsedSecs,
  safetyLevel,
  latestSample,
  onStartTest,
  onStopTest,
  latestReport,
  onViewReport
}) => {
  const testLevels = [
    {
      id: 'Quick / Shop Safe',
      title: 'Quick Laptop Inspection',
      subtitle: 'Recommended for shop testing (< 2 min)',
      description: 'Burst CPU, RAM integrity, non-destructive SSD read/write, battery health, thermal baseline.',
      badge: 'RECOMMENDED'
    },
    {
      id: 'Standard',
      title: 'Full Benchmark Suite',
      subtitle: 'Comprehensive diagnostic (5–10 min)',
      description: 'Sustained CPU multi-threading, RAM bandwidth, deep storage benchmarks, throttling curves.',
      badge: 'DETAILED'
    },
    {
      id: 'Extended',
      title: 'Extended Stress & Stability',
      subtitle: 'Thermal degradation stress (20+ min)',
      description: 'Prolonged combined stress to evaluate cooling assembly, thermal paste degradation, and long-term stability.',
      badge: 'STRESS TEST'
    }
  ];

  const getSafetyBadge = (level: string) => {
    switch (level) {
      case 'WARNING':
        return <span className="badge-caution"><AlertTriangle size={13} /> THERMAL WARNING</span>;
      case 'REDUCE LOAD':
        return <span className="badge-caution"><Flame size={13} /> THROTTLING DETECTED</span>;
      case 'STOP':
        return <span className="badge-fail"><ShieldAlert size={13} /> EMERGENCY SHUTDOWN</span>;
      case 'PAUSE':
        return <span className="badge-neutral">PAUSED</span>;
      default:
        return <span className="badge-pass"><CheckCircle2 size={13} /> THERMAL GUARDIAN ACTIVE</span>;
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--accent)', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
            Diagnostic Control Suite
          </span>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '0.1rem' }}>
            Safe System Diagnostics & Guardian
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Certified non-destructive benchmark sequences with active hardware thermal threshold protection.
          </p>
        </div>
        <div>
          {getSafetyBadge(safetyLevel)}
        </div>
      </div>

      {/* Test Level Selector Cards */}
      {!isRunning && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
          {testLevels.map((lvl) => {
            const isSelected = testLevel === lvl.id;
            return (
              <div
                key={lvl.id}
                onClick={() => setTestLevel(lvl.id)}
                style={{
                  background: isSelected ? 'var(--primary-light)' : 'var(--bg-card-sub)',
                  border: `2px solid ${isSelected ? 'var(--primary)' : 'var(--border-card)'}`,
                  borderRadius: '12px',
                  padding: '1.1rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  boxShadow: isSelected ? '0 4px 16px var(--primary-glow)' : 'none'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.45rem' }}>
                  <span style={{
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    padding: '0.15rem 0.45rem',
                    borderRadius: '5px',
                    background: isSelected ? 'var(--primary)' : 'var(--bg-page)',
                    color: isSelected ? '#ffffff' : 'var(--text-muted)',
                    border: `1px solid ${isSelected ? 'transparent' : 'var(--border-card)'}`
                  }}>
                    {lvl.badge}
                  </span>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Clock size={13} /> {lvl.subtitle.split('(')[1]?.replace(')', '') || 'Safe'}
                  </span>
                </div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.25rem' }}>
                  {lvl.title}
                </h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {lvl.description}
                </p>
              </div>
            );
          })}
        </div>
      )}

      {/* Active Run Monitor */}
      {isRunning && (
        <div className="spec-subcard" style={{
          border: '1.5px solid var(--primary)',
          borderRadius: '12px',
          padding: '1.25rem',
          marginBottom: '1.5rem',
          boxShadow: '0 4px 20px var(--primary-glow)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="active-pulse" style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--primary)' }} />
              <span style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-main)' }}>
                Diagnostic in Progress: {testLevel}
              </span>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', fontSize: '0.85rem', flexWrap: 'wrap' }}>
              <span style={{ color: 'var(--text-muted)' }}>
                Elapsed: <b style={{ color: 'var(--text-main)' }}>{elapsedSecs}s</b>
              </span>
              
              {latestSample?.cpu_temp_c && (
                <span style={{
                  color: latestSample.cpu_temp_c >= 88 ? 'var(--status-fail)' : (latestSample.cpu_temp_c >= 78 ? 'var(--status-caution)' : 'var(--status-pass)'),
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem'
                }}>
                  <Thermometer size={16} /> {latestSample.cpu_temp_c}°C
                </span>
              )}

              {latestSample?.cpu_freq_mhz && (
                <span style={{ color: 'var(--accent)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Gauge size={16} /> {(latestSample.cpu_freq_mhz / 1000).toFixed(2)} GHz
                </span>
              )}
            </div>
          </div>

          {/* Progress Bar */}
          <div style={{ width: '100%', height: '9px', background: 'var(--bg-page)', borderRadius: '9999px', overflow: 'hidden', marginBottom: '0.75rem', border: '1px solid var(--border-card)' }}>
            <div style={{
              width: `${Math.min(100, Math.round(progress * 100))}%`,
              height: '100%',
              background: 'linear-gradient(90deg, var(--primary), var(--accent), var(--status-pass))',
              borderRadius: '9999px',
              transition: 'width 0.3s ease'
            }} />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>{currentStage}</span>
            <span style={{ fontWeight: 700, color: 'var(--text-main)' }}>{Math.round(progress * 100)}%</span>
          </div>
        </div>
      )}

      {/* Control Action Buttons */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
        {!isRunning ? (
          <button
            onClick={onStartTest}
            className="btn-primary"
            style={{ padding: '0.75rem 1.6rem', fontSize: '0.95rem' }}
          >
            <Play size={18} /> Start {testLevel}
          </button>
        ) : (
          <button
            onClick={onStopTest}
            className="btn-danger"
            style={{ padding: '0.75rem 1.6rem', fontSize: '0.95rem' }}
          >
            <Square size={18} /> STOP DIAGNOSTIC
          </button>
        )}

        {latestReport && !isRunning && (
          <button
            onClick={() => onViewReport(latestReport)}
            className="btn-secondary"
            style={{ padding: '0.75rem 1.3rem' }}
          >
            <CheckCircle2 size={16} color="var(--status-pass)" />
            View Completed Report ({latestReport.report_id})
          </button>
        )}
      </div>
    </div>
  );
};
