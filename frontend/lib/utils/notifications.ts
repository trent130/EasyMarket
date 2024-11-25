import { User } from '@/lib/models/user';

// In a real application, you would use a proper email service or push notification system
async function sendNotification(user: User, message: string) {
  console.log(`Sending notification to ${user.email}: ${message}`);
  // Simulate notification delay
  await new Promise(resolve => setTimeout(resolve, 1000));
}

export async function notifyUserOfSuspiciousActivity(user: User, activity: string, details: Record<string, any>) {
  const message = `Suspicious activity detected on your account: ${activity}. Details: ${JSON.stringify(details)}. If this wasn't you, please contact support immediately.`;
  await sendNotification(user, message);
}
