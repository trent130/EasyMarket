export interface ActivityLogEntry {
    id: string;
    timestamp: string;
    eventType: ActivityEventType;
    details: Record<string, any>;
    ipAddress: string;
    userAgent: string;
    location?: {
        city?: string;
        country?: string;
        region?: string;
    };
    status: 'success' | 'failure';
}

export type ActivityEventType =
    | 'login'
    | 'logout'
    | 'password_change'
    | 'profile_update'
    | 'security_settings_change'
    | 'device_added'
    | 'device_removed'
    | 'two_factor_enabled'
    | 'two_factor_disabled'
    | 'recovery_codes_generated'
    | 'security_questions_updated';

export interface SecurityQuestion {
    id: string;
    question: string;
    lastUpdated: string;
}

export interface TrustedDevice {
    id: string;
    name: string;
    browser: string;
    operatingSystem: string;
    lastUsed: string;
    isCurrent: boolean;
}

export interface ActiveSession {
    id: string;
    ipAddress: string;
    location: string;
    device: string;
    lastActive: string;
    isCurrent: boolean;
} 