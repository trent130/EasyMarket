import { fetchWrapper } from '../../utils/fetchWrapper';

export interface SecurityLog {
    id: string;
    userId: number;
    action: string;
    ipAddress: string;
    userAgent: string;
    location: string;
    timestamp: string;
    status: 'success' | 'failure';
    details?: Record<string, any>;
}

export interface SecuritySettings {
    twoFactorEnabled: boolean;
    loginNotifications: boolean;
    trustedDevices: boolean;
    passwordLastChanged: string;
    securityQuestionsSet: boolean;
}

export const securityApi = {
    // Security Settings
    getSecuritySettings: () =>
        fetchWrapper<SecuritySettings>('/api/security/settings'),

    updateSecuritySettings: (settings: Partial<SecuritySettings>) =>
        fetchWrapper('/api/security/settings', {
            method: 'PUT',
            body: JSON.stringify(settings)
        }),

    // Activity Logging
    getActivityLogs: (params?: {
        startDate?: string;
        endDate?: string;
        type?: string;
        page?: number;
        pageSize?: number;
    }) =>
        fetchWrapper<SecurityLog[]>('/api/security/activity-logs', { params }),

    // Password Management
    changePassword: (currentPassword: string, newPassword: string) =>
        fetchWrapper('/api/security/change-password', {
            method: 'POST',
            body: JSON.stringify({ currentPassword, newPassword })
        }),

    setupSecurityQuestions: (questions: Array<{ question: string; answer: string }>) =>
        fetchWrapper('/api/security/security-questions', {
            method: 'POST',
            body: JSON.stringify({ questions })
        }),

    // Device Management
    getTrustedDevices: () =>
        fetchWrapper<Array<{
            id: string;
            name: string;
            lastUsed: string;
            browser: string;
            os: string;
            isCurrent: boolean;
        }>>('/api/security/trusted-devices'),

    removeTrustedDevice: (deviceId: string) =>
        fetchWrapper(`/api/security/trusted-devices/${deviceId}`, {
            method: 'DELETE'
        }),

    // Session Management
    getActiveSessions: () =>
        fetchWrapper<Array<{
            id: string;
            ipAddress: string;
            location: string;
            device: string;
            lastActive: string;
            isCurrent: boolean;
        }>>('/api/security/active-sessions'),

    terminateSession: (sessionId: string) =>
        fetchWrapper(`/api/security/active-sessions/${sessionId}`, {
            method: 'DELETE'
        }),

    terminateAllOtherSessions: () =>
        fetchWrapper('/api/security/active-sessions/terminate-others', {
            method: 'POST'
        }),

    // Login Verification
    requestLoginVerification: (email: string) =>
        fetchWrapper('/api/security/login-verification', {
            method: 'POST',
            body: JSON.stringify({ email })
        }),

    verifyLoginCode: (email: string, code: string) =>
        fetchWrapper('/api/security/verify-login-code', {
            method: 'POST',
            body: JSON.stringify({ email, code })
        })
};

export type SecurityApi = typeof securityApi; 