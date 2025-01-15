import { useState, useEffect } from 'react';
import { User } from '../../types/common';
import { profileApi, SecurityKey } from '../../services/api/profileApi';
import { handleApiError } from '../../utils/errorHandling';
import { startRegistration } from '@simplewebauthn/browser';
import './Profile.css';
import { string } from 'zod';

interface ProfileProps {
    user: User;
    onUpdate: () => void;
}

interface ActivityLog {
    id: string;
    action: string;
    timestamp: string;
    deviceInfo: string;
    location: string;
}

export function Profile() {
    const [isEditing, setIsEditing] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [securityKeys, setSecurityKeys] = useState<SecurityKey[]>([]);
    const [keyName, setKeyName] = useState('');
    const [showKeyDialog, setShowKeyDialog] = useState(false);
    const [recoveryCodes, setRecoveryCodes] = useState<string[]>([]);
    const [showRecoveryCodes, setShowRecoveryCodes] = useState(false);
    const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([]);
    const [devices, setDevices] = useState<Array<{
        id: string;
        name: string;
        lastUsed: string;
        browser: string;
    }>>([]);

        os: string;
    }>([]);
    const [sessions, setSessions] = useState<Array<{
        id: string;
        createdAt: string;
        lastActive: string;
        ipAddress: string;
        userAgent: string;
    }>>([]);

    useEffect(() => {
        loadSecurityData();
    }, []);

    async function loadSecurityData() {
        try {
            const [keys, logs, deviceList, sessionList] = await Promise.all([
                profileApi.getSecurityKeys(),
                profileApi.getActivityLogs(),
                
                profileApi.getDevices(),
                profileApi.getSessions()
            ]);
            
            setSecurityKeys(keys);
            setActivityLogs(logs);
            setDevices(deviceList);
            setSessions(sessionList);
        } catch (err: unknown) {
            setError(handleApiError(err));
        }
    }

    const generateRecoveryCodes = async () => {
        try {
            setLoading(true);
            const codes = await profileApi.generateRecoveryCodes();
            setRecoveryCodes(codes);
            setShowRecoveryCodes(true);
            setMessage('New recovery codes generated. Please save them securely.');
        } catch (err: unknown) {
            setError(handleApiError(err));
        } finally {
            setLoading(false);
        }
    };

    const handleDeviceRevoke = async (deviceId: string) => {
        try {
            setLoading(true);
            await profileApi.revokeDevice(deviceId);
            await loadSecurityData();
            setMessage('Device access revoked successfully');
        } catch (err: unknown) {
            setError(handleApiError(err));
        } finally {
            setLoading(false);
        }
    };

    const handleSessionTerminate = async (sessionId: string) => {
        try {
            setLoading(true);
            await profileApi.terminateSession(sessionId);
            await loadSecurityData();
            setMessage('Session terminated successfully');
        } catch (err: unknown) {
            setError(handleApiError(err));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="profile-container">
            {/* Profile Edit Form */}
            {isEditing ? (
<form onSubmit={handleSubmit} className="profile-form" aria-label="Profile Edit Form">
                    <div className="form-group">
                        <label htmlFor="firstName">First Name</label>
                        <input
                            type="text"
                            id="firstName"
                            name="firstName"
                            defaultValue={user.firstName}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="lastName">Last Name</label>
                        <input
                            type="text"
                            id="lastName"
                            name="lastName"
                            defaultValue={user.lastName}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            defaultValue={user.email}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="avatar">Profile Picture</label>
                        <input
                            type="file"
                            id="avatar"
                            name="avatar"
                            accept="image/*"
                        />
                    </div>

                    <button 
                        type="submit" 
                        className="submit-button"
                        disabled={loading}
                    >
                        {loading ? 'Saving...' : 'Save Changes'}
                    </button>
                </form>
            ) : (
                <div className="profile-sections">
                    {/* Basic Info Section */}
                    <section className="profile-section">
                        <h2>Profile Information</h2>
                        <div className="profile-details">
                            <div className="avatar-container">
                                <img 
                                    src={user.avatar || '/default-avatar.png'} 
                                    alt={`${user.firstName}'s avatar`}
                                    className="profile-avatar"
                                />
                            </div>
                            <div className="user-info">
                                <p><strong>Name:</strong> {user.firstName} {user.lastName}</p>
                                <p><strong>Email:</strong> {user.email}</p>
                                <p><strong>Role:</strong> {user.role}</p>
                                <p><strong>Status:</strong> {user.status}</p>
                            </div>
                        </div>
                        <button 
                            onClick={() => setIsEditing(true)}
                            className="edit-button"
                        >
                            Edit Profile
                        </button>
                    </section>

                    {/* Data Management Section */}
                    <section className="profile-section">
                        <h2>Data Management</h2>
                        <button onClick={handleDownloadData} className="data-button">
                            Download My Data
                        </button>
                        <button 
                            onClick={() => setShowDeleteConfirmation(true)} 
                            className="delete-button"
                        >
                            Delete Account
                        </button>
                    </section>

                    {/* WebAuthn Section */}
                    <section className="profile-section security-section">
                        <h2>Two-Factor Authentication</h2>
                        <div className="webauthn-container">
                            {securityKeys.length > 0 ? (
                                <>
                                    <p>WebAuthn is registered for this account.</p>
                                    <button
                                        onClick={handleAuthenticateWebAuthn}
                                        className="security-button"
                                        disabled={loading}
                                    >
                                        Verify with WebAuthn
                                    </button>
                                </>
                            ) : (
                                <>
                                    <p>Enhance your account security with WebAuthn.</p>
                                    <button
                                        onClick={handleRegisterWebAuthn}
                                        className="security-button"
                                        disabled={loading}
                                    >
                                        Setup WebAuthn
                                    </button>
                                </>
                            )}
                        </div>
                    </section>

                    {/* Enhanced Security Section */}
                    <section className="profile-section security-section">
                        <h2>Security Settings</h2>
                        
                        {/* Two-Factor Authentication */}
                        <div className="security-subsection">
                            <h3>Two-Factor Authentication</h3>
                            <div className="webauthn-container">
                                {securityKeys.length > 0 ? (
                                    <>
                                        <div className="security-keys-list">
                                            <h4>Registered Security Keys</h4>
                                            {securityKeys.map(key => (
                                                <div key={key.id} className="security-key-item">
                                                    <div className="key-info">
                                                        <span className="key-name">{key.name}</span>
                                                        <span className="key-last-used">
                                                            Last used: {new Date(key.lastUsed).toLocaleDateString()}
                                                        </span>
                                                    </div>
                                                    <button
                                                        onClick={() => handleRemoveKey(key.id)}
                                                        className="remove-key-button"
                                                        disabled={loading}
                                                    >
                                                        Remove
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                        <button
                                            onClick={() => setShowKeyDialog(true)}
                                            className="add-key-button"
                                            disabled={loading}
                                        >
                                            Add Another Security Key
                                        </button>
                                    </>
                                ) : (
                                    <div className="setup-2fa">
                                        <p>Protect your account with a security key or biometric authentication.</p>
                                        <button
                                            onClick={() => setShowKeyDialog(true)}
                                            className="security-button"
                                            disabled={loading}
                                        >
                                            Setup Two-Factor Authentication
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Security Key Dialog */}
                        {showKeyDialog && (
                            <div className="key-dialog-overlay">
                                <div className="key-dialog">
                                    <h3>Register New Security Key</h3>
                                    <div className="key-form">
                                        <input
                                            type="text"
                                            value={keyName}
                                            onChange={(e) => setKeyName(e.target.value)}
                                            placeholder="Enter a name for your security key"
                                            className="key-name-input"
                                        />
                                        <div className="key-dialog-buttons">
                                            <button
                                                onClick={handleRegisterWebAuthn}
                                                className="register-key-button"
                                                disabled={loading || !keyName.trim()}
                                            >
                                                {loading ? 'Registering...' : 'Register Key'}
                                            </button>
                                            <button
                                                onClick={() => {
                                                    setShowKeyDialog(false);
                                                    setKeyName('');
                                                }}
                                                className="cancel-button"
                                                disabled={loading}
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Recovery Codes */}
                        <div className="security-subsection">
                            <h3>Recovery Codes</h3>
                            {showRecoveryCodes ? (
                                <div className="recovery-codes">
                                    {recoveryCodes.map((code, index) => (
                                        <code key={index} className="recovery-code">{code}</code>
                                    ))}
                                    <button
                                        onClick={() => setShowRecoveryCodes(false)}
                                        className="hide-codes-button"
                                    >
                                        Hide Codes
                                    </button>
                                </div>
                            ) : (
                                <button
                                    onClick={generateRecoveryCodes}
                                    className="generate-codes-button"
                                    disabled={loading}
                                >
                                    Generate New Recovery Codes
                                </button>
                            )}
                        </div>

                        {/* Device Management */}
                        <div className="security-subsection">
                            <h3>Device Management</h3>
                            <div className="devices-list">
                                {devices.map(device => (
                                    <div key={device.id} className="device-item">
                                        <div className="device-info">
                                            <span className="device-name">{device.name}</span>
                                            <span className="device-details">
                                                Last active: {new Date(device.lastActive).toLocaleDateString()}
                                            </span>
                                        </div>
                                        <button
                                            onClick={() => handleDeviceRevoke(device.id)}
                                            className="revoke-button"
                                            disabled={loading}
                                        >
                                            Revoke Access
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Active Sessions */}
                        <div className="security-subsection">
                            <h3>Active Sessions</h3>
                            <div className="sessions-list">
                                {sessions.map(session => (
                                    <div key={session.id} className="session-item">
                                        <div className="session-info">
                                            <span className="session-device">{session.deviceName}</span>
                                            <span className="session-location">{session.location}</span>
                                            <span className="session-time">
                                                Started: {new Date(session.startTime).toLocaleString()}
                                            </span>
                                        </div>
                                        <button
                                            onClick={() => handleSessionTerminate(session.id)}
                                            className="terminate-button"
                                            disabled={loading}
                                        >
                                            Terminate Session
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Activity Log */}
                        <div className="security-subsection">
                            <h3>Recent Activity</h3>
                            <div className="activity-log">
                                {activityLogs.map(log => (
                                    <div key={log.id} className="activity-item">
                                        <span className="activity-action">{log.action}</span>
                                        <span className="activity-time">
                                            {new Date(log.timestamp).toLocaleString()}
                                        </span>
                                        <span className="activity-device">{log.deviceInfo}</span>
                                        <span className="activity-location">{log.location}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </section>

                    {/* Delete Confirmation */}
                    {showDeleteConfirmation && (
                        <div className="delete-confirmation">
                            <p>Are you sure? This cannot be undone.</p>
                            <div className="button-group">
                                <button onClick={handleDeleteAccount} className="confirm-delete">
                                    Yes, Delete
                                </button>
                                <button 
                                    onClick={() => setShowDeleteConfirmation(false)}
                                    className="cancel-delete"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Messages */}
            {error && <div className="error-message">{error}</div>}
            {message && <div className="success-message">{message}</div>}
        </div>
    );
} 