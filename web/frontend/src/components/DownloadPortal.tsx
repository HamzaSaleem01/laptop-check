import React, { useState, useEffect } from 'react';
import { 
  Download, Terminal, Shield, CheckCircle2, 
  Copy, Check, HardDrive, Lock, ArrowRight,
  Sparkles, Zap, FileCode, Layers
} from 'lucide-react';

interface DownloadPortalProps {
  onOpenReportViewer: () => void;
  hasLoadedReport?: boolean;
}

export type SupportedOS = 'windows' | 'macos' | 'linux';

export const DownloadPortal: React.FC<DownloadPortalProps> = ({ 
  onOpenReportViewer, 
  hasLoadedReport 
}) => {
  const [detectedOS, setDetectedOS] = useState<SupportedOS>('windows');
  const [selectedOS, setSelectedOS] = useState<SupportedOS>('windows');
  const [copiedCommand, setCopiedCommand] = useState<string | null>(null);

  // Auto-detect Visitor OS
  useEffect(() => {
    const ua = navigator.userAgent.toLowerCase();
    const plat = ((navigator as any).userAgentData?.platform || navigator.platform || '').toLowerCase();
    
    let current: SupportedOS = 'windows';
    if (plat.includes('mac') || ua.includes('macintosh') || ua.includes('mac os')) {
      current = 'macos';
    } else if (plat.includes('linux') || ua.includes('linux') || ua.includes('x11')) {
      current = 'linux';
    } else {
      current = 'windows';
    }

    setDetectedOS(current);
    setSelectedOS(current);
  }, []);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCommand(id);
    setTimeout(() => setCopiedCommand(null), 2500);
  };

  const getOSDisplayName = (os: SupportedOS) => {
    switch (os) {
      case 'windows': return 'Windows 10 / 11';
      case 'macos': return 'macOS (Apple Silicon & Intel)';
      case 'linux': return 'Linux (Ubuntu, Debian, Fedora, Arch)';
    }
  };

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', paddingBottom: '3rem' }}>
      
      {/* Hero Section */}
      <section style={{ textAlign: 'center', padding: '2.5rem 1rem 3rem 1rem' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.35rem 0.9rem',
          borderRadius: '50px',
          background: 'rgba(99, 102, 241, 0.12)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          color: 'var(--primary)',
          fontSize: '0.82rem',
          fontWeight: 600,
          marginBottom: '1.25rem'
        }}>
          <Sparkles size={14} />
          <span>Version 1.0.0 Stable • 100% Non-Destructive Native Diagnostics</span>
        </div>

        <h1 style={{
          fontSize: 'clamp(2rem, 5vw, 3.25rem)',
          fontWeight: 800,
          lineHeight: 1.15,
          color: 'var(--text-main)',
          marginBottom: '1.2rem',
          letterSpacing: '-0.02em'
        }}>
          Genuine Laptop Diagnostics.<br />
          <span style={{
            background: 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Zero Data Risk. Zero Fake Specs.
          </span>
        </h1>

        <p style={{
          fontSize: 'clamp(1rem, 2vw, 1.15rem)',
          color: 'var(--text-secondary)',
          maxWidth: '740px',
          margin: '0 auto 2rem auto',
          lineHeight: 1.6
        }}>
          Web browsers are sandboxed and cannot access true CPU thermals, RAM channels, 
          NVMe SMART health, or battery wear. Download the native LaptopCheck agent to safely 
          audit any new or used laptop with guaranteed 100% read-only safety.
        </p>

        {/* Operating System Switcher Tabs */}
        <div style={{
          display: 'inline-flex',
          background: 'var(--bg-card-sub)',
          padding: '0.35rem',
          borderRadius: '12px',
          border: '1px solid var(--border-card)',
          gap: '0.4rem',
          marginBottom: '1.5rem',
          flexWrap: 'wrap',
          justifyContent: 'center'
        }}>
          {(['windows', 'macos', 'linux'] as SupportedOS[]).map(os => {
            const isSelected = selectedOS === os;
            const isAutoDetected = detectedOS === os;
            return (
              <button
                key={os}
                onClick={() => setSelectedOS(os)}
                style={{
                  background: isSelected ? 'var(--primary)' : 'transparent',
                  color: isSelected ? '#ffffff' : 'var(--text-secondary)',
                  border: 'none',
                  padding: '0.6rem 1.25rem',
                  borderRadius: '9px',
                  fontWeight: 600,
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  transition: 'all 0.2s ease',
                  boxShadow: isSelected ? '0 4px 12px var(--primary-glow)' : 'none'
                }}
              >
                <span>{os === 'windows' ? '🪟 Windows' : os === 'macos' ? '🍎 macOS' : '🐧 Linux'}</span>
                {isAutoDetected && (
                  <span style={{
                    fontSize: '0.68rem',
                    background: isSelected ? 'rgba(255, 255, 255, 0.25)' : 'var(--primary-light)',
                    color: isSelected ? '#ffffff' : 'var(--primary)',
                    padding: '0.1rem 0.4rem',
                    borderRadius: '4px',
                    fontWeight: 700
                  }}>
                    DETECTED
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Highlighted Primary Action for Selected OS */}
        <div style={{
          maxWidth: '820px',
          margin: '0 auto',
          background: 'var(--bg-card)',
          border: '1px solid var(--border-focus)',
          borderRadius: '16px',
          padding: '2rem',
          boxShadow: 'var(--card-shadow)',
          textAlign: 'left'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.35rem' }}>
                <span style={{
                  background: 'var(--status-pass-bg)',
                  color: 'var(--status-pass)',
                  border: '1px solid var(--status-pass-border)',
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  padding: '0.2rem 0.55rem',
                  borderRadius: '6px'
                }}>
                  RECOMMENDED FOR {selectedOS.toUpperCase()}
                </span>
                <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>
                  {getOSDisplayName(selectedOS)}
                </span>
              </div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)' }}>
                {selectedOS === 'windows' && 'LaptopCheck for Windows (Standalone & Script)'}
                {selectedOS === 'macos' && 'LaptopCheck for macOS (Universal Script & Zip)'}
                {selectedOS === 'linux' && 'LaptopCheck for Linux (Standalone Binary & Script)'}
              </h2>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              {selectedOS === 'windows' && (
                <>
                  <a
                    href="/downloads/LaptopCheck-windows.zip"
                    download="LaptopCheck-windows.zip"
                    className="btn-primary"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.75rem 1.4rem',
                      fontSize: '0.95rem',
                      textDecoration: 'none',
                      borderRadius: '10px'
                    }}
                  >
                    <Download size={18} />
                    <span>Download Windows ZIP</span>
                  </a>
                  <a
                    href="/LaptopCheck_Windows.bat"
                    download="LaptopCheck_Windows.bat"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.75rem 1.2rem',
                      fontSize: '0.95rem',
                      textDecoration: 'none',
                      borderRadius: '10px',
                      background: 'var(--bg-card-sub)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--border-card)',
                      fontWeight: 600
                    }}
                  >
                    <FileCode size={18} />
                    <span>Download .BAT</span>
                  </a>
                </>
              )}

              {selectedOS === 'macos' && (
                <>
                  <a
                    href="/downloads/LaptopCheck-macos.zip"
                    download="LaptopCheck-macos.zip"
                    className="btn-primary"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.75rem 1.4rem',
                      fontSize: '0.95rem',
                      textDecoration: 'none',
                      borderRadius: '10px'
                    }}
                  >
                    <Download size={18} />
                    <span>Download macOS ZIP</span>
                  </a>
                  <a
                    href="/scan_macos.sh"
                    download="scan_macos.sh"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.75rem 1.2rem',
                      fontSize: '0.95rem',
                      textDecoration: 'none',
                      borderRadius: '10px',
                      background: 'var(--bg-card-sub)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--border-card)',
                      fontWeight: 600
                    }}
                  >
                    <FileCode size={18} />
                    <span>Download Script</span>
                  </a>
                </>
              )}

              {selectedOS === 'linux' && (
                <>
                  <a
                    href="/downloads/LaptopCheck-linux-x86_64.tar.gz"
                    download="LaptopCheck-linux-x86_64.tar.gz"
                    className="btn-primary"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.75rem 1.4rem',
                      fontSize: '0.95rem',
                      textDecoration: 'none',
                      borderRadius: '10px'
                    }}
                  >
                    <Download size={18} />
                    <span>Download Linux Binary (tar.gz)</span>
                  </a>
                  <a
                    href="/scan.sh"
                    download="scan.sh"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.75rem 1.2rem',
                      fontSize: '0.95rem',
                      textDecoration: 'none',
                      borderRadius: '10px',
                      background: 'var(--bg-card-sub)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--border-card)',
                      fontWeight: 600
                    }}
                  >
                    <FileCode size={18} />
                    <span>Download Script</span>
                  </a>
                </>
              )}
            </div>
          </div>

          {/* Quick Terminal One-Liner Option */}
          <div style={{
            background: 'var(--bg-input)',
            borderRadius: '10px',
            padding: '1rem 1.25rem',
            border: '1px solid var(--border-subtle)',
            marginBottom: '1.5rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                <Terminal size={14} color="var(--primary)" />
                <span>INSTANT TERMINAL ONE-LINER (NO INSTALLATION REQUIRED):</span>
              </div>
              <button
                onClick={() => {
                  let cmd = '';
                  if (selectedOS === 'windows') {
                    cmd = 'powershell -ExecutionPolicy Bypass -Command "irm https://laptopcheck.vercel.app/scan.ps1 | iex"';
                  } else if (selectedOS === 'macos') {
                    cmd = 'curl -fsSL https://laptopcheck.vercel.app/scan_macos.sh | bash';
                  } else {
                    cmd = 'curl -fsSL https://laptopcheck.vercel.app/scan.sh | bash';
                  }
                  copyToClipboard(cmd, 'cmd-hero');
                }}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: copiedCommand === 'cmd-hero' ? 'var(--status-pass)' : 'var(--text-muted)',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.35rem'
                }}
              >
                {copiedCommand === 'cmd-hero' ? <Check size={14} /> : <Copy size={14} />}
                <span>{copiedCommand === 'cmd-hero' ? 'Copied Command!' : 'Copy Command'}</span>
              </button>
            </div>

            <pre style={{
              margin: 0,
              fontFamily: 'var(--font-mono)',
              fontSize: '0.88rem',
              color: 'var(--text-main)',
              overflowX: 'auto',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-all'
            }}>
              {selectedOS === 'windows' && 'powershell -ExecutionPolicy Bypass -Command "irm https://laptopcheck.vercel.app/scan.ps1 | iex"'}
              {selectedOS === 'macos' && 'curl -fsSL https://laptopcheck.vercel.app/scan_macos.sh | bash'}
              {selectedOS === 'linux' && 'curl -fsSL https://laptopcheck.vercel.app/scan.sh | bash'}
            </pre>
          </div>

          {/* Step-by-Step Instructions */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <div style={{
                width: '28px',
                height: '28px',
                borderRadius: '50%',
                background: 'var(--primary-light)',
                color: 'var(--primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 700,
                fontSize: '0.85rem',
                flexShrink: 0
              }}>1</div>
              <div>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.2rem' }}>
                  {selectedOS === 'windows' ? 'Download or Run One-Liner' : 'Download or Run in Terminal'}
                </h4>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  {selectedOS === 'windows' ? 'Run LaptopCheck_Windows.bat or paste the PowerShell command above.' : 'Open Terminal and run the quick command or download the executable package.'}
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <div style={{
                width: '28px',
                height: '28px',
                borderRadius: '50%',
                background: 'var(--primary-light)',
                color: 'var(--primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 700,
                fontSize: '0.85rem',
                flexShrink: 0
              }}>2</div>
              <div>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.2rem' }}>
                  Safe 100% Read-Only Scan
                </h4>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  The agent scans CPU, RAM channels, battery wear & NVMe SMART in 15–30 seconds within safe limits.
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <div style={{
                width: '28px',
                height: '28px',
                borderRadius: '50%',
                background: 'var(--primary-light)',
                color: 'var(--primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 700,
                fontSize: '0.85rem',
                flexShrink: 0
              }}>3</div>
              <div>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.2rem' }}>
                  Instant Report & Offline File
                </h4>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  Outputs a terminal matrix and generates <code style={{ color: 'var(--primary)' }}>laptop_specs.json</code> to view or export.
                </p>
              </div>
            </div>
          </div>

          {/* Quick link to Inspect Report */}
          <div style={{ marginTop: '1.5rem', paddingTop: '1.25rem', borderTop: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              {hasLoadedReport ? 'Diagnostic report currently loaded for your machine:' : 'Already ran the collector on your laptop?'}
            </span>
            <button
              onClick={onOpenReportViewer}
              style={{
                background: hasLoadedReport ? 'var(--primary-light)' : 'transparent',
                border: '1px solid var(--border-card)',
                color: hasLoadedReport ? 'var(--primary)' : 'var(--text-main)',
                padding: '0.45rem 0.9rem',
                borderRadius: '8px',
                fontSize: '0.82rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                transition: 'all 0.15s ease'
              }}
            >
              <span>{hasLoadedReport ? 'View Loaded Assessment' : 'Inspect Saved Report / JSON'}</span>
              <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </section>

      {/* Safety & Non-Destructive Protection Guarantee (Crucial Section) */}
      <section style={{
        margin: '2rem 1rem',
        background: 'linear-gradient(180deg, rgba(16, 185, 129, 0.05) 0%, rgba(17, 24, 39, 0.4) 100%)',
        border: '1px solid var(--status-pass-border)',
        borderRadius: '16px',
        padding: '2.5rem 2rem'
      }}>
        <div style={{ textAlign: 'center', maxWidth: '720px', margin: '0 auto 2rem auto' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.3rem 0.75rem',
            borderRadius: '50px',
            background: 'var(--status-pass-bg)',
            color: 'var(--status-pass)',
            fontSize: '0.8rem',
            fontWeight: 700,
            marginBottom: '0.75rem'
          }}>
            <Shield size={14} />
            <span>STRICT SAFETY & NON-DESTRUCTIVE GUARANTEE</span>
          </div>
          <h2 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.75rem' }}>
            Safe for 5+ Year Old Laptops & Valuable Personal Data
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.5 }}>
            Whether testing a brand new machine in a computer shop or auditing a 5-year-old laptop filled with irreplaceable files, LaptopCheck runs under strict, fail-safe boundaries.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
          
          <div className="spec-subcard" style={{ padding: '1.5rem' }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              background: 'var(--status-pass-bg)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1rem'
            }}>
              <CheckCircle2 size={22} color="var(--status-pass)" />
            </div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
              100% Read-Only Inspection
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              LaptopCheck <strong>NEVER deletes, moves, or modifies</strong> any existing user documents, operating system files, or disk partitions. Your data is completely untouched.
            </p>
          </div>

          <div className="spec-subcard" style={{ padding: '1.5rem' }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              background: 'rgba(99, 102, 241, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1rem'
            }}>
              <Zap size={22} color="var(--primary)" />
            </div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
              Capacity & Thermal Bounded
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              Tests run in short, controlled slices and <strong>never overload or burn out</strong> aging hardware. Active thermal guardians throttle load or abort immediately if temperatures reach warning thresholds.
            </p>
          </div>

          <div className="spec-subcard" style={{ padding: '1.5rem' }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              background: 'rgba(6, 182, 212, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1rem'
            }}>
              <HardDrive size={22} color="var(--accent)" />
            </div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
              Non-Destructive Storage Verification
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              Storage health reads genuine firmware SMART status and Windows/Linux kernel counters without raw block overrides. Any temporary benchmark file is strictly ephemeral and deleted immediately.
            </p>
          </div>

          <div className="spec-subcard" style={{ padding: '1.5rem' }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              background: 'rgba(245, 158, 11, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1rem'
            }}>
              <Lock size={22} color="var(--status-caution)" />
            </div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
              Privacy-First & Anonymous
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              Hardware serial numbers, MAC addresses, and local system hostnames are automatically redacted by default, protecting user privacy during second-hand sale inspections.
            </p>
          </div>

        </div>
      </section>

      {/* Why Native App vs Browser Sandbox */}
      <section style={{ margin: '3rem 1rem', padding: '0 0.5rem' }}>
        <div style={{ textAlign: 'center', maxWidth: '720px', margin: '0 auto 2.5rem auto' }}>
          <h2 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.75rem' }}>
            Why Download an App Instead of Browser Testing?
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.5 }}>
            Modern web browsers enforce strict security sandboxes. Any website claiming to accurately test internal laptop health without a native collector is displaying mock or incomplete data.
          </p>
        </div>

        <div style={{
          background: 'var(--bg-card)',
          borderRadius: '16px',
          border: '1px solid var(--border-card)',
          overflow: 'hidden'
        }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1.5fr 1fr 1fr',
            padding: '1rem 1.5rem',
            background: 'var(--bg-card-sub)',
            borderBottom: '1px solid var(--border-card)',
            fontWeight: 700,
            fontSize: '0.88rem',
            color: 'var(--text-secondary)'
          }}>
            <div>HARDWARE CAPABILITY</div>
            <div style={{ color: 'var(--status-fail)' }}>WEB BROWSER SANDBOX</div>
            <div style={{ color: 'var(--status-pass)' }}>LAPTOPCHECK NATIVE APP</div>
          </div>

          {[
            {
              cap: 'Physical CPU Thermal Sensors (°C)',
              browser: 'Blocked (Sandboxed — cannot access hwmon / ACPI)',
              native: 'Genuine Core Temp via Linux hwmon / WMI / Apple SMI'
            },
            {
              cap: 'RAM Channels & Module Configuration',
              browser: 'Capped at 8GB generic estimate (Anti-fingerprinting)',
              native: 'Exact Dual-Channel / Single-Channel via SMBIOS'
            },
            {
              cap: 'NVMe SSD SMART Health & Wear Indicator',
              browser: 'Impossible (Web pages cannot query disk controllers)',
              native: 'Accurate SMART self-test & wear percentage'
            },
            {
              cap: 'Battery Physical Health & Cycle Count',
              browser: 'Charge % only (Cannot read degradation or ACPI cycles)',
              native: 'Full ACPI Design vs Actual Capacity + Cycle Count'
            },
            {
              cap: 'Data Safety & Non-Destructive Guarantee',
              browser: 'Cannot inspect or guarantee disk state',
              native: '100% Read-Only verified and bounded tests'
            }
          ].map((row, idx) => (
            <div
              key={idx}
              style={{
                display: 'grid',
                gridTemplateColumns: '1.5fr 1fr 1fr',
                padding: '1.1rem 1.5rem',
                borderBottom: idx < 4 ? '1px solid var(--border-subtle)' : 'none',
                fontSize: '0.85rem',
                alignItems: 'center'
              }}
            >
              <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                {row.cap}
              </div>
              <div style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <span style={{ color: 'var(--status-fail)', fontWeight: 700 }}>✕</span>
                <span>{row.browser}</span>
              </div>
              <div style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <span style={{ color: 'var(--status-pass)', fontWeight: 700 }}>✓</span>
                <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{row.native}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* All Platform Packages & Formats Table */}
      <section style={{ margin: '3rem 1rem' }}>
        <div style={{ textAlign: 'center', maxWidth: '720px', margin: '0 auto 2rem auto' }}>
          <h2 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
            All Download Formats & Packages
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Clean, portable, and zero-dependency options for Windows, macOS, and Linux.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
          
          {/* Windows Card */}
          <div className="glass-panel" style={{ padding: '1.75rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <span style={{ fontSize: '1.3rem' }}>🪟 Windows</span>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, padding: '0.2rem 0.5rem', borderRadius: '5px', background: 'var(--primary-light)', color: 'var(--primary)' }}>
                  PORTABLE ZIP & SCRIPT
                </span>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem', lineHeight: 1.4 }}>
                For Windows 10 and Windows 11 (64-bit). Inspects via native CIM/WMI without installing external drivers.
              </p>

              <div style={{ background: 'var(--bg-input)', padding: '0.75rem', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.8rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                <code>powershell -c "irm https://laptopcheck.vercel.app/scan.ps1 | iex"</code>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <a
                href="/downloads/LaptopCheck-windows.zip"
                download="LaptopCheck-windows.zip"
                className="btn-primary"
                style={{ flex: 1, textAlign: 'center', textDecoration: 'none', padding: '0.65rem' }}
              >
                Download ZIP
              </a>
              <a
                href="/LaptopCheck_Windows.bat"
                download="LaptopCheck_Windows.bat"
                style={{ padding: '0.65rem 1rem', background: 'var(--bg-card-sub)', color: 'var(--text-main)', border: '1px solid var(--border-card)', borderRadius: '8px', textDecoration: 'none', fontWeight: 600, fontSize: '0.85rem' }}
              >
                .BAT
              </a>
            </div>
          </div>

          {/* macOS Card */}
          <div className="glass-panel" style={{ padding: '1.75rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <span style={{ fontSize: '1.3rem' }}>🍎 macOS</span>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, padding: '0.2rem 0.5rem', borderRadius: '5px', background: 'var(--primary-light)', color: 'var(--primary)' }}>
                  UNIVERSAL (M1–M4 & INTEL)
                </span>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem', lineHeight: 1.4 }}>
                Works on macOS Monterey, Ventura, Sonoma, and Sequoia. Inspects genuine battery cycle count and health via ioreg.
              </p>

              <div style={{ background: 'var(--bg-input)', padding: '0.75rem', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.8rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                <code>curl -fsSL https://laptopcheck.vercel.app/scan_macos.sh | bash</code>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <a
                href="/downloads/LaptopCheck-macos.zip"
                download="LaptopCheck-macos.zip"
                className="btn-primary"
                style={{ flex: 1, textAlign: 'center', textDecoration: 'none', padding: '0.65rem' }}
              >
                Download macOS ZIP
              </a>
              <a
                href="/scan_macos.sh"
                download="scan_macos.sh"
                style={{ padding: '0.65rem 1rem', background: 'var(--bg-card-sub)', color: 'var(--text-main)', border: '1px solid var(--border-card)', borderRadius: '8px', textDecoration: 'none', fontWeight: 600, fontSize: '0.85rem' }}
              >
                Script
              </a>
            </div>
          </div>

          {/* Linux Card */}
          <div className="glass-panel" style={{ padding: '1.75rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <span style={{ fontSize: '1.3rem' }}>🐧 Linux</span>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, padding: '0.2rem 0.5rem', borderRadius: '5px', background: 'var(--primary-light)', color: 'var(--primary)' }}>
                  STANDALONE BINARY & BASH
                </span>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem', lineHeight: 1.4 }}>
                Pre-compiled ELF binary and safe bash script for Ubuntu, Debian, Fedora, Arch, and RHEL x86_64.
              </p>

              <div style={{ background: 'var(--bg-input)', padding: '0.75rem', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.8rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                <code>curl -fsSL https://laptopcheck.vercel.app/scan.sh | bash</code>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <a
                href="/downloads/LaptopCheck-linux-x86_64.tar.gz"
                download="LaptopCheck-linux-x86_64.tar.gz"
                className="btn-primary"
                style={{ flex: 1, textAlign: 'center', textDecoration: 'none', padding: '0.65rem' }}
              >
                Download Binary
              </a>
              <a
                href="/scan.sh"
                download="scan.sh"
                style={{ padding: '0.65rem 1rem', background: 'var(--bg-card-sub)', color: 'var(--text-main)', border: '1px solid var(--border-card)', borderRadius: '8px', textDecoration: 'none', fontWeight: 600, fontSize: '0.85rem' }}
              >
                Script
              </a>
            </div>
          </div>

        </div>
      </section>

      {/* Versioning & Release Roadmap (Well-Maintained Future) */}
      <section style={{
        margin: '3rem 1rem',
        padding: '2rem',
        background: 'var(--bg-card)',
        borderRadius: '16px',
        border: '1px solid var(--border-card)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
              <Layers size={18} color="var(--primary)" />
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)' }}>
                Release Versioning & Maintenance Roadmap
              </h3>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Built for reliability, regular updates, and enterprise-grade longevity.
            </p>
          </div>
          <span style={{
            background: 'var(--primary-light)',
            color: 'var(--primary)',
            padding: '0.3rem 0.75rem',
            borderRadius: '20px',
            fontSize: '0.8rem',
            fontWeight: 700,
            border: '1px solid var(--border-focus)'
          }}>
            CURRENT: v1.0.0
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
          
          <div style={{ padding: '1.25rem', background: 'var(--bg-card-sub)', borderRadius: '12px', borderLeft: '4px solid var(--status-pass)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontWeight: 700, color: 'var(--text-main)', fontSize: '0.95rem' }}>v1.0.0 (Current Stable)</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--status-pass)', fontWeight: 700 }}>ACTIVE</span>
            </div>
            <ul style={{ paddingLeft: '1.2rem', fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
              <li>Cross-platform safe read-only collectors (Windows, macOS, Linux).</li>
              <li>Dual-channel RAM topology & NVMe SMART telemetry extraction.</li>
              <li>ACPI battery wear & physical cycle count measurement.</li>
              <li>Computational Materials Science & Programming suitability algorithms.</li>
            </ul>
          </div>

          <div style={{ padding: '1.25rem', background: 'var(--bg-card-sub)', borderRadius: '12px', borderLeft: '4px solid var(--primary)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontWeight: 700, color: 'var(--text-main)', fontSize: '0.95rem' }}>v1.1.0 (Next Upgrade)</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--primary)', fontWeight: 700 }}>IN PROGRESS</span>
            </div>
            <ul style={{ paddingLeft: '1.2rem', fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
              <li>Direct desktop GUI window (Electron/Tauri wrapper).</li>
              <li>Expanded workload profiles: Deep Learning, CAD, and 4K Video Editing.</li>
              <li>Automated battery charge/discharge slope degradation modeling.</li>
            </ul>
          </div>

          <div style={{ padding: '1.25rem', background: 'var(--bg-card-sub)', borderRadius: '12px', borderLeft: '4px solid var(--accent)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontWeight: 700, color: 'var(--text-main)', fontSize: '0.95rem' }}>v2.0.0 (Long-Term Vision)</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--accent)', fontWeight: 700 }}>PLANNED</span>
            </div>
            <ul style={{ paddingLeft: '1.2rem', fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
              <li>Enterprise refurbished laptop verification & bulk auditing.</li>
              <li>Cryptographically signed tamper-proof hardware certificate seals.</li>
              <li>Shop-mode rapid thermal dissipation testing and fan RPM acoustic curves.</li>
            </ul>
          </div>

        </div>
      </section>

    </div>
  );
};
