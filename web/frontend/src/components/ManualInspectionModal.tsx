import React, { useState, useEffect } from 'react';
import { Monitor, Keyboard, MousePointer, Usb, RotateCcw, Maximize2 } from 'lucide-react';
import type { StatusEnum } from '../types';

export const ManualInspectionSection: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'screen' | 'keyboard' | 'touchpad' | 'ports'>('screen');

  // Screen Test State
  const [isFullscreenScreen, setIsFullscreenScreen] = useState(false);
  const screenColors = ['#000000', '#ffffff', '#ef4444', '#10b981', '#3b82f6', '#6b7280'];
  const [colorIndex, setColorIndex] = useState(0);

  // Keyboard Tester State
  const [pressedKeys, setPressedKeys] = useState<Set<string>>(new Set());

  // Touchpad State
  const [touchpadClicks, setTouchpadClicks] = useState({ left: 0, right: 0 });
  const [touchpadMovement, setTouchpadMovement] = useState({ x: 0, y: 0 });

  // Ports Checklist State
  const [portsStatus, setPortsStatus] = useState<Record<string, StatusEnum>>({
    'USB-A Port 1': 'PASS',
    'USB-A Port 2': 'PASS',
    'USB-C / Thunderbolt': 'PASS',
    'HDMI Video Output': 'PASS',
    'Audio Jack 3.5mm': 'PASS',
    'SD Card Reader': 'NOT TESTED',
    'Ethernet RJ-45': 'NOT TESTED'
  });

  // Keyboard event listener
  useEffect(() => {
    if (activeSubTab !== 'keyboard') return;

    const handleKeyDown = (e: KeyboardEvent) => {
      e.preventDefault();
      const code = e.code.replace('Key', '').replace('Digit', '');
      setPressedKeys(prev => new Set(prev).add(code));
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeSubTab]);

  const keyboardRows = [
    ['Escape', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'Delete'],
    ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
    ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
    ['CapsLock', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'", 'Enter'],
    ['ShiftLeft', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'ShiftRight'],
    ['ControlLeft', 'AltLeft', 'Space', 'AltRight', 'ControlRight', 'ArrowLeft', 'ArrowUp', 'ArrowDown', 'ArrowRight']
  ];

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--accent)', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
            Shop Floor Physical Verification
          </span>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '0.1rem' }}>
            Manual Hardware Inspection
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Inspect physical components that cannot be fully diagnosed electronically.
          </p>
        </div>

        {/* Sub-tab pills */}
        <div style={{
          display: 'flex',
          gap: '0.35rem',
          background: 'var(--bg-nav)',
          padding: '0.3rem',
          borderRadius: '9px',
          border: '1px solid var(--border-card)'
        }}>
          {[
            { id: 'screen', label: 'Display Panel', icon: <Monitor size={14} /> },
            { id: 'keyboard', label: 'Keyboard Tester', icon: <Keyboard size={14} /> },
            { id: 'touchpad', label: 'Touchpad', icon: <MousePointer size={14} /> },
            { id: 'ports', label: 'Physical Ports', icon: <Usb size={14} /> }
          ].map(tab => {
            const isActive = activeSubTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveSubTab(tab.id as any)}
                style={{
                  background: isActive ? 'var(--primary)' : 'transparent',
                  color: isActive ? '#ffffff' : 'var(--text-muted)',
                  border: 'none',
                  padding: '0.4rem 0.75rem',
                  borderRadius: '7px',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  transition: 'all 0.15s ease'
                }}
              >
                {tab.icon} {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* 1. SCREEN TEST */}
      {activeSubTab === 'screen' && (
        <div>
          <div className="spec-subcard" style={{ marginBottom: '1rem', padding: '1.25rem' }}>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.35rem' }}>
              Dead Pixel & Backlight Bleed Inspection
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '1rem', lineHeight: '1.4' }}>
              Cycle through solid full-screen colors (Black, White, Red, Green, Blue, Gray) to check for stuck/dead sub-pixels, vertical/horizontal lines, flickering, or edge bleeding.
            </p>

            <button
              onClick={() => {
                setColorIndex(0);
                setIsFullscreenScreen(true);
              }}
              className="btn-primary"
            >
              <Maximize2 size={16} /> Launch Fullscreen Color Cycler
            </button>
          </div>

          {/* Fullscreen Overlay */}
          {isFullscreenScreen && (
            <div
              onClick={() => {
                if (colorIndex < screenColors.length - 1) {
                  setColorIndex(colorIndex + 1);
                } else {
                  setIsFullscreenScreen(false);
                }
              }}
              style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: '100vw',
                height: '100vh',
                backgroundColor: screenColors[colorIndex],
                zIndex: 99999,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                userSelect: 'none'
              }}
            >
              <div style={{
                background: 'rgba(0, 0, 0, 0.75)',
                color: '#ffffff',
                padding: '0.75rem 1.25rem',
                borderRadius: '8px',
                fontSize: '0.85rem',
                fontWeight: 600,
                pointerEvents: 'none',
                boxShadow: '0 4px 16px rgba(0,0,0,0.5)'
              }}>
                Color {colorIndex + 1} of {screenColors.length} — Click anywhere to cycle or exit
              </div>
            </div>
          )}
        </div>
      )}

      {/* 2. KEYBOARD TESTER */}
      {activeSubTab === 'keyboard' && (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Press keys on the physical laptop keyboard. Tested keys turn green to verify input matrix.
            </p>
            <button
              onClick={() => setPressedKeys(new Set())}
              className="btn-secondary"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
            >
              <RotateCcw size={13} /> Reset Pressed Keys
            </button>
          </div>

          <div className="spec-subcard" style={{
            padding: '1.25rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.4rem',
            alignItems: 'center',
            overflowX: 'auto'
          }}>
            {keyboardRows.map((row, rIdx) => (
              <div key={rIdx} style={{ display: 'flex', gap: '0.35rem' }}>
                {row.map(k => {
                  const isPressed = pressedKeys.has(k.toUpperCase()) || pressedKeys.has(k);
                  return (
                    <div
                      key={k}
                      className={`kb-key ${isPressed ? 'pressed' : ''}`}
                      style={{
                        minWidth: k.length > 3 ? '65px' : '40px',
                        fontSize: k.length > 4 ? '0.68rem' : '0.8rem'
                      }}
                    >
                      {k.replace('Left', '').replace('Right', '')}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3. TOUCHPAD TEST */}
      {activeSubTab === 'touchpad' && (
        <div className="spec-subcard" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.35rem' }}>
            Touchpad & Gesture Test Zone
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Move cursor, click left, click right, and test inside this trackpad box to verify responsiveness.
          </p>

          <div
            onMouseMove={(e) => setTouchpadMovement({ x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY })}
            onMouseDown={(e) => {
              if (e.button === 0) setTouchpadClicks(prev => ({ ...prev, left: prev.left + 1 }));
              if (e.button === 2) setTouchpadClicks(prev => ({ ...prev, right: prev.right + 1 }));
            }}
            onContextMenu={(e) => e.preventDefault()}
            style={{
              height: '180px',
              border: '2px dashed var(--border-subtle)',
              borderRadius: '12px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'crosshair',
              background: 'var(--bg-card)'
            }}
          >
            <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--accent)', marginBottom: '0.25rem' }}>
              Touchpad Tracking Area
            </div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Coordinates: X: {touchpadMovement.x}px | Y: {touchpadMovement.y}px
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--status-pass)', marginTop: '0.4rem', fontWeight: 600 }}>
              Left Clicks: {touchpadClicks.left} • Right Clicks: {touchpadClicks.right}
            </div>
          </div>
        </div>
      )}

      {/* 4. PHYSICAL PORTS CHECKLIST */}
      {activeSubTab === 'ports' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '0.75rem' }}>
          {Object.entries(portsStatus).map(([portName, st]) => {
            return (
              <div
                key={portName}
                className="spec-subcard"
                style={{
                  padding: '0.85rem 1rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '0.5rem'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Usb size={16} color="var(--primary)" />
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>{portName}</span>
                </div>

                <div style={{ display: 'flex', gap: '0.25rem' }}>
                  {(['PASS', 'FAIL', 'NOT TESTED'] as StatusEnum[]).map(val => (
                    <button
                      key={val}
                      onClick={() => setPortsStatus(prev => ({ ...prev, [portName]: val }))}
                      style={{
                        background: st === val ? (val === 'PASS' ? 'var(--status-pass)' : (val === 'FAIL' ? 'var(--status-fail)' : 'var(--status-neutral)')) : 'var(--bg-card)',
                        color: st === val ? '#ffffff' : 'var(--text-muted)',
                        border: `1px solid ${st === val ? 'transparent' : 'var(--border-card)'}`,
                        borderRadius: '4px',
                        padding: '0.2rem 0.45rem',
                        fontSize: '0.68rem',
                        fontWeight: 600,
                        cursor: 'pointer'
                      }}
                    >
                      {val}
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
