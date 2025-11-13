import { useState, useEffect } from 'react';
import './Profile.css';

function Profile({ user, onUpdateUser }) {
  const [activeTab, setActiveTab] = useState('info');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [fullUserData, setFullUserData] = useState(null);
  
  // Profile info state
  const [name, setName] = useState(user?.name || '');
  
  // Password change state
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  // Fetch full user data on mount
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch(
          `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/auth/me`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
        
        if (response.ok) {
          const data = await response.json();
          setFullUserData(data);
          setName(data.name || '');
        }
      } catch (err) {
        console.error('Failed to fetch user data:', err);
      }
    };
    
    fetchUserData();
  }, []);

  useEffect(() => {
    setName(user?.name || '');
  }, [user]);

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/auth/profile`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ name }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to update profile');
      }

      // Update local user data with full user object
      const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
      const updatedUser = { ...currentUser, name: data.name };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      
      // Update parent component state
      onUpdateUser(updatedUser);
      
      // Also update fullUserData state
      setFullUserData(prev => ({ ...prev, name: data.name }));

      setMessage({ type: 'success', text: 'Profile updated successfully!' });
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    // Validation
    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage({ type: 'error', text: 'New passwords do not match' });
      setLoading(false);
      return;
    }

    if (passwordData.new_password.length < 8) {
      setMessage({ type: 'error', text: 'Password must be at least 8 characters' });
      setLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/auth/change-password`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            current_password: passwordData.current_password,
            new_password: passwordData.new_password
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to change password');
      }

      setMessage({ type: 'success', text: 'Password changed successfully!' });
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Just now';
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return 'Just now';
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return 'Just now';
    }
  };

  const displayUser = fullUserData || user;

  return (
    <div className="profile-container">
      <div className="profile-header">
        <div className="profile-avatar">
          <span className="avatar-letter">
            {displayUser?.name?.charAt(0).toUpperCase() || displayUser?.email?.charAt(0).toUpperCase() || '?'}
          </span>
        </div>
        <div className="profile-header-info">
          <h1 className="profile-name">{displayUser?.name || 'User Profile'}</h1>
          <p className="profile-email">
            <span className="email-icon">✉️</span>
            {displayUser?.email}
          </p>
          <div className="profile-badges">
            <span className="badge">👤 Member</span>
            {displayUser?.email_verified && <span className="badge verified">✓ Verified</span>}
          </div>
        </div>
      </div>

      <div className="profile-tabs">
        <button
          className={activeTab === 'info' ? 'active' : ''}
          onClick={() => setActiveTab('info')}
        >
          📋 Profile Info
        </button>
        <button
          className={activeTab === 'security' ? 'active' : ''}
          onClick={() => setActiveTab('security')}
        >
          🔒 Security
        </button>
      </div>

      {message.text && (
        <div className={`profile-message ${message.type}`}>
          {message.type === 'success' ? '✅' : '⚠️'} {message.text}
        </div>
      )}

      {activeTab === 'info' && (
        <div className="profile-section">
          <h3>Account Information</h3>
          
          <div className="profile-stats">
            <div className="profile-stat">
              <div className="stat-icon">📅</div>
              <div className="stat-content">
                <span className="stat-label">Member Since</span>
                <span className="stat-value">{formatDate(displayUser?.created_at)}</span>
              </div>
            </div>
            <div className="profile-stat">
              <div className="stat-icon">🕐</div>
              <div className="stat-content">
                <span className="stat-label">Last Login</span>
                <span className="stat-value">{formatDate(displayUser?.last_login)}</span>
              </div>
            </div>
          </div>

          <form onSubmit={handleUpdateProfile} className="profile-form">
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your name"
                disabled={loading}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                value={displayUser?.email || ''}
                disabled
                className="disabled-input"
              />
              <small className="form-hint">✉️ Email cannot be changed for security reasons</small>
            </div>

            <button type="submit" className="profile-save-btn" disabled={loading}>
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        </div>
      )}

      {activeTab === 'security' && (
        <div className="profile-section">
          <h3>Change Password</h3>
          
          <form onSubmit={handleChangePassword} className="profile-form">
            <div className="form-group">
              <label htmlFor="current_password">Current Password</label>
              <input
                type="password"
                id="current_password"
                value={passwordData.current_password}
                onChange={(e) => setPasswordData({
                  ...passwordData,
                  current_password: e.target.value
                })}
                placeholder="Enter current password"
                disabled={loading}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="new_password">New Password</label>
              <input
                type="password"
                id="new_password"
                value={passwordData.new_password}
                onChange={(e) => setPasswordData({
                  ...passwordData,
                  new_password: e.target.value
                })}
                placeholder="Enter new password (min 8 characters)"
                disabled={loading}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirm_password">Confirm New Password</label>
              <input
                type="password"
                id="confirm_password"
                value={passwordData.confirm_password}
                onChange={(e) => setPasswordData({
                  ...passwordData,
                  confirm_password: e.target.value
                })}
                placeholder="Confirm new password"
                disabled={loading}
                required
              />
            </div>

            <button type="submit" className="profile-save-btn" disabled={loading}>
              {loading ? 'Changing...' : 'Change Password'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

export default Profile;
