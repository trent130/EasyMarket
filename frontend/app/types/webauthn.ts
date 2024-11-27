export interface PublicKeyCredentialCreationOptions {
    challenge: BufferSource;
    rp: PublicKeyCredentialRpEntity;
    user: PublicKeyCredentialUserEntity;
    pubKeyCredParams: PublicKeyCredentialParameters[];
    timeout?: number;
    excludeCredentials?: PublicKeyCredentialDescriptor[];
    authenticatorSelection?: AuthenticatorSelectionCriteria;
    attestation?: AttestationConveyancePreference;
    extensions?: AuthenticationExtensionsClientInputs;
}

export interface PublicKeyCredentialRequestOptions {
    challenge: BufferSource;
    timeout?: number;
    rpId?: string;
    allowCredentials?: PublicKeyCredentialDescriptor[];
    userVerification?: UserVerificationRequirement;
    extensions?: AuthenticationExtensionsClientInputs;
}

export interface WebAuthnRegistrationResult {
    id: string;
    rawId: ArrayBuffer;
    response: {
        attestationObject: ArrayBuffer;
        clientDataJSON: ArrayBuffer;
    };
    type: 'public-key';
}

export interface WebAuthnAuthenticationResult {
    id: string;
    rawId: ArrayBuffer;
    response: {
        authenticatorData: ArrayBuffer;
        clientDataJSON: ArrayBuffer;
        signature: ArrayBuffer;
        userHandle: ArrayBuffer | null;
    };
    type: 'public-key';
} 