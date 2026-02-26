import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import '../Auth.css';

const AdminDashboard = () => {
    const [showUsersModal, setShowUsersModal] = useState(false);
    const [showUploadsModal, setShowUploadsModal] = useState(false);
    const [showActivityModal, setShowActivityModal] = useState(false);
    const [users, setUsers] = useState([]);
    const [uploads, setUploads] = useState([]);
    const [activityUser, setActivityUser] = useState(null);
    const [activityHistory, setActivityHistory] = useState([]);
    const [stats, setStats] = useState({ total_users: 0, total_uploads: 0, active_users: 0 });
    const [loadingUsers, setLoadingUsers] = useState(false);
    const [loadingUploads, setLoadingUploads] = useState(false);
    const [loadingActivity, setLoadingActivity] = useState(false);
    const [loadingStats, setLoadingStats] = useState(false);
    const [errorUsers, setErrorUsers] = useState('');
    const [errorUploads, setErrorUploads] = useState('');
    const { logout, user } = useAuth();
    const navigate = useNavigate();

    // Fetch stats on mount
    useEffect(() => {
        fetchStats();
    }, []);

    const handleLogout = () => {
        logout();
        navigate('/signin');
    };

    const fetchStats = async () => {
        setLoadingStats(true);
        try {
            const response = await axios.get('/api/admin/stats');
            if (response.data.success) {
                setStats(response.data.stats);
            }
        } catch (error) {
            console.error('Stats fetch error:', error);
        } finally {
            setLoadingStats(false);
        }
    };

    const fetchUsers = async () => {
        setLoadingUsers(true);
        setErrorUsers('');
        try {
            const response = await axios.get('/api/admin/users');
            if (response.data.success) {
                setUsers(response.data.users);
                setShowUsersModal(true);
            } else {
                setErrorUsers(response.data.error || 'Failed to fetch users');
            }
        } catch (error) {
            setErrorUsers(error.response?.data?.error || error.message);
        } finally {
            setLoadingUsers(false);
        }
    };

    const fetchUploads = async () => {
        setLoadingUploads(true);
        setErrorUploads('');
        try {
            const response = await axios.get('/api/admin/uploads');
            if (response.data.success) {
                setUploads(response.data.uploads);
                setShowUploadsModal(true);
            } else {
                setErrorUploads(response.data.error || 'Failed to fetch uploads');
            }
        } catch (error) {
            setErrorUploads(error.response?.data?.error || error.message);
        } finally {
            setLoadingUploads(false);
        }
    };

    const fetchUserActivity = async (userId) => {
        setLoadingActivity(true);
        try {
            const response = await axios.get(`/api/admin/users/${userId}/activity`);
            if (response.data.success) {
                setActivityUser(response.data.user);
                setActivityHistory(response.data.history);
                setShowActivityModal(true);
            }
        } catch (error) {
            console.error('Activity fetch error:', error);
        } finally {
            setLoadingActivity(false);
        }
    };

    const formatDate = (iso) => {
        if (!iso) return '—';
        const d = new Date(iso);
        return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const statCards = [
        { icon: '👥', label: 'Total Users', value: stats.total_users, color: '#3b82f6' },
        { icon: '📁', label: 'Total Uploads', value: stats.total_uploads, color: '#a855f7' },
        { icon: '🟢', label: 'Active (7d)', value: stats.active_users, color: '#22c55e' }
    ];

    return (
        <div className="admin-container">
            <div className="auth-background"></div>

            <div style={{ position: 'absolute', top: '20px', right: '20px', zIndex: 100 }}>
                <span style={{ color: '#e5e7eb', marginRight: '15px' }}>{user?.name}</span>
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
                >
                    Logout
                </button>
            </div>

            <div className="admin-card">
                <h1>🎛️ Admin Dashboard</h1>
                <p className="muted">Manage users, uploads, and system health</p>

                {/* Stats Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
                    {statCards.map((s, i) => (
                        <div key={i} style={{
                            padding: '1.2rem',
                            borderRadius: '12px',
                            background: 'rgba(30, 41, 59, 0.5)',
                            border: `1px solid ${s.color}33`,
                            textAlign: 'center',
                            transition: 'all 0.3s'
                        }}>
                            <div style={{ fontSize: '1.5rem', marginBottom: '6px' }}>{s.icon}</div>
                            <div style={{ fontSize: '2rem', fontWeight: '700', color: s.color }}>
                                {loadingStats ? '...' : s.value}
                            </div>
                            <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '4px' }}>{s.label}</div>
                        </div>
                    ))}
                </div>

                <div className="admin-grid">
                    <div className="admin-box">
                        <h3>👥 Users</h3>
                        <p>Manage registered users, view login activity.</p>
                        <button className="admin-btn" onClick={fetchUsers} disabled={loadingUsers}>
                            {loadingUsers ? 'Loading...' : 'View Users'}
                        </button>
                    </div>

                    <div className="admin-box">
                        <h3>📁 Uploads</h3>
                        <p>Review uploaded PDFs and reading activity.</p>
                        <button className="admin-btn" onClick={fetchUploads} disabled={loadingUploads}>
                            {loadingUploads ? 'Loading...' : 'View Uploads'}
                        </button>
                    </div>

                    <div className="admin-box">
                        <h3>🏥 Health</h3>
                        <p>Check backend and model health.</p>
                        <button className="admin-btn" onClick={fetchStats}>Refresh Stats</button>
                    </div>

                    <div className="admin-box">
                        <h3>⚙️ Settings</h3>
                        <p>Application configuration and secrets.</p>
                        <button className="admin-btn">Open Settings</button>
                    </div>
                </div>
            </div>

            {/* Users Modal */}
            {showUsersModal && (
                <div className="admin-modal-overlay" onClick={() => setShowUsersModal(false)}>
                    <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
                        <h2>Registered Users ({users.length})</h2>
                        {errorUsers && <p style={{ color: '#fecaca' }}>{errorUsers}</p>}
                        <div className="admin-table">
                            <div className="admin-table-header" style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
                                <div>Name</div>
                                <div>Email</div>
                                <div>Last Login</div>
                                <div>Logins / Uploads</div>
                                <div>Actions</div>
                            </div>
                            {users.map(u => (
                                <div key={u.id} className="admin-table-row" style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
                                    <div>{u.name}</div>
                                    <div style={{ fontSize: '0.85rem', wordBreak: 'break-all' }}>{u.email}</div>
                                    <div style={{ fontSize: '0.85rem' }}>{formatDate(u.last_login)}</div>
                                    <div>{u.login_count || 0} / {u.uploads_count || 0}</div>
                                    <div>
                                        <button
                                            className="admin-btn"
                                            style={{ padding: '5px 10px', fontSize: '0.8rem' }}
                                            onClick={() => fetchUserActivity(u.id)}
                                            disabled={loadingActivity}
                                        >
                                            View Activity
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <button className="admin-close-btn" onClick={() => setShowUsersModal(false)}>Close</button>
                    </div>
                </div>
            )}

            {/* Uploads Modal */}
            {showUploadsModal && (
                <div className="admin-modal-overlay" onClick={() => setShowUploadsModal(false)}>
                    <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
                        <h2>Recent Uploads ({uploads.length})</h2>
                        {errorUploads && <p style={{ color: '#fecaca' }}>{errorUploads}</p>}
                        {uploads.length === 0 ? (
                            <p style={{ textAlign: 'center', color: '#999' }}>No uploads yet</p>
                        ) : (
                            <div className="admin-table">
                                <div className="admin-table-header">
                                    <div>Title</div>
                                    <div>User</div>
                                    <div>Uploaded</div>
                                </div>
                                {uploads.map(upload => (
                                    <div key={upload.id} className="admin-table-row">
                                        <div>{upload.title}</div>
                                        <div>{upload.user_name || upload.user_id || '—'}</div>
                                        <div>{formatDate(upload.created_at)}</div>
                                    </div>
                                ))}
                            </div>
                        )}
                        <button className="admin-close-btn" onClick={() => setShowUploadsModal(false)}>Close</button>
                    </div>
                </div>
            )}

            {/* User Activity Modal */}
            {showActivityModal && activityUser && (
                <div className="admin-modal-overlay" onClick={() => setShowActivityModal(false)}>
                    <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
                        <h2>📊 Activity: {activityUser.name}</h2>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
                            <div style={{ padding: '1rem', borderRadius: '10px', background: 'rgba(30, 41, 59, 0.6)', textAlign: 'center' }}>
                                <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Email</div>
                                <div style={{ fontSize: '0.95rem', marginTop: '4px', wordBreak: 'break-all' }}>{activityUser.email}</div>
                            </div>
                            <div style={{ padding: '1rem', borderRadius: '10px', background: 'rgba(30, 41, 59, 0.6)', textAlign: 'center' }}>
                                <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Total Logins</div>
                                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#3b82f6', marginTop: '4px' }}>{activityUser.login_count || 0}</div>
                            </div>
                            <div style={{ padding: '1rem', borderRadius: '10px', background: 'rgba(30, 41, 59, 0.6)', textAlign: 'center' }}>
                                <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Last Login</div>
                                <div style={{ fontSize: '0.9rem', marginTop: '4px' }}>{formatDate(activityUser.last_login)}</div>
                            </div>
                        </div>

                        <h3 style={{ marginBottom: '0.8rem' }}>📚 Reading History ({activityHistory.length})</h3>
                        {activityHistory.length === 0 ? (
                            <p style={{ textAlign: 'center', color: '#999' }}>No reading history yet</p>
                        ) : (
                            <div className="admin-table">
                                <div className="admin-table-header" style={{ gridTemplateColumns: '2fr 1fr 1fr 1fr' }}>
                                    <div>Title</div>
                                    <div>Progress</div>
                                    <div>Status</div>
                                    <div>Last Read</div>
                                </div>
                                {activityHistory.map(h => (
                                    <div key={h.id} className="admin-table-row" style={{ gridTemplateColumns: '2fr 1fr 1fr 1fr' }}>
                                        <div>{h.title}</div>
                                        <div>
                                            {h.last_page}/{h.total_pages || '?'} pages
                                        </div>
                                        <div>
                                            <span style={{
                                                padding: '2px 8px',
                                                borderRadius: '12px',
                                                fontSize: '0.75rem',
                                                background: h.status === 'completed' ? 'rgba(34,197,94,0.15)' : 'rgba(59,130,246,0.15)',
                                                color: h.status === 'completed' ? '#22c55e' : '#3b82f6'
                                            }}>
                                                {h.status || 'in_progress'}
                                            </span>
                                        </div>
                                        <div style={{ fontSize: '0.85rem' }}>{formatDate(h.updated_at)}</div>
                                    </div>
                                ))}
                            </div>
                        )}
                        <button className="admin-close-btn" onClick={() => setShowActivityModal(false)}>Close</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminDashboard;
