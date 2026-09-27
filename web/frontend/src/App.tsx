import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { HardwareSpecsCard } from './components/HardwareSpecsCard';
import { DiagnosticTestController } from './components/DiagnosticTestController';
import { WorkloadSelector } from './components/WorkloadSelector';
import { ManualInspectionSection } from './components/ManualInspectionModal';
import { ReportViewer } from './components/ReportViewer';
import { Globe } from 'lucide-react';
import type { SystemHardwareSnapshot, DiagnosticReport } from './types';
import { MOCK_SIMULATION_PRESETS_LIST, MOCK_HARDWARE_PRESETS, createMockReport } from './mockData';

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

  const [activeTab, setActiveTab] = useState('diagnostics');
  const [isSimulation, setIsSimulation] = useState(true);
  const [simulationPreset, setSimulationPreset] = useState('mid_range');
  const [simulationPresetsList, setSimulationPresetsList] = useState(MOCK_SIMULATION_PRESETS_LIST);

  const [hardware, setHardware] = useState<SystemHardwareSnapshot | null>(MOCK_HARDWARE_PRESETS.mid_range);
  const [loadingHardware, setLoadingHardware] = useState(false);
  const [isCloudDemo, setIsCloudDemo] = useState(false);

  // Test Run State
  const [testLevel, setTestLevel] = useState('Quick / Shop Safe');
  const [selectedWorkloads, setSelectedWorkloads] = useState<string[]>(['comp_materials_science', 'programming']);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState('Ready');
  const [elapsedSecs, setElapsedSecs] = useState(0);
  const [safetyLevel, setSafetyLevel] = useState('NORMAL');
  const [latestSample, setLatestSample] = useState<any>(null);

  const [latestReport, setLatestReport] = useState<DiagnosticReport | null>(null);
  const [historicalReports, setHistoricalReports] = useState<Array<{ filename: string; size_kb: number; created_at: string }>>([]);

  // Fetch simulation presets list from API if available
  useEffect(() => {
    fetch('/api/simulation/presets')
      .then(res => {
        if (!res.ok) throw new Error('API server returned error');
        return res.json();
      })
      .then(data => {
        setSimulationPresetsList(data);
        setIsCloudDemo(false);
      })
      .catch(() => {
        // Cloud / Standalone mode on Vercel
        setIsCloudDemo(true);
      });
  }, []);

  // Fetch hardware snapshot from API with fallback to rich preset data
  const loadHardware = () => {
    setLoadingHardware(true);
    fetch(`/api/hardware?simulate=${isSimulation}&preset=${simulationPreset}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        setHardware(data);
        setLoadingHardware(false);
        setIsCloudDemo(false);
      })
      .catch(() => {
        // Fallback to client-side preset for Vercel deployment
        const fallbackHw = MOCK_HARDWARE_PRESETS[simulationPreset] || MOCK_HARDWARE_PRESETS.mid_range;
        setHardware(fallbackHw);
        setLoadingHardware(false);
        setIsCloudDemo(true);
      });
  };

  useEffect(() => {
    loadHardware();
  }, [isSimulation, simulationPreset]);

  // Fetch reports list
  const loadReports = () => {
    fetch('/api/reports')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch reports');
        return res.json();
      })
      .then(data => setHistoricalReports(data))
      .catch(() => {
        // Fallback reports on Vercel
        setHistoricalReports([
          { filename: 'LaptopCheck_ThinkPad_E14_Gen_4_Sample.pdf', size_kb: 56.9, created_at: '2026-09-27 19:42:32' },
          { filename: 'LaptopCheck_Precision_7770_Sample.pdf', size_kb: 64.2, created_at: '2026-09-27 18:41:06' },
          { filename: 'LaptopCheck_EcoBook_14_Sample.pdf', size_kb: 54.4, created_at: '2026-09-27 18:48:05' }
        ]);
      });
  };

  useEffect(() => {
    loadReports();
  }, []);

  // Polling during active test if connected to backend
  useEffect(() => {
    let interval: any = null;
    if (isRunning && !isCloudDemo) {
      interval = setInterval(() => {
        fetch('/api/test-runs/active')
          .then(res => res.json())
          .then(data => {
            setProgress(data.progress || 0);
            setCurrentStage(data.current_stage || 'Testing...');
            setElapsedSecs(data.elapsed_secs || 0);
            setSafetyLevel(data.safety_level || 'NORMAL');
            if (data.latest_sample) {
              setLatestSample(data.latest_sample);
            }

            if (!data.is_running && data.progress >= 1.0) {
              setIsRunning(false);
              if (data.latest_report) {
                setLatestReport(data.latest_report);
                setActiveTab('reports');
              }
              loadReports();
            }
          })
          .catch(() => {});
      }, 700);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isRunning, isCloudDemo]);

  // Client-side simulation runner for Vercel Cloud Demo
  const runCloudDemoTest = () => {
    setIsRunning(true);
    setProgress(0.05);
    setCurrentStage('Initializing diagnostic sequence...');
    setElapsedSecs(0);

    const stages = [
      { pct: 0.15, stage: 'Probing CPU multi-core burst capability...', temp: 48, freq: 2800 },
      { pct: 0.35, stage: 'Testing sustained multi-threading & thermal stability...', temp: 64, freq: 2600 },
      { pct: 0.55, stage: 'Measuring RAM sequential bandwidth & integrity...', temp: 68, freq: 2700 },
      { pct: 0.72, stage: 'Benchmarking storage sequential read/write...', temp: 59, freq: 2800 },
      { pct: 0.88, stage: 'Executing scientific BLAS DGEMM routines...', temp: 71, freq: 2500 },
      { pct: 0.96, stage: 'Evaluating workload suitability requirements...', temp: 54, freq: 2800 },
      { pct: 1.0, stage: 'Diagnostic complete! Building assessment report...', temp: 49, freq: 2800 }
    ];

    let currentIdx = 0;
    const interval = setInterval(() => {
      currentIdx += 1;
      setElapsedSecs(prev => prev + 1);

      if (currentIdx < stages.length) {
        const item = stages[currentIdx];
        setProgress(item.pct);
        setCurrentStage(item.stage);
        setLatestSample({ cpu_temp_c: item.temp, cpu_freq_mhz: item.freq });
      } else {
        clearInterval(interval);
        setIsRunning(false);
        const report = createMockReport(simulationPreset, testLevel);
        setLatestReport(report);
        setActiveTab('reports');
      }
    }, 1200);
  };

  // Start test handler
  const handleStartTest = () => {
    if (isCloudDemo) {
      runCloudDemoTest();
      return;
    }

    fetch('/api/test-runs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        test_level: testLevel,
        workload_ids: selectedWorkloads,
        simulate: isSimulation,
        simulation_preset: simulationPreset
      })
    })
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(() => {
        setIsRunning(true);
        setProgress(0.02);
        setCurrentStage('Initializing diagnostic engine...');
      })
      .catch(() => {
        // Fallback to cloud demo simulation
        runCloudDemoTest();
      });
  };

  // Stop test handler
  const handleStopTest = () => {
    if (isCloudDemo) {
      setIsRunning(false);
      setCurrentStage('Test aborted by user');
      return;
    }

    fetch('/api/test-runs/stop', { method: 'POST' })
      .then(() => {
        setIsRunning(false);
        setCurrentStage('Test aborted by user');
      })
      .catch(() => {
        setIsRunning(false);
      });
  };

  return (
    <div style={{ minHeight: '100vh', paddingBottom: '3rem' }}>
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isSimulation={isSimulation}
        setIsSimulation={setIsSimulation}
        simulationPreset={simulationPreset}
        setSimulationPreset={setSimulationPreset}
        simulationPresetsList={simulationPresetsList}
        theme={theme}
        toggleTheme={toggleTheme}
      />

      <main style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 1.5rem' }}>
        {/* Cloud Demo Notification Pill */}
        {isCloudDemo && (
          <div className="spec-subcard" style={{
            padding: '0.65rem 1rem',
            marginBottom: '1rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.5rem',
            border: '1px solid var(--border-focus)',
            background: 'var(--primary-light)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-main)' }}>
              <Globe size={15} color="var(--primary)" />
              <span><b>Live Cloud Interactive Mode:</b> Full simulated diagnostic suites, hardware presets, and test sequences active in browser.</span>
            </div>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Run <code>./LaptopCheck --open-browser</code> locally to connect to physical machine sensors.
            </span>
          </div>
        )}

        {/* Hardware Snapshot visible on primary tabs */}
        <HardwareSpecsCard hardware={hardware} loading={loadingHardware} />

        {/* Tab 1: Diagnostics & Run */}
        {activeTab === 'diagnostics' && (
          <div>
            <DiagnosticTestController
              testLevel={testLevel}
              setTestLevel={setTestLevel}
              isRunning={isRunning}
              progress={progress}
              currentStage={currentStage}
              elapsedSecs={elapsedSecs}
              safetyLevel={safetyLevel}
              latestSample={latestSample}
              onStartTest={handleStartTest}
              onStopTest={handleStopTest}
              latestReport={latestReport}
              onViewReport={(rep) => {
                setLatestReport(rep);
                setActiveTab('reports');
              }}
            />

            <WorkloadSelector
              selectedWorkloads={selectedWorkloads}
              setSelectedWorkloads={setSelectedWorkloads}
            />
          </div>
        )}

        {/* Tab 2: Workloads & Suitability */}
        {activeTab === 'workloads' && (
          <WorkloadSelector
            selectedWorkloads={selectedWorkloads}
            setSelectedWorkloads={setSelectedWorkloads}
          />
        )}

        {/* Tab 3: Manual Shop Checks */}
        {activeTab === 'manual' && (
          <ManualInspectionSection />
        )}

        {/* Tab 4: PDF Reports */}
        {activeTab === 'reports' && (
          <ReportViewer
            report={latestReport}
            historicalReports={historicalReports}
            onRefreshReports={loadReports}
          />
        )}
      </main>
    </div>
  );
}

export default App;
