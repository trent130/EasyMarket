import { compare } from 'bcrypt';

const PASSWORD_HISTORY_LIMIT = 5;

/**
 * Checks if a new password is reused based on the given password history.
 * @param newPassword - The new password to check.
 * @param passwordHistory - The password history to check against.
 * @returns True if the new password is reused, false otherwise.
 */
export async function isPasswordReused(newPassword: string, passwordHistory: string[]): Promise<boolean> {
  for (const oldPassword of passwordHistory) {
    if (await compare(newPassword, oldPassword)) {
      return true;
    }
  }
  return false;
}

/**
 * Updates the password history by prepending the current password and limiting the history to a maximum size.
 * @param currentPassword - The current password to prepend to the history.
 * @param passwordHistory - The password history to update.
 * @returns The updated password history with the current password and limited to the maximum size.
 */
export function updatePasswordHistory(currentPassword: string, passwordHistory: string[]): string[] {
  const updatedHistory = [currentPassword, ...passwordHistory];
  return updatedHistory.slice(0, PASSWORD_HISTORY_LIMIT);
}
