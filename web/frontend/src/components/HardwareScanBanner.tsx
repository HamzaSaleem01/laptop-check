import React, { useState } from 'react';
import { Download, Terminal, Upload, Check, Copy, AlertTriangle, ShieldCheck } from 'lucide-react';
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
  const [copied, setCopied] = useState(false);
  const psCommand = 'powershell -c "irm https://laptopcheck.vercel.app/scan.ps1 | iex"';

  const copyToClipboard = () => {
    navigator.clipboard.writeText(psCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const json = JSON.parse(event.target?.result as string);
        if (json && json.device_model) {
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
        background: 'rgba(16, 185, 129, 0.1)',
        border: '1px solid rgba(16, 185, 129, 0.4)',
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
              100% GENUINE HARDWARE IMPORTED
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Viewing verified motherboard, SSD, CPU, and battery data for <b>{machineName || 'Host Laptop'}</b>.
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
        <AlertTriangle size={22} color="#f59e0b" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div>
          <h3 style={{ fontSize: '0.96rem', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 0.25rem 0' }}>
            Want 100% Genuine Specs for THIS Specific Laptop?
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.45 }}>
            Web browsers are sandboxed for security — websites <b>cannot</b> access physical BIOS serials, NVMe SSD health, or battery cycle counts directly through JavaScript.
            Run the instant scanner below on this machine to read <b>exact hardware</b> in 3 seconds:
          </p>
        </div>
      </div>

      {/* 3 Instant Methods */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '0.85rem'
      }}>
        {/* Method 1: 1-Liner PowerShell Command */}
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-card)',
          borderRadius: '10px',
          padding: '0.85rem 1rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.45rem', color: 'var(--primary)' }}>
            <Terminal size={16} />
            <span style={{ fontSize: '0.82rem', fontWeight: 700 }}>Option A: Instant Windows 1-Liner</span>
          </div>
          <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
            Open Windows <b>PowerShell</b> and paste this (reads exact model, SSD, battery & auto-opens here):
          </p>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            background: 'var(--bg-app)',
            borderRadius: '6px',
            padding: '0.3rem 0.5rem',
            border: '1px solid var(--border-card)'
          }}>
            <code style={{ fontSize: '0.72rem', color: 'var(--accent)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontFamily: 'var(--font-mono)' }}>
              irm https://laptopcheck.vercel.app/scan.ps1 | iex
            </code>
            <button
              onClick={copyToClipboard}
              style={{
                background: copied ? 'var(--status-pass)' : 'var(--primary)',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                padding: '0.25rem 0.55rem',
                fontSize: '0.7rem',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem',
                marginLeft: '0.4rem'
              }}
              title="Copy to clipboard"
            >
              {copied ? <Check size={12} /> : <Copy size={12} />}
              <span>{copied ? 'Copied!' : 'Copy'}</span>
            </button>
          </div>
        </div>

        {/* Method 2: Portable .bat Download */}
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
              <span style={{ fontSize: '0.82rem', fontWeight: 700 }}>Option B: Zero-Install .bat Tool</span>
            </div>
            <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginBottom: '0.65rem' }}>
              Download our standalone batch script, double click it on any shop or friend's laptop (no installation needed):
            </p>
          </div>

          <a
            href="/LaptopCheck_Windows.bat"
            download="LaptopCheck_Windows.bat"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.45rem',
              padding: '0.45rem 1rem',
              borderRadius: '7px',
              fontSize: '0.78rem',
              fontWeight: 700,
              color: '#ffffff',
              background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
              textDecoration: 'none',
              boxShadow: '0 2px 8px rgba(5, 150, 105, 0.3)'
            }}
          >
            <Download size={14} />
            <span>Download LaptopCheck_Windows.bat</span>
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
              <span style={{ fontSize: '0.82rem', fontWeight: 700 }}>Option C: Upload Saved Scan</span>
            </div>
            <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginBottom: '0.65rem' }}>
              Already ran the scanner and saved <code>laptop_specs.json</code>? Upload it here to view the diagnostic dashboard:
            </p>
          </div>

          <label style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.45rem',
            padding: '0.45rem 1rem',
            borderRadius: '7px',
            fontSize: '0.78rem',
            fontWeight: 700,
            color: 'var(--text-main)',
            background: 'var(--bg-card)',
            border: '1px solid var(--border-card)',
            cursor: 'pointer'
          }}>
            <Upload size={14} />
            <span>Select laptop_specs.json</span>
            <input
              type="file"
              accept=".json"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
          </label>
        </div>
      </div>
    </div>
  );
};
