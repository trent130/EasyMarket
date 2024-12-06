import { fetchWrapper } from '../../utils/fetchWrapper';
import { User } from '../../types/common';
import { 
    PublicKeyCredentialCreationOptions,
    PublicKeyCredentialRequestOptions,
} from '@simplewebauthn/typescript-types';

export interface SecurityKey {
    id: string;
    name: string;
    lastUsed: string;
    credentialId: string;
}

export interface WebAuthnError extends Error {
    name: 'NotAllowedError' | 'SecurityError' | 'AbortError';
}

interface ProfileUpdateData {
    firstName: string;
    lastName: string;
    email: string;
    avatar?: File;
}

interface FetchOptionsWithBlob extends RequestInit {
    params?: Record<string, string | number>;
    blob?: boolean;
}

async function fetchWrapperBlob(endpoint: string, options?: FetchOptionsWithBlob): Promise<Blob> {
    const response = await fetch(endpoint, options);
    if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
    }
    return response.blob();
}

export const profileApi = {
    updateProfile: (formData: FormData) =>
        fetchWrapper<User>('/api/user/profile', {
            method: 'PUT',
            body: formData,
            headers: {} // Let browser set content-type for FormData
        }),

    getWebAuthnRegistrationOptions: () =>
        fetchWrapper<PublicKeyCredentialCreationOptions>('/api/auth/webauthn/register-options'),

    verifyWebAuthnRegistration: (credential: any, keyName: string) =>
        fetchWrapper('/api/auth/webauthn/verify-registration', {
            method: 'POST',
            body: JSON.stringify({ credential, keyName })
        }),

    getWebAuthnAuthOptions: () =>
        fetchWrapper<PublicKeyCredentialRequestOptions>('/api/auth/webauthn/auth-options'),

    verifyWebAuthnAuthentication: (credential: any) =>
        fetchWrapper('/api/auth/webauthn/verify-authentication', {
            method: 'POST',
            body: JSON.stringify(credential)
        }),

    getSecurityKeys: () =>
        fetchWrapper<SecurityKey[]>('/api/user/security-keys'),

    removeSecurityKey: (keyId: string) =>
        fetchWrapper(`/api/user/security-keys/${keyId}`, {
            method: 'DELETE'
        }),

    exportUserData: () =>
        fetchWrapperBlob('/api/user/data-export', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            }
        }),

    deleteAccount: () =>
        fetchWrapper('/api/user/delete-account', {
            method: 'POST'
        }),
};

// impimentations in the backend 
