import zxcvbn from 'zxcvbn';

export interface PasswordStrengthResult {
  score: number;
  feedback: {
    warning: string;
    suggestions: string[];
  };
}

export function checkPasswordStrength(password: string): PasswordStrengthResult {
  const result = zxcvbn(password);
  return {
    score: result.score,
    feedback: result.feedback
  };
}

export function isPasswordStrong(password: string): boolean {
  const result = checkPasswordStrength(password);
  return result.score >= 3; // Considering scores 3 and 4 as strong
}
