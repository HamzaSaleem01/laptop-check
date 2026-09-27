import React from 'react';
import { Laptop, Download, FileText, ShieldCheck, CheckSquare, Sun, Moon } from 'lucide-react';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  theme,
  toggleTheme,
}) => {
  return (
    <header className="glass-panel" style={{ margin: '1rem auto', padding: '0.85rem 1.5rem', maxWidth: '1400px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        
        {/* Brand & Logo */}
        <div 
          onClick={() => setActiveTab('downloads')}
          style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}
        >
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
              <h1 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.01em' }}>LaptopCheck</h1>
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
              Safe Hardware Diagnostic & Workload Analyzer
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
            { id: 'downloads', label: 'Downloads & Setup', icon: <Download size={15} /> },
            { id: 'viewer', label: 'Inspect Report', icon: <FileText size={15} /> },
            { id: 'workloads', label: 'Workload Matrix', icon: <ShieldCheck size={15} /> },
            { id: 'manual', label: 'Shop Checklist', icon: <CheckSquare size={15} /> }
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
                  padding: '0.45rem 0.95rem',
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

        {/* Right Controls: Quick Download Link & Theme Switch */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          
          <button
            onClick={() => setActiveTab('downloads')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.45rem 0.85rem',
              borderRadius: '8px',
              fontSize: '0.78rem',
              fontWeight: 700,
              background: 'linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%)',
              color: '#ffffff',
              border: 'none',
              cursor: 'pointer',
              boxShadow: '0 2px 10px var(--primary-glow)'
            }}
          >
            <Download size={14} />
            <span>Get LaptopCheck</span>
          </button>

          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            className="theme-toggle-btn"
            title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Theme`}
            aria-label="Toggle theme"
            style={{
              background: 'var(--bg-input)',
              border: '1px solid var(--border-card)',
              color: 'var(--text-main)',
              padding: '0.45rem 0.8rem',
              borderRadius: '8px',
              fontSize: '0.78rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem'
            }}
          >
            {theme === 'dark' ? (
              <>
                <Sun size={14} color="#f59e0b" />
                <span>Light</span>
              </>
            ) : (
              <>
                <Moon size={14} color="var(--primary)" />
                <span>Dark</span>
              </>
            )}
          </button>
        </div>

      </div>
    </header>
  );
};
