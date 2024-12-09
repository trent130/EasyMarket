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


/**
 * Checks if a given key is within the rate limit, and if not, locks them out for a duration.
 * @param key The key to check.
 * @param isIp Whether the key is an IP address (true) or a user ID (false).
 * @returns An object with a boolean indicating whether the request was allowed, and optionally a timestamp indicating when the lockout will expire.
 */
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

/**
 * Gets the client's IP address from the request headers.
 *
 * If the request is being proxied, the IP address is obtained from the
 * `X-Forwarded-For` header. Otherwise, the IP address is unknown.
 */
export function getClientIp(req: Request): string {
  const forwardedFor = req.headers.get('x-forwarded-for');
  if (forwardedFor) {
    return forwardedFor.split(',')[0].trim();
  }
  return 'unknown';
}

/**
 * Resets the rate limit for a given key.
 *
 * @param key The key to reset.
 * @param isIp Whether the key is an IP address (true) or a user ID (false).
 */
export function resetRateLimit(key: string, isIp: boolean = false): void {
  const map = isIp ? ipRateLimitMap : userRateLimitMap;
  map.delete(key);
}
