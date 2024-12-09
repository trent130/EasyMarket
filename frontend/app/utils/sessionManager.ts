import { redis } from '../../lib/redis/mockRedis';
import { v4 as uuidv4 } from 'uuid';

const SESSION_EXPIRY = 24 * 60 * 60; // 24 hours in seconds

/**
 * Creates a new session for a user.
 * @param userId The ID of the user that the session is for.
 * @returns A newly generated session ID.
 */
export async function createSession(userId: string): Promise<string> {
  const sessionId = uuidv4();
  await redis.set(`session:${sessionId}`, userId, 'EX', SESSION_EXPIRY);
  return sessionId;
}

/**
 * Retrieves the user ID associated with a given session ID.
 * @param sessionId The session ID to look up.
 * @returns The user ID associated with the session ID, or null if no session is found.
 */
export async function getSession(sessionId: string): Promise<string | null> {
  return await redis.get(`session:${sessionId}`);
}

/**
 * Deletes a session by ID.
 * @param sessionId The ID of the session to delete.
 * @returns A promise that resolves when the session has been deleted.
 */
export async function deleteSession(sessionId: string): Promise<void> {
  await redis.del(`session:${sessionId}`);
}

/**
 * Refreshes the expiration time of an existing session.
 * 
 * @param sessionId - The ID of the session to refresh.
 * @returns A promise that resolves when the session has been refreshed. 
 * If the session does not exist, no action is taken.
 */
export async function refreshSession(sessionId: string): Promise<void> {
  const userId = await getSession(sessionId);
  if (userId) {
    await redis.set(`session:${sessionId}`, userId, 'EX', SESSION_EXPIRY);
  }
}
