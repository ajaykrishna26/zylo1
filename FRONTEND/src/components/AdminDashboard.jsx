import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import '../Auth.css';

const AdminDashboard = () => {
    const [showUsersModal, setShowUsersModal] = useState(false);
    const [showUploadsModal, setShowUploadsModal] = useState(false);
    const [users, setUsers] = useState([]);
    const [uploads, setUploads] = useState([]);
    const [loadingUsers, setLoadingUsers] = useState(false);
    const [loadingUploads, setLoadingUploads] = useState(false);
    const [errorUsers, setErrorUsers] = useState('');
    const [errorUploads, setErrorUploads] = useState('');
    const { logout, user } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/signin');
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

                <div className="admin-grid">
                    <div className="admin-box">
                        <h3>👥 Users</h3>
                        <p>Manage registered users and roles.</p>
                        <button className="admin-btn" onClick={fetchUsers} disabled={loadingUsers}>
                            {loadingUsers ? 'Loading...' : 'View Users'}
                        </button>
                    </div>

                    <div className="admin-box">
                        <h3>📁 Uploads</h3>
                        <p>Review uploaded PDFs and processing queue.</p>
                        <button className="admin-btn" onClick={fetchUploads} disabled={loadingUploads}>
                            {loadingUploads ? 'Loading...' : 'View Uploads'}
                        </button>
                    </div>

                    <div className="admin-box">
                        <h3>🏥 Health</h3>
                        <p>Check backend and model health.</p>
                        <button className="admin-btn">Check Health</button>
                    </div>

                    <div className="admin-box">
                        <h3>⚙️ Settings</h3>
                        <p>Application configuration and secrets.</p>
                        <button className="admin-btn">Open Settings</button>
                    </div>
                </div>
            </div>

            {showUsersModal && (
                <div className="admin-modal-overlay" onClick={() => setShowUsersModal(false)}>
                    <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
                        <h2>Registered Users ({users.length})</h2>
                        {errorUsers && <p style={{ color: '#fecaca' }}>{errorUsers}</p>}
                        <div className="admin-table">
                            <div className="admin-table-header">
                                <div>Name</div>
                                <div>Email</div>
                                <div>Created</div>
                            </div>
                            {users.map(user => (
                                <div key={user.id} className="admin-table-row">
                                    <div>{user.name}</div>
                                    <div>{user.email}</div>
                                    <div>{new Date(user.created_at).toLocaleDateString()}</div>
                                </div>
                            ))}
                        </div>
                        <button className="admin-close-btn" onClick={() => setShowUsersModal(false)}>Close</button>
                    </div>
                </div>
            )}

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
                                    <div>User ID</div>
                                    <div>Uploaded</div>
                                </div>
                                {uploads.map(upload => (
                                    <div key={upload.id} className="admin-table-row">
                                        <div>{upload.title}</div>
                                        <div>{upload.user_id}</div>
                                        <div>{new Date(upload.created_at).toLocaleDateString()}</div>
                                    </div>
                                ))}
                            </div>
                        )}
                        <button className="admin-close-btn" onClick={() => setShowUploadsModal(false)}>Close</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminDashboard;
