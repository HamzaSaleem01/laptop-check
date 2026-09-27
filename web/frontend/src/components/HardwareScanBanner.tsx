import React from 'react';
import { Download, Terminal, Upload, Shield, ShieldCheck, Lock, FileCode } from 'lucide-react';
import type { SystemHardwareSnapshot } from '../types';

interface HardwareScanBannerProps {
  onHardwareImported: (hw: SystemHardwareSnapshot) => void;
  isImported: boolean;
  machineName?: string;
}

export const HardwareScanBanner: React.FC<HardwareScanBannerProps> = ({
  onHardwareImported,
  isImported,
  machineName,
}) => {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const json = JSON.parse(event.target?.result as string);
        if (json && (json.device_model || json.cpu)) {
          onHardwareImported(json);
        } else {
          alert('Invalid hardware snapshot JSON file format.');
        }
      } catch (err) {
        alert('Could not parse JSON file.');
      }
    };
    reader.readAsText(file);
  };

  if (isImported) {
    return (
      <div className="glass-panel" style={{
        padding: '1rem 1.5rem',
        marginBottom: '1.25rem',
        background: 'rgba(16, 185, 129, 0.08)',
        border: '1px solid rgba(16, 185, 129, 0.35)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <ShieldCheck size={22} color="#10b981" />
          <div>
            <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#10b981' }}>
              VERIFIED OS & FIRMWARE TELEMETRY ACTIVE
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Viewing native SMBIOS, CPU topology, storage, and battery metrics for <b>{machineName || 'Host Device'}</b>.
            </div>
          </div>
        </div>

        <button
          onClick={() => {
            window.location.hash = '';
            window.location.reload();
          }}
          className="btn-secondary"
          style={{ fontSize: '0.75rem', padding: '0.35rem 0.75rem' }}
        >
          Reset to Browser View
        </button>
      </div>
    );
  }

  return (
    <div className="glass-panel" style={{
      padding: '1.25rem 1.5rem',
      marginBottom: '1.25rem',
      border: '1px solid var(--border-focus)',
      background: 'linear-gradient(180deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%)'
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.85rem', marginBottom: '1rem' }}>
        <Shield size={22} color="var(--primary)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div>
          <h3 style={{ fontSize: '0.96rem', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 0.25rem 0' }}>
            Inspect Real Firmware, Hybrid Core Topology & Battery Health
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.45 }}>
            Web browsers are sandboxed for security — JavaScript cannot inspect physical BIOS tables, NVMe SMART health, thermal sensors, or battery cycle counts.
            Use our <b>inspectable, read-only standalone collectors</b> to read direct OS & firmware telemetry locally without admin rights:
          </p>
        </div>
      </div>

      {/* 3 Inspectable Methods */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '0.85rem'
      }}>
        {/* Method 1: Windows Collector */}
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-card)',
          borderRadius: '10px',
          padding: '0.85rem 1rem',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.45rem', color: 'var(--primary)' }}>
              <Terminal size={16} />
              <span style={{ fontSize: '0.82rem', fontWeight: 700 }}>Option A: Windows Native Collector</span>
            </div>
            <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginBottom: '0.65rem' }}>
              Download our transparent PowerShell script or portable launcher. Open and inspect source before running:
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <a
              href="/scan.ps1"
              download="scan.ps1"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.35rem',
                padding: '0.35rem 0.75rem',
                borderRadius: '6px',
                fontSize: '0.74rem',
                fontWeight: 600,
                color: 'var(--text-main)',
                background: 'var(--bg-card-sub)',
                border: '1px solid var(--border-card)',
                textDecoration: 'none'
              }}
            >
              <FileCode size={13} color="var(--primary)" />
              <span>Inspect scan.ps1</span>
            </a>

            <a
              href="/LaptopCheck_Windows.bat"
              download="LaptopCheck_Windows.bat"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.35rem',
                padding: '0.35rem 0.75rem',
                borderRadius: '6px',
                fontSize: '0.74rem',
                fontWeight: 700,
                color: '#fff',
                background: 'var(--primary)',
                textDecoration: 'none'
              }}
            >
              <Download size={13} />
              <span>Download .bat</span>
            </a>
          </div>
        </div>

        {/* Method 2: Linux Collector */}
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-card)',
          borderRadius: '10px',
          padding: '0.85rem 1rem',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.45rem', color: '#10b981' }}>
              <Download size={16} />
              <span style={{ fontSize: '0.82rem', fontWeight: 700 }}>Option B: Linux Native Collector</span>
            </div>
            <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginBottom: '0.65rem' }}>
              Standalone shell script for Ubuntu, Debian, Fedora, Arch. Reads <code>sysfs</code> and <code>lscpu</code> without root:
            </p>
          </div>

          <a
            href="/scan.sh"
            download="scan.sh"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.45rem',
              padding: '0.42rem 0.85rem',
              borderRadius: '7px',
              fontSize: '0.75rem',
              fontWeight: 700,
              color: '#ffffff',
              background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
              textDecoration: 'none'
            }}
          >
            <Download size={13} />
            <span>Download scan.sh</span>
          </a>
        </div>

        {/* Method 3: Upload Scanned JSON */}
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-card)',
          borderRadius: '10px',
          padding: '0.85rem 1rem',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.45rem', color: 'var(--accent)' }}>
              <Upload size={16} />
              <span style={{ fontSize: '0.82rem', fontWeight: 700 }}>Option C: Upload JSON Report</span>
            </div>
            <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginBottom: '0.65rem' }}>
              Already generated <code>laptop_specs.json</code>? Upload it here for offline evaluation:
            </p>
          </div>

          <label style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.45rem',
            padding: '0.42rem 0.85rem',
            borderRadius: '7px',
            fontSize: '0.75rem',
            fontWeight: 700,
            color: 'var(--text-main)',
            background: 'var(--bg-card-sub)',
            border: '1px solid var(--border-card)',
            cursor: 'pointer'
          }}>
            <Upload size={13} />
            <span>Select JSON File</span>
            <input
              type="file"
              accept=".json"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
          </label>
        </div>
      </div>

      {/* Trust & Privacy Notice */}
      <div style={{
        marginTop: '0.85rem',
        padding: '0.55rem 0.85rem',
        borderRadius: '7px',
        background: 'rgba(15, 23, 42, 0.4)',
        border: '1px solid var(--border-card)',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        fontSize: '0.72rem',
        color: 'var(--text-muted)'
      }}>
        <Lock size={14} color="var(--primary)" style={{ flexShrink: 0 }} />
        <span>
          <b>Safe & Private by Default:</b> All collector scripts run read-only with standard user rights (never requests administrator or root).
          Serial numbers and hostnames are redacted by default. Zero automated background network uploads.
        </span>
      </div>
    </div>
  );
};
