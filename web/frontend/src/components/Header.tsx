import React from 'react';
import { Laptop, Cpu, ShieldCheck, FileText, CheckSquare, Sun, Moon, Download } from 'lucide-react';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isSimulation: boolean;
  setIsSimulation: (sim: boolean) => void;
  simulationPreset: string;
  setSimulationPreset: (preset: string) => void;
  simulationPresetsList: Array<{ id: string; label: string }>;
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  isSimulation,
  setIsSimulation,
  simulationPreset,
  setSimulationPreset,
  simulationPresetsList,
  theme,
  toggleTheme,
}) => {
  return (
    <header className="glass-panel" style={{ margin: '1rem auto', padding: '0.85rem 1.5rem', maxWidth: '1400px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        
        {/* Brand & Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            background: 'linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%)',
            padding: '0.65rem',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 14px var(--primary-glow)'
          }}>
            <Laptop size={24} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h1 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-main)' }}>LaptopCheck</h1>
              <span style={{
                background: 'var(--primary-light)',
                color: 'var(--primary)',
                fontSize: '0.7rem',
                fontWeight: 700,
                padding: '0.15rem 0.45rem',
                borderRadius: '6px',
                border: '1px solid var(--border-focus)'
              }}>v1.0.0</span>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Hardware Diagnostic & Workload Suitability Analyzer
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{
          display: 'flex',
          gap: '0.35rem',
          background: 'var(--bg-nav)',
          padding: '0.3rem',
          borderRadius: '10px',
          border: '1px solid var(--border-card)'
        }}>
          {[
            { id: 'diagnostics', label: 'Diagnostics & Run', icon: <Cpu size={15} /> },
            { id: 'workloads', label: 'Workloads & Matrix', icon: <ShieldCheck size={15} /> },
            { id: 'manual', label: 'Manual Shop Checks', icon: <CheckSquare size={15} /> },
            { id: 'reports', label: 'PDF Reports', icon: <FileText size={15} /> }
          ].map(tab => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  background: isActive ? 'var(--primary)' : 'transparent',
                  color: isActive ? '#ffffff' : 'var(--text-muted)',
                  border: 'none',
                  padding: '0.45rem 0.85rem',
                  borderRadius: '7px',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  transition: 'all 0.15s ease'
                }}
              >
                {tab.icon}
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Controls: Mode Toggle, Portable Tool Download & Theme Switch */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexWrap: 'wrap' }}>
          {/* Portable .bat Download Button */}
          <a
            href="/LaptopCheck_Windows.bat"
            download="LaptopCheck_Windows.bat"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.35rem 0.75rem',
              borderRadius: '8px',
              fontSize: '0.76rem',
              fontWeight: 700,
              textDecoration: 'none',
              color: '#ffffff',
              background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
              boxShadow: '0 2px 8px rgba(2, 132, 199, 0.3)',
              border: 'none',
              transition: 'transform 0.15s ease'
            }}
            title="Download zero-install Windows hardware scanner to extract genuine BIOS, NVMe SMART & battery wear cycles"
          >
            <Download size={13} color="#ffffff" />
            <span>Windows .bat</span>
          </a>

          {/* Mode Switcher: Live This Device vs Reference Profiles */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.45rem',
            background: isSimulation ? 'var(--status-caution-bg)' : 'var(--status-pass-bg)',
            border: `1px solid ${isSimulation ? 'var(--status-caution-border)' : 'var(--status-pass-border)'}`,
            padding: '0.3rem 0.65rem',
            borderRadius: '9999px',
            fontSize: '0.74rem',
            fontWeight: 700
          }}>
            <span style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              background: isSimulation ? 'var(--status-caution)' : 'var(--status-pass)',
              boxShadow: `0 0 6px ${isSimulation ? 'var(--status-caution)' : 'var(--status-pass)'}`
            }} />
            <span style={{ color: isSimulation ? 'var(--status-caution)' : 'var(--status-pass)' }}>
              {isSimulation ? 'REFERENCE PRESETS' : 'THIS DEVICE (LIVE)'}
            </span>
            <button
              onClick={() => setIsSimulation(!isSimulation)}
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-card)',
                color: 'var(--text-main)',
                padding: '0.15rem 0.45rem',
                borderRadius: '5px',
                fontSize: '0.68rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
              title={isSimulation ? "Switch to probing this machine's actual hardware" : "Switch to comparing against standard reference laptops"}
            >
              {isSimulation ? 'Detect This PC' : 'Compare Presets'}
            </button>
          </div>

          {isSimulation && (
            <select
              value={simulationPreset}
              onChange={(e) => setSimulationPreset(e.target.value)}
              style={{
                background: 'var(--bg-input)',
                color: 'var(--text-main)',
                border: '1px solid var(--border-card)',
                padding: '0.35rem 0.55rem',
                borderRadius: '7px',
                fontSize: '0.76rem',
                fontWeight: 500,
                cursor: 'pointer'
              }}
            >
              {simulationPresetsList.map(p => (
                <option key={p.id} value={p.id}>{p.label}</option>
              ))}
            </select>
          )}

          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            className="theme-toggle-btn"
            title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Theme`}
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? (
              <>
                <Sun size={15} color="#f59e0b" />
                <span>Light</span>
              </>
            ) : (
              <>
                <Moon size={15} color="var(--primary)" />
                <span>Dark</span>
              </>
            )}
          </button>
        </div>

      </div>
    </header>
  );
};
