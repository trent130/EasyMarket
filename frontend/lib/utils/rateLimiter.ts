const WINDOW_SIZE = 15 * 60 * 1000; // 15 minutes
const MAX_REQUESTS_PER_IP = 100;
const MAX_REQUESTS_PER_USER = 5;
const LOCKOUT_DURATION = 30 * 60 * 1000; // 30 minutes

interface RateLimitEntry {
  count: number;
  firstRequest: number;
  lockedUntil?: number;
}

const ipRateLimitMap = new Map<string, RateLimitEntry>();
const userRateLimitMap = new Map<string, RateLimitEntry>();

export function rateLimit(key: string, isIp: boolean = false): { allowed: boolean; lockedUntil?: number } {
  const now = Date.now();
  const map = isIp ? ipRateLimitMap : userRateLimitMap;
  const maxRequests = isIp ? MAX_REQUESTS_PER_IP : MAX_REQUESTS_PER_USER;
  
  const entry = map.get(key) || { count: 0, firstRequest: now };

  if (entry.lockedUntil && now < entry.lockedUntil) {
    return { allowed: false, lockedUntil: entry.lockedUntil };
  }

  if (now - entry.firstRequest > WINDOW_SIZE) {
    entry.count = 1;
    entry.firstRequest = now;
  } else {
    entry.count++;
  }

  if (entry.count > maxRequests) {
    entry.lockedUntil = now + LOCKOUT_DURATION;
    map.set(key, entry);
    return { allowed: false, lockedUntil: entry.lockedUntil };
  }

  map.set(key, entry);
  return { allowed: true };
}

export function getClientIp(req: Request): string {
  const forwardedFor = req.headers.get('x-forwarded-for');
  if (forwardedFor) {
    return forwardedFor.split(',')[0].trim();
  }
  return 'unknown';
}

export function resetRateLimit(key: string, isIp: boolean = false): void {
  const map = isIp ? ipRateLimitMap : userRateLimitMap;
  map.delete(key);
}
