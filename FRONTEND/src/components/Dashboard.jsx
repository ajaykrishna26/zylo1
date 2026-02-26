import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../App.css';

const Dashboard = () => {
    const { logout, user } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/signin');
    };

    return (
        <div className="App" style={{ backgroundColor: '#020617', minHeight: '100vh' }}>
            <div style={{ position: 'absolute', top: '20px', right: '20px', zIndex: 100, display: 'flex', alignItems: 'center', gap: '15px' }}>
                <span style={{ color: '#e5e7eb', fontWeight: '500' }}>{user?.name || 'User'}</span>
                <button
                    onClick={handleLogout}
                    style={{
                        background: 'rgba(255,255,255,0.1)',
                        border: '1px solid rgba(255,255,255,0.2)',
                        color: '#fff',
                        padding: '8px 16px',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        transition: 'all 0.3s'
                    }}
                    onMouseEnter={(e) => {
                        e.target.style.background = 'rgba(255,255,255,0.2)';
                    }}
                    onMouseLeave={(e) => {
                        e.target.style.background = 'rgba(255,255,255,0.1)';
                    }}
                >
                    Logout
                </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', padding: '40px 20px' }}>
                <div style={{ textAlign: 'center', marginBottom: '60px' }}>
                    <h1 className="gradient-text" style={{ fontSize: '3rem', marginBottom: '10px' }}>
                        📚 Reading Assistant
                    </h1>
                    <p className="text-secondary" style={{ fontSize: '1.2rem' }}>
                        Welcome back! What would you like to do?
                    </p>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px', maxWidth: '800px', width: '100%' }}>

                    {/* Upload PDF Card */}
                    <div
                        className="glass fade-in"
                        style={{
                            padding: '40px',
                            borderRadius: '16px',
                            background: 'rgba(30, 41, 59, 0.6)',
                            border: '1px solid #334155',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            textAlign: 'center',
                            position: 'relative',
                            overflow: 'hidden'
                        }}
                        onClick={() => navigate('/upload')}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.transform = 'translateY(-8px)';
                            e.currentTarget.style.borderColor = '#3b82f6';
                            e.currentTarget.style.background = 'rgba(30, 41, 59, 0.9)';
                            e.currentTarget.style.boxShadow = '0 20px 50px rgba(59, 130, 246, 0.2)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.borderColor = '#334155';
                            e.currentTarget.style.background = 'rgba(30, 41, 59, 0.6)';
                            e.currentTarget.style.boxShadow = 'none';
                        }}
                    >
                        <div style={{ fontSize: '4rem', marginBottom: '20px' }}>📤</div>
                        <h2 style={{ margin: '0 0 15px 0', color: '#e5e7eb', fontSize: '1.8rem' }}>
                            Upload PDF
                        </h2>
                        <p style={{ margin: '0', color: '#a0aec0', fontSize: '1rem', lineHeight: '1.6' }}>
                            Upload a new PDF to practice reading and pronunciation
                        </p>
                    </div>

                    {/* Read Books Card */}
                    <div
                        className="glass fade-in"
                        style={{
                            padding: '40px',
                            borderRadius: '16px',
                            background: 'rgba(30, 41, 59, 0.6)',
                            border: '1px solid #334155',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            textAlign: 'center',
                            position: 'relative',
                            overflow: 'hidden'
                        }}
                        onClick={() => navigate('/books')}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.transform = 'translateY(-8px)';
                            e.currentTarget.style.borderColor = '#a855f7';
                            e.currentTarget.style.background = 'rgba(30, 41, 59, 0.9)';
                            e.currentTarget.style.boxShadow = '0 20px 50px rgba(168, 85, 247, 0.2)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.borderColor = '#334155';
                            e.currentTarget.style.background = 'rgba(30, 41, 59, 0.6)';
                            e.currentTarget.style.boxShadow = 'none';
                        }}
                    >
                        <div style={{ fontSize: '4rem', marginBottom: '20px' }}>📖</div>
                        <h2 style={{ margin: '0 0 15px 0', color: '#e5e7eb', fontSize: '1.8rem' }}>
                            Read Books
                        </h2>
                        <p style={{ margin: '0', color: '#a0aec0', fontSize: '1rem', lineHeight: '1.6' }}>
                            Select from your previously uploaded documents and practice reading
                        </p>
                    </div>

                </div>
            </div>
        </div>
    );
};

export default Dashboard;
