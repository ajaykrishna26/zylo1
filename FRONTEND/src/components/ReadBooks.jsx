import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import '../App.css';

const ReadBooks = () => {
    const { logout, user, pdfHistory, fetchHistory, deleteFromHistory } = useAuth();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('online-library'); // 'online-library' only
    const [onlineBooks, setOnlineBooks] = useState([]);
    const [loadingOnline, setLoadingOnline] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [onlineLoading, setOnlineLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchHistory();
        setLoading(false);
    }, []);

    // Fetch featured online books when tab changes
    useEffect(() => {
        if (activeTab === 'online-library' && onlineBooks.length === 0 && !loadingOnline) {
            fetchFeaturedBooks();
        }
    }, [activeTab]);

    const fetchFeaturedBooks = async () => {
        setLoadingOnline(true);
        setError('');
        try {
            const response = await axios.get('/api/online-books/featured?limit=20');
            if (response.data.success) {
                setOnlineBooks(response.data.books);
            } else {
                setError(response.data.error || 'Failed to fetch online books');
            }
        } catch (err) {
            console.error('Error fetching featured books:', err);
            setError('Failed to connect to online library');
        } finally {
            setLoadingOnline(false);
        }
    };

    const handleSearchOnlineBooks = async (e) => {
        e.preventDefault();
        if (!searchQuery.trim()) {
            fetchFeaturedBooks();
            return;
        }

        setOnlineLoading(true);
        setError('');
        try {
            const response = await axios.get('/api/online-books/search', {
                params: { query: searchQuery, limit: 20 }
            });
            if (response.data.success) {
                setOnlineBooks(response.data.books);
            } else {
                setError(response.data.error || 'Search failed');
            }
        } catch (err) {
            console.error('Search error:', err);
            setError('Failed to search online books');
        } finally {
            setOnlineLoading(false);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/signin');
    };

    const handleReadPdf = (pdf) => {
        // Store selected PDF in session/state and navigate to reader
        navigate('/reader', { state: { pdf } });
    };

    const handleReadOnlineBook = (book) => {
        // For online books, we store the book data including the text URL
        navigate('/reader', { state: { pdf: { ...book, isOnlineBook: true } } });
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

            <div style={{ padding: '40px 24px', maxWidth: '1200px', margin: '0 auto', background: 'transparent' }}>
                <div style={{ marginBottom: '50px' }}>
                    <h1 className="gradient-text" style={{ fontSize: '2.5rem', marginBottom: '10px' }}>
                        📖 Reading Library
                    </h1>
                    <p className="text-secondary" style={{ fontSize: '1rem' }}>
                        Explore your books and discover online reading materials
                    </p>
                </div>

                {/* Tab Navigation */}
                <div style={{ display: 'flex', gap: '10px', marginBottom: '30px', borderBottom: '1px solid rgba(51, 65, 85, 0.5)' }}>
                    <div style={{ padding: '12px 24px', fontSize: '1rem', fontWeight: '600', color: '#3b82f6' }}>🌐 Online Library</div>
                </div>

                {/* My Books tab removed — defaulting to Online Library */}

                {/* Online Library Tab */}
                {activeTab === 'online-library' && (
                    <div>
                        {/* Search Bar */}
                        <form onSubmit={handleSearchOnlineBooks} style={{ marginBottom: '30px' }}>
                            <div style={{ display: 'flex', gap: '10px' }}>
                                <input
                                    type="text"
                                    placeholder="Search books by title or author..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    style={{
                                        flex: 1,
                                        padding: '12px 15px',
                                        background: 'rgba(30, 41, 59, 0.6)',
                                        border: '1px solid #334155',
                                        borderRadius: '8px',
                                        color: '#e5e7eb',
                                        fontSize: '1rem',
                                        transition: 'all 0.3s',
                                    }}
                                    onFocus={(e) => {
                                        e.target.style.borderColor = '#3b82f6';
                                        e.target.style.background = 'rgba(30, 41, 59, 0.8)';
                                    }}
                                    onBlur={(e) => {
                                        e.target.style.borderColor = '#334155';
                                        e.target.style.background = 'rgba(30, 41, 59, 0.6)';
                                    }}
                                />
                                <button
                                    type="submit"
                                    disabled={onlineLoading}
                                    style={{
                                        padding: '12px 30px',
                                        background: 'rgba(59, 130, 246, 0.8)',
                                        border: '1px solid rgba(59, 130, 246, 1)',
                                        borderRadius: '8px',
                                        color: '#fff',
                                        cursor: 'pointer',
                                        fontSize: '1rem',
                                        fontWeight: '500',
                                        transition: 'all 0.3s',
                                    }}
                                    onMouseEnter={(e) => {
                                        if (!onlineLoading) {
                                            e.target.style.background = 'rgba(59, 130, 246, 1)';
                                        }
                                    }}
                                    onMouseLeave={(e) => {
                                        if (!onlineLoading) {
                                            e.target.style.background = 'rgba(59, 130, 246, 0.8)';
                                        }
                                    }}
                                >
                                    {onlineLoading ? 'Searching...' : 'Search'}
                                </button>
                            </div>
                        </form>

                        {/* Error Message */}
                        {error && (
                            <div style={{
                                textAlign: 'center',
                                padding: '15px',
                                background: 'rgba(239, 68, 68, 0.1)',
                                border: '1px solid rgba(239, 68, 68, 0.3)',
                                borderRadius: '8px',
                                color: '#fca5a5',
                                marginBottom: '20px'
                            }}>
                                {error}
                            </div>
                        )}

                        {/* Online Books Grid */}
                        {loadingOnline ? (
                            <div style={{ textAlign: 'center', color: '#a0aec0', fontSize: '1.1rem' }}>
                                Loading books from Project Gutenberg...
                            </div>
                        ) : onlineBooks && onlineBooks.length > 0 ? (
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
                                {onlineBooks.map((book) => (
                                    <div
                                        key={book.id}
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
                                        onClick={() => handleReadOnlineBook(book)}
                                        onMouseEnter={(e) => {
                                            e.currentTarget.style.transform = 'translateY(-4px)';
                                            e.currentTarget.style.borderColor = '#10b981';
                                            e.currentTarget.style.background = 'rgba(30, 41, 59, 0.9)';
                                        }}
                                        onMouseLeave={(e) => {
                                            e.currentTarget.style.transform = 'translateY(0)';
                                            e.currentTarget.style.borderColor = '#334155';
                                            e.currentTarget.style.background = 'rgba(30, 41, 59, 0.6)';
                                        }}
                                    >
                                        {book.cover_image ? (
                                            <div style={{
                                                width: '100%',
                                                height: '180px',
                                                marginBottom: '15px',
                                                borderRadius: '6px',
                                                overflow: 'hidden',
                                                background: 'rgba(15, 23, 42, 0.5)'
                                            }}>
                                                <img
                                                    src={book.cover_image}
                                                    alt={book.title}
                                                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                                    onError={(e) => {
                                                        e.target.style.display = 'none';
                                                    }}
                                                />
                                            </div>
                                        ) : (
                                            <div style={{ fontSize: '3rem', marginBottom: '15px', textAlign: 'center' }}>📖</div>
                                        )}
                                        <h3 style={{ margin: '0 0 8px 0', color: '#e5e7eb', fontSize: '1.1rem', wordWrap: 'break-word' }}>
                                            {book.title}
                                        </h3>
                                        <p style={{ margin: '0 0 8px 0', color: '#a0aec0', fontSize: '0.9rem' }}>
                                            by {book.author}
                                        </p>
                                        <p style={{ margin: '0', color: '#64748b', fontSize: '0.85rem' }}>
                                            📊 {book.download_count.toLocaleString()} downloads
                                        </p>
                                        <p style={{ margin: '8px 0 0 0', color: '#64748b', fontSize: '0.8rem' }}>
                                            Source: {book.source}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        ) : !loadingOnline && (
                            <div style={{ textAlign: 'center', padding: '60px 20px', color: '#a0aec0' }}>
                                <p style={{ fontSize: '1.2rem', marginBottom: '20px' }}>
                                    No books found
                                </p>
                                <button
                                    onClick={fetchFeaturedBooks}
                                    className="btn btn-primary"
                                    style={{ padding: '12px 30px', fontSize: '1rem' }}
                                >
                                    Browse Featured Books
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ReadBooks;
