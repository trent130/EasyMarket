import crypto from 'crypto';

// In a real application, you would use a proper email service
async function sendEmail(to: string, subject: string, body: string) {
  console.log(`Sending email to ${to}:\nSubject: ${subject}\nBody: ${body}`);
  // Simulate email sending delay
  await new Promise(resolve => setTimeout(resolve, 1000));
}

export async function generateAndSendEmailCode(email: string): Promise<string> {
  const code = crypto.randomInt(100000, 999999).toString();
  await sendEmail(
    email,
    'Your Authentication Code',
    `Your authentication code is: ${code}. This code will expire in 10 minutes.`
  );
  return code;
}
