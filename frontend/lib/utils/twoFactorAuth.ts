import { authenticator } from 'otplib';
import QRCode from 'qrcode';

export function generateSecret() {
  return authenticator.generateSecret();
}

export function generateTOTP(secret: string) {
  return authenticator.generate(secret);
}

export function verifyTOTP(token: string, secret: string) {
  return authenticator.verify({ token, secret });
}

export async function generateQRCode(secret: string, email: string, issuer: string = 'YourApp') {
  const otpauth = authenticator.keyuri(email, issuer, secret);
  return QRCode.toDataURL(otpauth);
}
