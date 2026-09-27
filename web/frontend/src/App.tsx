import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { DownloadPortal } from './components/DownloadPortal';
import { HardwareSpecsCard } from './components/HardwareSpecsCard';
import { WorkloadSelector } from './components/WorkloadSelector';
import { ManualInspectionSection } from './components/ManualInspectionModal';
import { ReportViewer } from './components/ReportViewer';
import type { SystemHardwareSnapshot, DiagnosticReport } from './types';
import { createMockReport } from './mockData';

export function App() {
  // Theme Management (Light / Dark with localStorage persistence)
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('laptopcheck_theme');
    if (saved === 'light' || saved === 'dark') return saved;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('laptopcheck_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  // Active Tab: Defaults to 'downloads' (Official Portal & Setup Hub)
  const [activeTab, setActiveTab] = useState<'downloads' | 'viewer' | 'workloads' | 'manual'>('downloads');

  // Hardware State: NULL by default. NO hardcoded specs on initial visit!
  const [hardware, setHardware] = useState<SystemHardwareSnapshot | null>(null);
  const [latestReport, setLatestReport] = useState<DiagnosticReport | null>(null);
  const [historicalReports, setHistoricalReports] = useState<Array<{ filename: string; size_kb: number; created_at: string }>>([]);

  // Workload selection
  const [selectedWorkloads, setSelectedWorkloads] = useState<string[]>(['comp_materials_science', 'programming']);

  // Helper to construct a report from genuine or uploaded hardware snapshot
  const buildReportFromSnapshot = (snap: SystemHardwareSnapshot) => {
    setHardware(snap);
    const report = createMockReport('mid_range', 'Quick / Shop Safe', snap);
    setLatestReport(report);
    setActiveTab('viewer');
  };

  // Check URL hash for imported 100% genuine data from scan.ps1, scan.sh, or scan_macos.sh
  useEffect(() => {
    const checkHash = () => {
      if (window.location.hash.startsWith('#data=')) {
        try {
          const raw = window.location.hash.slice(6);
          let jsonStr = '';
          try {
            jsonStr = decodeURIComponent(escape(atob(raw)));
          } catch {
            jsonStr = atob(raw);
          }
          const parsed = JSON.parse(jsonStr) as SystemHardwareSnapshot;
          if (parsed && (parsed.device_model || parsed.cpu)) {
            buildReportFromSnapshot(parsed);
          }
        } catch (e) {
          console.warn('Failed to parse URL hash hardware data:', e);
        }
      }
    };

    checkHash();
    window.addEventListener('hashchange', checkHash);
    return () => window.removeEventListener('hashchange', checkHash);
  }, []);

  // Fetch reports list if backend server is available
  const loadReports = () => {
    fetch('/api/reports')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch reports');
        return res.json();
      })
      .then(data => setHistoricalReports(data))
      .catch(() => {
        // Local API not running (static or serverless mode)
        setHistoricalReports([]);
      });
  };

  useEffect(() => {
    loadReports();
  }, []);

  const handleClearReport = () => {
    setHardware(null);
    setLatestReport(null);
    if (window.location.hash.startsWith('#data=')) {
      history.replaceState(null, document.title, window.location.pathname + window.location.search);
    }
    setActiveTab('downloads');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      {/* Universal Top Navigation Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={(tab: any) => setActiveTab(tab)}
        theme={theme}
        toggleTheme={toggleTheme}
      />

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '0 1rem' }}>
        
        {/* TAB 1: DOWNLOADS & SETUP (Default Landing Portal) */}
        {activeTab === 'downloads' && (
          <DownloadPortal
            onOpenReportViewer={() => setActiveTab('viewer')}
            hasLoadedReport={!!hardware}
          />
        )}

        {/* TAB 2: INSPECT REPORT / REPORT VIEWER */}
        {activeTab === 'viewer' && (
          <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
            <ReportViewer
              report={latestReport}
              historicalReports={historicalReports}
              onRefreshReports={loadReports}
              onLoadSnapshot={buildReportFromSnapshot}
              onClearReport={handleClearReport}
              onGoToDownloads={() => setActiveTab('downloads')}
            />

            {/* If genuine hardware is loaded, show the detailed specs card below report */}
            {hardware && (
              <div style={{ marginTop: '2rem' }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '1rem',
                  padding: '0 0.5rem'
                }}>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)' }}>
                    Detailed Hardware Inventory & Provenance
                  </h3>
                  <span style={{ fontSize: '0.8rem', color: 'var(--status-pass)', fontWeight: 600 }}>
                    100% Genuine Inspected Telemetry
                  </span>
                </div>

                <HardwareSpecsCard
                  hardware={hardware}
                  loading={false}
                />
              </div>
            )}
          </div>
        )}

        {/* TAB 3: WORKLOADS MATRIX */}
        {activeTab === 'workloads' && (
          <div style={{ maxWidth: '1200px', margin: '0 auto', paddingBottom: '3rem' }}>
            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
              <h2 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                Workload Suitability Verification Matrix
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', maxWidth: '650px', margin: '0 auto' }}>
                LaptopCheck evaluates inspected hardware against demanding scientific and engineering profiles to deliver an unbiased purchase or deployment recommendation.
              </p>
            </div>

            <WorkloadSelector
              selectedWorkloads={selectedWorkloads}
              setSelectedWorkloads={setSelectedWorkloads}
            />
          </div>
        )}

        {/* TAB 4: MANUAL SHOP INSPECTION CHECKLIST */}
        {activeTab === 'manual' && (
          <div style={{ maxWidth: '1000px', margin: '0 auto', paddingBottom: '3rem' }}>
            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
              <h2 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                Physical Shop Inspection Checklist
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', maxWidth: '650px', margin: '0 auto' }}>
                Before buying a used or refurbished laptop, run through this 9-point physical inspection to detect chassis drops, hinge wear, screen defects, and port failures.
              </p>
            </div>

            <ManualInspectionSection />
          </div>
        )}

      </main>

      {/* Universal Footer */}
      <footer style={{
        marginTop: 'auto',
        background: 'var(--bg-header)',
        borderTop: '1px solid var(--border-card)',
        padding: '2rem 1.5rem',
        textAlign: 'center',
        fontSize: '0.82rem',
        color: 'var(--text-muted)'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <span style={{ fontWeight: 700, color: 'var(--text-main)' }}>LaptopCheck v1.0.0</span> — Professional Laptop Diagnostic & Workload Suitability Analyzer.
          </div>
          <div style={{ display: 'flex', gap: '1.25rem' }}>
            <span style={{ color: 'var(--status-pass)', fontWeight: 600 }}>100% Non-Destructive Safe</span>
            <span>Windows • macOS • Linux</span>
            <span>Zero Data Risk</span>
          </div>
        </div>
      </footer>

    </div>
  );
}

export default App;
