import React from 'react';
import { Atom, Code, Sparkles, Briefcase, Check } from 'lucide-react';

interface WorkloadSelectorProps {
  selectedWorkloads: string[];
  setSelectedWorkloads: (wids: string[]) => void;
}

export const WorkloadSelector: React.FC<WorkloadSelectorProps> = ({
  selectedWorkloads,
  setSelectedWorkloads
}) => {
  const workloads = [
    {
      id: 'comp_materials_science',
      title: 'Computational Materials Science / Physics',
      badge: 'FLAGSHIP PROFILE',
      icon: <Atom size={22} color="var(--accent)" />,
      priorityBadges: ['CPU Multi-Core: VERY HIGH', 'RAM Bandwidth: VERY HIGH', 'Thermal Stability: VERY HIGH', 'Linux Support: HIGH'],
      description: 'Engineered for Density Functional Theory (DFT), Quantum ESPRESSO, ASE, VESTA, NumPy/SciPy/BLAS, and HPC job preparation.',
      softwareList: ['Quantum ESPRESSO (pw.x)', 'ASE (Atomic Simulation Environment)', 'NumPy & SciPy (BLAS/LAPACK)', 'VESTA 3D crystal structures']
    },
    {
      id: 'programming',
      title: 'Software Development & Engineering',
      badge: 'RECOMMENDED',
      icon: <Code size={22} color="var(--primary)" />,
      priorityBadges: ['RAM Capacity: VERY HIGH', 'CPU Compilation: HIGH', 'Fast NVMe: HIGH'],
      description: 'Optimized for multi-container Docker development, Rust/C++ compilation, IDEs, and local test runners.',
      softwareList: ['VS Code & JetBrains IDEs', 'Docker & Kubernetes', 'C++ / Rust compilers', 'Python / Node.js servers']
    },
    {
      id: 'ai_ml',
      title: 'AI / Machine Learning & Data Science',
      badge: 'INTENSIVE',
      icon: <Sparkles size={22} color="#ec4899" />,
      priorityBadges: ['NVIDIA CUDA VRAM: VERY HIGH', 'System RAM: HIGH', 'Thermal Budget: HIGH'],
      description: 'High-throughput matrix operations, local LLM inference (Ollama), PyTorch tensor computations.',
      softwareList: ['PyTorch / CUDA', 'Transformers / HuggingFace', 'Ollama / Local LLMs', 'Pandas data pipelines']
    },
    {
      id: 'productivity',
      title: 'General Productivity & Office',
      badge: 'STANDARD',
      icon: <Briefcase size={22} color="var(--status-pass)" />,
      priorityBadges: ['Battery Health: HIGH', 'RAM Capacity: HIGH', 'System Responsiveness: HIGH'],
      description: 'Smooth multi-tab web browsing, video conferencing, office suites, and document authoring.',
      softwareList: ['Google Chrome & Edge multi-tab', 'Microsoft 365 / LibreOffice', 'Zoom & Teams video meetings', 'PDF review']
    }
  ];

  const toggleWorkload = (id: string) => {
    if (selectedWorkloads.includes(id)) {
      if (selectedWorkloads.length > 1) {
        setSelectedWorkloads(selectedWorkloads.filter(w => w !== id));
      }
    } else {
      setSelectedWorkloads([...selectedWorkloads, id]);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
      <div style={{ marginBottom: '1.25rem' }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--accent)', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
          Workload Suitability Configuration
        </span>
        <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '0.1rem' }}>
          Target Use Cases & Workload Evaluation
        </h2>
        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          LaptopCheck evaluates hardware capabilities, memory bandwidth, and thermal stability against specialized workload profiles.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(310px, 1fr))', gap: '1rem' }}>
        {workloads.map((w) => {
          const isSelected = selectedWorkloads.includes(w.id);
          return (
            <div
              key={w.id}
              onClick={() => toggleWorkload(w.id)}
              style={{
                background: isSelected ? 'var(--primary-light)' : 'var(--bg-card-sub)',
                border: `2px solid ${isSelected ? 'var(--primary)' : 'var(--border-card)'}`,
                borderRadius: '12px',
                padding: '1.2rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                position: 'relative',
                boxShadow: isSelected ? '0 4px 16px var(--primary-glow)' : 'none'
              }}
            >
              {/* Top Row: Icon + Badge + Checkmark */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div style={{ background: 'var(--bg-card)', padding: '0.45rem', borderRadius: '9px', border: '1px solid var(--border-card)' }}>
                    {w.icon}
                  </div>
                  <span style={{
                    fontSize: '0.68rem',
                    fontWeight: 700,
                    padding: '0.18rem 0.45rem',
                    borderRadius: '5px',
                    background: isSelected ? 'var(--primary)' : 'var(--bg-card)',
                    color: isSelected ? '#ffffff' : 'var(--text-muted)',
                    border: `1px solid ${isSelected ? 'transparent' : 'var(--border-card)'}`
                  }}>
                    {w.badge}
                  </span>
                </div>

                <div style={{
                  width: '22px',
                  height: '22px',
                  borderRadius: '50%',
                  background: isSelected ? 'var(--primary)' : 'var(--bg-card)',
                  border: `1px solid ${isSelected ? 'var(--primary)' : 'var(--border-card)'}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#ffffff'
                }}>
                  {isSelected && <Check size={13} />}
                </div>
              </div>

              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.35rem' }}>
                {w.title}
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.75rem', lineHeight: '1.4' }}>
                {w.description}
              </p>

              {/* Priorities */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginBottom: '0.75rem' }}>
                {w.priorityBadges.map((badge, idx) => (
                  <span key={idx} style={{
                    fontSize: '0.68rem',
                    fontWeight: 600,
                    background: 'var(--bg-card)',
                    color: 'var(--accent)',
                    padding: '0.18rem 0.45rem',
                    borderRadius: '4px',
                    border: '1px solid var(--border-card)'
                  }}>
                    {badge}
                  </span>
                ))}
              </div>

              {/* Typical Workload Examples */}
              <div style={{ borderTop: '1px solid var(--border-card)', paddingTop: '0.55rem', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                <b style={{ color: 'var(--text-secondary)' }}>Typical Stack:</b> {w.softwareList.join(', ')}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
