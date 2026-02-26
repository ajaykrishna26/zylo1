// frontend/src/components/Header.js
import React from 'react';
import { useTheme } from '../context/ThemeContext';

const Header = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '18px 24px' }}>
      <div>
        <h1 style={{ margin: 0 }}>Dyslexia Reading Assistant</h1>
        <p style={{ margin: 0 }}>Practice reading with personalized feedback</p>
      </div>
      <div>
        <button
          onClick={toggleTheme}
          aria-label="Toggle theme"
          style={{
            padding: '8px 12px',
            borderRadius: 8,
            border: '1px solid rgba(0,0,0,0.08)',
            background: 'transparent',
            cursor: 'pointer'
          }}
        >
          {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
        </button>
      </div>
    </header>
  );
};

export default Header;