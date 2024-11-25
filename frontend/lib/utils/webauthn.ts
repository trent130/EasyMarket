import { generateAuthenticationOptions, generateRegistrationOptions, verifyAuthenticationResponse, verifyRegistrationResponse } from '@simplewebauthn/server';
import type { GenerateAuthenticationOptionsOpts, GenerateRegistrationOptionsOpts, VerifyAuthenticationResponseOpts, VerifyRegistrationResponseOpts } from '@simplewebauthn/server';

// These values should be stored securely and retrieved for each user
// For this example, we'll use a simple in-memory store
const challengeStore = new Map<string, string>();
const authenticatorStore = new Map<string, any[]>();

export const generateRegistrationOptionsHelper = (userId: string, userName: string, userDisplayName: string) => {
  const opts: GenerateRegistrationOptionsOpts = {
    rpName: 'Your App Name',
    rpID: 'localhost',
    userID: userId,
    userName,
    userDisplayName,
    timeout: 60000,
    attestationType: 'none',
    authenticatorSelection: {
      residentKey: 'preferred',
      userVerification: 'preferred',
    },
    supportedAlgorithmIDs: [-7, -257],
  };

  const options = generateRegistrationOptions(opts);
  
  // Store the challenge for later verification
  challengeStore.set(userId, options.challenge);

  return options;
};

export const verifyRegistrationResponseHelper = async (userId: string, response: any) => {
  const expectedChallenge = challengeStore.get(userId);
  if (!expectedChallenge) {
    throw new Error('Challenge not found');
  }

  const opts: VerifyRegistrationResponseOpts = {
    response,
    expectedChallenge,
    expectedOrigin: 'http://localhost:3000',
    expectedRPID: 'localhost',
    requireUserVerification: true,
  };

  const verification = await verifyRegistrationResponse(opts);

  if (verification.verified && verification.registrationInfo) {
    const { credentialPublicKey, credentialID, counter } = verification.registrationInfo;
    
    // Store the authenticator info
    const existingAuthenticators = authenticatorStore.get(userId) || [];
    authenticatorStore.set(userId, [...existingAuthenticators, { credentialID, credentialPublicKey, counter }]);
  }

  return verification;
};

export const generateAuthenticationOptionsHelper = (userId: string) => {
  const userAuthenticators = authenticatorStore.get(userId) || [];

  const opts: GenerateAuthenticationOptionsOpts = {
    timeout: 60000,
    allowCredentials: userAuthenticators.map(auth => ({
      id: auth.credentialID,
      type: 'public-key',
      transports: ['internal'],
    })),
    userVerification: 'preferred',
    rpID: 'localhost',
  };

  const options = generateAuthenticationOptions(opts);
  
  // Store the challenge for later verification
  challengeStore.set(userId, options.challenge);

  return options;
};

export const verifyAuthenticationResponseHelper = async (userId: string, response: any) => {
  const expectedChallenge = challengeStore.get(userId);
  if (!expectedChallenge) {
    throw new Error('Challenge not found');
  }

  const userAuthenticators = authenticatorStore.get(userId) || [];
  const authenticator = userAuthenticators.find(auth => 
    Buffer.from(auth.credentialID).toString('base64url') === response.id
  );

  if (!authenticator) {
    throw new Error('Authenticator not found');
  }

  const opts: VerifyAuthenticationResponseOpts = {
    response,
    expectedChallenge,
    expectedOrigin: 'http://localhost:3000',
    expectedRPID: 'localhost',
    authenticator,
    requireUserVerification: true,
  };

  const verification = await verifyAuthenticationResponse(opts);

  if (verification.verified) {
    // Update the authenticator's counter
    authenticator.counter = verification.authenticationInfo.newCounter;
  }

  return verification;
};
