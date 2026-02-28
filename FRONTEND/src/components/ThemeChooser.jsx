import React from 'react';
import { useTheme } from '../context/ThemeContext';

const ThemeChooser = () => {
  const { theme, setTheme, setShowChooser } = useTheme();

  const choose = (t) => {
    setTheme(t);
    setShowChooser(false);
  };

  return (
    <div style={overlayStyle}>
      <div style={modalStyle}>
        <h2 style={{ marginTop: 0 }}>Choose a theme</h2>
        <p style={{ color: '#374151' }}>Pick Light or Dark mode for the app.</p>
        <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
          <button onClick={() => choose('light')} style={buttonStyle}>🌤️ Light</button>
          <button onClick={() => choose('dark')} style={{ ...buttonStyle, background: '#111827', color: '#fff' }}>🌙 Dark</button>
        </div>
      </div>
    </div>
  );
};

const overlayStyle = {
  position: 'fixed',
  inset: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: 'rgba(0,0,0,0.35)',
  zIndex: 9999
};

const modalStyle = {
  background: '#ffffff',
  padding: 24,
  borderRadius: 12,
  width: 360,
  boxShadow: '0 8px 30px rgba(16,24,40,0.12)'
};

const buttonStyle = {
  padding: '10px 16px',
  borderRadius: 8,
  border: '1px solid rgba(0,0,0,0.08)',
  background: '#f3f4f6',
  cursor: 'pointer'
};

export default ThemeChooser;
