import { compare } from 'bcrypt';

const PASSWORD_HISTORY_LIMIT = 5;

export async function isPasswordReused(newPassword: string, passwordHistory: string[]): Promise<boolean> {
  for (const oldPassword of passwordHistory) {
    if (await compare(newPassword, oldPassword)) {
      return true;
    }
  }
  return false;
}

export function updatePasswordHistory(currentPassword: string, passwordHistory: string[]): string[] {
  const updatedHistory = [currentPassword, ...passwordHistory];
  return updatedHistory.slice(0, PASSWORD_HISTORY_LIMIT);
}
