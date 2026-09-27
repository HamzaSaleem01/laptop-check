import React, { useState } from 'react';
import type { SystemHardwareSnapshot, FieldProvenance } from '../types';
import { Cpu, HardDrive, Battery, Layers, ChevronDown, ChevronUp, Monitor, Info, Download, ShieldCheck } from 'lucide-react';

interface HardwareSpecsCardProps {
  hardware: SystemHardwareSnapshot | null;
  loading: boolean;
}

export const HardwareSpecsCard: React.FC<HardwareSpecsCardProps> = ({ hardware, loading }) => {
  const [technicalView, setTechnicalView] = useState(false);

  if (loading) {
    return (
      <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', marginBottom: '1.5rem' }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Probing host laptop hardware sensors & WebGL graphics...</p>
      </div>
    );
  }

  if (!hardware) {
    return (
      <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', marginBottom: '1.5rem' }}>
        <p style={{ color: 'var(--status-caution)', fontSize: '0.9rem' }}>No hardware information available.</p>
      </div>
    );
  }

  const { cpu, ram, storage, battery, os, gpus, provenance } = hardware;
  const isSim = hardware.is_simulation;
  const isBrowserMode = !isSim && (!provenance || Object.values(provenance).some(p => p.source.startsWith('browser:')));

  // Helper for provenance badge
  const renderProvBadge = (key: string, defaultSource = 'OS/Hardware') => {
    const prov: FieldProvenance | undefined = provenance ? provenance[key] : undefined;
    if (!prov) {
      return (
        <span style={{ fontSize: '0.65rem', padding: '0.1rem 0.35rem', borderRadius: '4px', background: 'var(--bg-card)', color: 'var(--text-dim)', border: '1px solid var(--border-card)' }}>
          {defaultSource}
        </span>
      );
    }

    if (prov.status === 'simulated') {
      return (
        <span style={{ fontSize: '0.65rem', padding: '0.1rem 0.35rem', borderRadius: '4px', background: 'rgba(168, 85, 247, 0.15)', color: '#a855f7', border: '1px solid rgba(168, 85, 247, 0.3)' }}>
          Synthetic Example
        </span>
      );
    }

    if (prov.status === 'unavailable' || prov.confidence === 'unavailable') {
      return (
        <span style={{ fontSize: '0.65rem', padding: '0.1rem 0.35rem', borderRadius: '4px', background: 'rgba(239, 68, 68, 0.12)', color: '#ef4444', border: '1px solid rgba(239, 68, 68, 0.25)' }}>
          Unavailable
        </span>
      );
    }

    if (prov.source.startsWith('browser:')) {
      return (
        <span style={{ fontSize: '0.65rem', padding: '0.1rem 0.35rem', borderRadius: '4px', background: 'rgba(245, 158, 11, 0.12)', color: '#f59e0b', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
          Browser Estimate
        </span>
      );
    }

    return (
      <span style={{ fontSize: '0.65rem', padding: '0.1rem 0.35rem', borderRadius: '4px', background: 'rgba(16, 185, 129, 0.12)', color: '#10b981', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
        {prov.status === 'measured' ? 'OS Measured' : 'Firmware Reported'}
      </span>
    );
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
      
      {/* Dynamic Status Notification Banner */}
      {isSim ? (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.6rem',
          background: 'rgba(245, 158, 11, 0.08)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          borderRadius: '10px',
          padding: '0.65rem 1rem',
          marginBottom: '1.25rem'
        }}>
          <Info size={18} color="#f59e0b" style={{ flexShrink: 0 }} />
          <div style={{ flex: 1 }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#f59e0b' }}>
              SYNTHETIC DEMONSTRATION PROFILE: {hardware.simulation_profile_name || 'Standard Preset'}
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: '0.5rem' }}>
              Reference hardware specs used for safe baseline comparison. All metrics are synthetic examples.
            </span>
          </div>
        </div>
      ) : isBrowserMode ? (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '0.75rem',
          background: 'rgba(59, 130, 246, 0.08)',
          border: '1px solid rgba(59, 130, 246, 0.25)',
          borderRadius: '10px',
          padding: '0.65rem 1rem',
          marginBottom: '1.25rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Info size={18} color="#3b82f6" style={{ flexShrink: 0 }} />
            <div>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#3b82f6' }}>
                BROWSER-LEVEL DEVICE INSPECTION ACTIVE
              </span>
              <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)', margin: 0 }}>
                Displaying genuine WebGL GPU, threads, and platform facts. Low-level sensors (temperature, SMART wear, battery cycles) are sandboxed.
              </p>
            </div>
          </div>
          <a
            href="/scan.ps1"
            download="scan.ps1"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-card)',
              color: 'var(--text-main)',
              padding: '0.3rem 0.65rem',
              borderRadius: '6px',
              fontSize: '0.74rem',
              fontWeight: 600,
              textDecoration: 'none'
            }}
            title="Download standalone collector for deep BIOS, SMART & thermal telemetry"
          >
            <Download size={13} color="var(--primary)" />
            <span>Download Collector</span>
          </a>
        </div>
      ) : (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.6rem',
          background: 'rgba(16, 185, 129, 0.08)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          borderRadius: '10px',
          padding: '0.65rem 1rem',
          marginBottom: '1.25rem'
        }}>
          <ShieldCheck size={18} color="#10b981" style={{ flexShrink: 0 }} />
          <div style={{ flex: 1 }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#10b981' }}>
              DIRECT OS & FIRMWARE TELEMETRY ACTIVE
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: '0.5rem' }}>
              Verified SMBIOS topology, hardware sensors, and kernel diagnostics.
            </span>
          </div>
        </div>
      )}

      {/* Header bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--accent)', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
            {isSim ? 'Demonstration Profile' : (isBrowserMode ? 'Host Device (Browser Probed)' : 'Verified Physical Machine')}
          </span>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '0.1rem' }}>
            {hardware.manufacturer} {hardware.device_model}
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            {os.system} {os.release} • {os.architecture} {os.kernel ? `(${os.kernel})` : ''}
            {hardware.is_redacted && <span style={{ marginLeft: '0.5rem', color: 'var(--primary)', fontWeight: 600 }}>• [Redacted for Privacy]</span>}
          </p>
        </div>

        <button
          onClick={() => setTechnicalView(!technicalView)}
          className="btn-secondary"
          style={{ padding: '0.45rem 0.85rem', fontSize: '0.8rem' }}
        >
          {technicalView ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
          {technicalView ? 'Simplified View' : 'Technical & Provenance Evidence'}
        </button>
      </div>

      {/* Grid of hardware pillars */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '1rem'
      }}>
        {/* CPU */}
        <div className="spec-subcard">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary)' }}>
              <Cpu size={18} />
              <span style={{ fontWeight: 700, fontSize: '0.88rem' }}>Processor</span>
            </div>
            {renderProvBadge('cpu.model', 'CPU Model')}
          </div>
          <div style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.2rem' }}>
            {cpu.model}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {cpu.p_cores !== undefined && cpu.e_cores !== undefined ? (
              <span>{cpu.p_cores} P-cores + {cpu.e_cores} E-cores ({cpu.threads_logical} Threads)</span>
            ) : (
              <span>{cpu.cores_physical ?? '?'} Cores • {cpu.threads_logical ?? '?'} Threads</span>
            )}
            {cpu.temperature_c !== undefined ? ` • ${cpu.temperature_c}°C` : (isBrowserMode ? ' • Temp: Sandbox limited' : '')}
          </div>
          {technicalView && (
            <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border-card)', fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
              <div>Base: {cpu.base_freq_mhz || 'N/A'} MHz | Max: {cpu.max_freq_mhz || 'N/A'} MHz</div>
              <div>Caches: L1d: {cpu.cache_l1d_kb ? `${cpu.cache_l1d_kb} KB` : 'N/A'} | L2: {cpu.cache_l2_kb ? `${cpu.cache_l2_kb} KB` : 'N/A'} | L3: {cpu.cache_l3_kb ? `${cpu.cache_l3_kb} KB` : 'N/A'}</div>
              <div>Instructions: {cpu.instruction_sets.slice(0, 6).join(', ') || 'Standard ISA'}</div>
            </div>
          )}
        </div>

        {/* Graphics (GPU) */}
        <div className="spec-subcard">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#8b5cf6' }}>
              <Monitor size={18} />
              <span style={{ fontWeight: 700, fontSize: '0.88rem' }}>Graphics (GPU)</span>
            </div>
            {renderProvBadge('gpu.0.name', 'GPU')}
          </div>
          <div style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.2rem' }}>
            {gpus && gpus.length > 0 ? gpus[0].name : 'Graphics Adapter'}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {gpus && gpus[0]?.is_dedicated ? 'Dedicated GPU' : 'Integrated Graphics'} • {gpus && gpus[0]?.vendor ? gpus[0].vendor : 'Active'}
          </div>
          {technicalView && gpus && gpus.length > 0 && (
            <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border-card)', fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
              <div>Driver: {gpus[0].driver_version || 'Active Driver'}</div>
              <div>Memory: {gpus[0].vram_mb ? `${gpus[0].vram_mb} MB Dedicated` : 'Dynamic Shared System RAM'}</div>
              <div>Compute APIs: {gpus[0].compute_apis && gpus[0].compute_apis.length > 0 ? gpus[0].compute_apis.join(', ') : 'Vulkan/OpenGL'}</div>
            </div>
          )}
        </div>

        {/* RAM */}
        <div className="spec-subcard">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent)' }}>
              <Layers size={18} />
              <span style={{ fontWeight: 700, fontSize: '0.88rem' }}>Memory (RAM)</span>
            </div>
            {renderProvBadge('memory.total_usable_gb', 'Memory')}
          </div>
          <div style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.2rem' }}>
            {ram.total_gb.toFixed(1)} GB {ram.memory_type !== 'Not available' && !ram.memory_type.includes('Unavailable') ? ram.memory_type : ''}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {ram.channels !== 'Not available' && !ram.channels.includes('Unavailable') ? `${ram.channels} • ` : ''}
            {ram.available_gb > 0 ? `${ram.available_gb.toFixed(1)} GB available` : 'Usable OS capacity'}
          </div>
          {technicalView && (
            <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border-card)', fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
              <div>Used: {ram.used_gb.toFixed(1)} GB / {ram.total_gb.toFixed(1)} GB</div>
              <div>Channels: {ram.channels}</div>
              <div>Type: {ram.memory_type}</div>
            </div>
          )}
        </div>

        {/* Storage */}
        <div className="spec-subcard">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--status-pass)' }}>
              <HardDrive size={18} />
              <span style={{ fontWeight: 700, fontSize: '0.88rem' }}>Storage Disk</span>
            </div>
            {renderProvBadge('storage.0.smart_status', 'Storage')}
          </div>
          <div style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.2rem' }}>
            {storage[0]?.model || 'Storage Device'}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {storage[0]?.capacity_gb ? `${storage[0].capacity_gb} GB` : 'Capacity unverified'} • {storage[0]?.media_type}
          </div>
          {technicalView && (
            <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border-card)', fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
              <div>SMART Status: {storage[0]?.smart_status}</div>
              {storage[0]?.temperature_c && <div>Drive Temp: {storage[0]?.temperature_c}°C</div>}
              {storage[0]?.smart_limitations && storage[0]?.smart_limitations.length > 0 && (
                <div style={{ color: 'var(--status-caution)' }}>Note: {storage[0].smart_limitations[0]}</div>
              )}
            </div>
          )}
        </div>

        {/* Battery */}
        <div className="spec-subcard">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--status-caution)' }}>
              <Battery size={18} />
              <span style={{ fontWeight: 700, fontSize: '0.88rem' }}>Battery Condition</span>
            </div>
            {renderProvBadge('battery.health_pct', 'Battery')}
          </div>
          <div style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.2rem' }}>
            {battery.present ? (
              battery.health_pct !== undefined ? (
                `Health: ${battery.health_pct}% (${battery.category})`
              ) : (
                `Charge: ${battery.is_charging ? 'Charging' : 'Present'} (Wear Unspecified)`
              )
            ) : (
              'No Physical Battery'
            )}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {battery.present ? (
              <>
                {battery.cycle_count ? `${battery.cycle_count} cycles • ` : ''}
                {battery.power_w ? `${battery.power_w}W draw • ` : ''}
                {battery.ac_connected ? 'AC Connected' : 'On Battery'}
              </>
            ) : (
              'Desktop / Server System'
            )}
          </div>
          {technicalView && battery.present && (
            <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border-card)', fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
              <div>Full Charge: {battery.full_charge_capacity_mwh ? `${Math.round(battery.full_charge_capacity_mwh)} mWh` : 'N/A'}</div>
              <div>Design: {battery.design_capacity_mwh ? `${Math.round(battery.design_capacity_mwh)} mWh` : 'N/A'}</div>
              {battery.wear_pct !== undefined && <div>Estimated Degradation: {battery.wear_pct}%</div>}
            </div>
          )}
        </div>
      </div>

      {/* Technical View: Complete Provenance Trail Table */}
      {technicalView && provenance && Object.keys(provenance).length > 0 && (
        <div style={{ marginTop: '1.25rem', paddingTop: '1.25rem', borderTop: '1px solid var(--border-card)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.75rem' }}>
            <ShieldCheck size={16} color="var(--primary)" />
            <h4 style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
              Hardware Telemetry Provenance Trail (Audit Evidence)
            </h4>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.74rem' }}>
              <thead>
                <tr style={{ background: 'var(--bg-card-sub)', color: 'var(--text-dim)', textAlign: 'left' }}>
                  <th style={{ padding: '0.45rem 0.65rem' }}>Field Key</th>
                  <th style={{ padding: '0.45rem 0.65rem' }}>Reported Value</th>
                  <th style={{ padding: '0.45rem 0.65rem' }}>Source Interface</th>
                  <th style={{ padding: '0.45rem 0.65rem' }}>Collection Method</th>
                  <th style={{ padding: '0.45rem 0.65rem' }}>Status</th>
                  <th style={{ padding: '0.45rem 0.65rem' }}>Limitations</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(provenance).map(([k, p]) => (
                  <tr key={k} style={{ borderBottom: '1px solid var(--border-card)' }}>
                    <td style={{ padding: '0.4rem 0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-main)' }}>{k}</td>
                    <td style={{ padding: '0.4rem 0.65rem', color: 'var(--text-main)', fontWeight: 600 }}>
                      {p.value !== null && p.value !== undefined ? String(p.value) : 'Not available'} {p.unit}
                    </td>
                    <td style={{ padding: '0.4rem 0.65rem', color: 'var(--text-muted)' }}>{p.source}</td>
                    <td style={{ padding: '0.4rem 0.65rem', color: 'var(--text-dim)' }}>{p.method}</td>
                    <td style={{ padding: '0.4rem 0.65rem' }}>{renderProvBadge(k)}</td>
                    <td style={{ padding: '0.4rem 0.65rem', color: 'var(--text-dim)', maxWidth: '240px' }}>
                      {p.limitations && p.limitations.length > 0 ? p.limitations.join('; ') : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
