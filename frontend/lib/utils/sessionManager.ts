import { redis } from '@/lib/redis/mockRedis';
import { v4 as uuidv4 } from 'uuid';

const SESSION_EXPIRY = 24 * 60 * 60; // 24 hours in seconds

export async function createSession(userId: string): Promise<string> {
  const sessionId = uuidv4();
  await redis.set(`session:${sessionId}`, userId, 'EX', SESSION_EXPIRY);
  return sessionId;
}

export async function getSession(sessionId: string): Promise<string | null> {
  return await redis.get(`session:${sessionId}`);
}

export async function deleteSession(sessionId: string): Promise<void> {
  await redis.del(`session:${sessionId}`);
}

export async function refreshSession(sessionId: string): Promise<void> {
  const userId = await getSession(sessionId);
  if (userId) {
    await redis.set(`session:${sessionId}`, userId, 'EX', SESSION_EXPIRY);
  }
}
