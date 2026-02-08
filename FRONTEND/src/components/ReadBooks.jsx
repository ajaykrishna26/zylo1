import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import '../App.css';

const ReadBooks = () => {
    const { logout, user, pdfHistory, fetchHistory } = useAuth();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchHistory();
        setLoading(false);
    }, []);

    const handleLogout = () => {
        logout();
        navigate('/signin');
    };

    const handleReadPdf = (pdf) => {
        // Store selected PDF in session/state and navigate to reader
        navigate('/reader', { state: { pdf } });
    };

    return (
        <div className="App" style={{ backgroundColor: '#020617', minHeight: '100vh' }}>
            <div style={{ position: 'absolute', top: '20px', right: '20px', zIndex: 100, display: 'flex', alignItems: 'center', gap: '15px' }}>
                <button
                    onClick={() => navigate('/dashboard')}
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
                    ← Back
                </button>
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

            <div style={{ padding: '80px 40px 40px 40px', maxWidth: '1000px', margin: '0 auto' }}>
                <div style={{ marginBottom: '50px' }}>
                    <h1 className="gradient-text" style={{ fontSize: '2.5rem', marginBottom: '10px' }}>
                        📖 Your Books
                    </h1>
                    <p className="text-secondary" style={{ fontSize: '1rem' }}>
                        Select a book from your reading history
                    </p>
                </div>

                {loading ? (
                    <div style={{ textAlign: 'center', color: '#a0aec0', fontSize: '1.1rem' }}>
                        Loading your books...
                    </div>
                ) : pdfHistory && pdfHistory.length > 0 ? (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
                        {pdfHistory.map((pdf, idx) => (
                            <div
                                key={idx}
                                className="glass fade-in"
                                style={{
                                    padding: '25px',
                                    borderRadius: '12px',
                                    background: 'rgba(30, 41, 59, 0.6)',
                                    border: '1px solid #334155',
                                    cursor: 'pointer',
                                    transition: 'all 0.3s ease',
                                    display: 'flex',
                                    flexDirection: 'column'
                                }}
                                onClick={() => handleReadPdf(pdf)}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.transform = 'translateY(-4px)';
                                    e.currentTarget.style.borderColor = '#3b82f6';
                                    e.currentTarget.style.background = 'rgba(30, 41, 59, 0.9)';
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.transform = 'translateY(0)';
                                    e.currentTarget.style.borderColor = '#334155';
                                    e.currentTarget.style.background = 'rgba(30, 41, 59, 0.6)';
                                }}
                            >
                                <div style={{ fontSize: '3rem', marginBottom: '15px' }}>📕</div>
                                <h3 style={{ margin: '0 0 8px 0', color: '#e5e7eb', fontSize: '1.1rem', wordWrap: 'break-word' }}>
                                    {pdf.filename || pdf.title || `Book ${idx + 1}`}
                                </h3>
                                <p style={{ margin: '0', color: '#a0aec0', fontSize: '0.9rem' }}>
                                    Uploaded: {new Date(pdf.created_at).toLocaleDateString()}
                                </p>
                                {pdf.pages && (
                                    <p style={{ margin: '8px 0 0 0', color: '#64748b', fontSize: '0.85rem' }}>
                                        {pdf.pages} page{pdf.pages > 1 ? 's' : ''}
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>
                ) : (
                    <div style={{ textAlign: 'center', padding: '60px 20px', color: '#a0aec0' }}>
                        <p style={{ fontSize: '1.2rem', marginBottom: '20px' }}>
                            📭 No books yet
                        </p>
                        <button
                            onClick={() => navigate('/upload')}
                            className="btn btn-primary"
                            style={{ padding: '12px 30px', fontSize: '1rem' }}
                        >
                            Upload Your First PDF
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ReadBooks;
