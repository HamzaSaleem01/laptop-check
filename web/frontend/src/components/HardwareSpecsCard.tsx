import React, { useState } from 'react';
import type { SystemHardwareSnapshot } from '../types';
import { Cpu, HardDrive, Battery, Layers, ChevronDown, ChevronUp } from 'lucide-react';

interface HardwareSpecsCardProps {
  hardware: SystemHardwareSnapshot | null;
  loading: boolean;
}

export const HardwareSpecsCard: React.FC<HardwareSpecsCardProps> = ({ hardware, loading }) => {
  const [technicalView, setTechnicalView] = useState(false);

  if (loading) {
    return (
      <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', marginBottom: '1.5rem' }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Probing system hardware sensors...</p>
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

  const { cpu, ram, storage, battery, os } = hardware;

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
      {/* Header bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--accent)', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
            System Under Diagnostic Inspection
          </span>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '0.1rem' }}>
            {hardware.manufacturer} {hardware.device_model}
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            {os.system} {os.release} • {os.architecture} {os.kernel ? `(${os.kernel})` : ''}
          </p>
        </div>

        <button
          onClick={() => setTechnicalView(!technicalView)}
          className="btn-secondary"
          style={{ padding: '0.45rem 0.85rem', fontSize: '0.8rem' }}
        >
          {technicalView ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
          {technicalView ? 'Simplified View' : 'Technical Specifications'}
        </button>
      </div>

      {/* Grid of hardware pillars */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '1rem'
      }}>
        {/* CPU */}
        <div className="spec-subcard">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem', color: 'var(--primary)' }}>
            <Cpu size={18} />
            <span style={{ fontWeight: 700, fontSize: '0.88rem' }}>Processor</span>
          </div>
          <div style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.2rem' }}>
            {cpu.model}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {cpu.cores_physical ?? '?'} Cores • {cpu.threads_logical ?? '?'} Threads
            {cpu.temperature_c ? ` • ${cpu.temperature_c}°C` : ''}
          </div>
          {technicalView && (
            <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border-card)', fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
              <div>Base: {cpu.base_freq_mhz || 'N/A'} MHz | Max: {cpu.max_freq_mhz || 'N/A'} MHz</div>
              <div>Instructions: {cpu.instruction_sets.slice(0, 8).join(', ') || 'x86_64'}</div>
            </div>
          )}
        </div>

        {/* RAM */}
        <div className="spec-subcard">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem', color: 'var(--accent)' }}>
            <Layers size={18} />
            <span style={{ fontWeight: 700, fontSize: '0.88rem' }}>Memory (RAM)</span>
          </div>
          <div style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.2rem' }}>
            {ram.total_gb.toFixed(1)} GB {ram.memory_type}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {ram.channels} • {ram.available_gb.toFixed(1)} GB available
          </div>
          {technicalView && (
            <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border-card)', fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
              <div>Used: {ram.used_gb.toFixed(1)} GB / {ram.total_gb.toFixed(1)} GB</div>
              <div>Speed: {ram.speed_mhz ? `${ram.speed_mhz} MHz` : 'Standard'}</div>
            </div>
          )}
        </div>

        {/* Storage */}
        <div className="spec-subcard">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem', color: 'var(--status-pass)' }}>
            <HardDrive size={18} />
            <span style={{ fontWeight: 700, fontSize: '0.88rem' }}>Storage Disk</span>
          </div>
          <div style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.2rem' }}>
            {storage[0]?.model || 'System Drive'}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {storage[0]?.capacity_gb} GB • {storage[0]?.media_type}
          </div>
          {technicalView && (
            <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border-card)', fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
              <div>SMART Health: {storage[0]?.smart_status}</div>
              {storage[0]?.temperature_c && <div>Drive Temp: {storage[0]?.temperature_c}°C</div>}
            </div>
          )}
        </div>

        {/* Battery */}
        <div className="spec-subcard">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem', color: 'var(--status-caution)' }}>
            <Battery size={18} />
            <span style={{ fontWeight: 700, fontSize: '0.88rem' }}>Battery State</span>
          </div>
          <div style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.2rem' }}>
            {battery.present ? `${battery.health_pct ?? 'N/A'}% Health` : 'No Battery / Desktop'}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {battery.category} {battery.cycle_count ? `• ${battery.cycle_count} cycles` : ''}
          </div>
          {technicalView && battery.present && (
            <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border-card)', fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
              <div>Full: {battery.full_charge_capacity_mwh ? `${Math.round(battery.full_charge_capacity_mwh / 1000)} Wh` : 'N/A'} / Design: {battery.design_capacity_mwh ? `${Math.round(battery.design_capacity_mwh / 1000)} Wh` : 'N/A'}</div>
              <div>Power: {battery.ac_connected ? 'AC Connected (Charging/Wall)' : 'Discharging on Battery'}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
