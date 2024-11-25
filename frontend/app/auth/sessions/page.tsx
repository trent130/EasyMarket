"use client";

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';

interface Session {
  id: string;
  userAgent: string;
  ip: string;
  lastActive: number;
}

export default function ManageSessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [error, setError] = useState('');
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
    } else if (status === 'authenticated') {
      fetchSessions();
    }
  }, [status, router]);

  const fetchSessions = async () => {
    try {
      const response = await fetch('/api/auth/sessions');
      if (response.ok) {
        const data = await response.json();
        setSessions(data);
      } else {
        setError('Failed to fetch sessions');
      }
    } catch (error) {
      setError('An error occurred while fetching sessions');
    }
  };

  const terminateSession = async (sessionId: string) => {
    try {
      const response = await fetch('/api/auth/sessions', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId }),
      });

      if (response.ok) {
        setSessions(sessions.filter(s => s.id !== sessionId));
      } else {
        setError('Failed to terminate session');
      }
    } catch (error) {
      setError('An error occurred while terminating the session');
    }
  };

  if (status === 'loading') {
    return <div>Loading...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto mt-8 p-4">
      <h1 className="text-2xl font-bold mb-4">Manage Active Sessions</h1>
      {error && <p className="text-red-500 mb-4">{error}</p>}
      <ul className="space-y-4">
        {sessions.map((s) => (
          <li key={s.id} className="border p-4 rounded-lg flex justify-between items-center">
            <div>
              <p><strong>Device:</strong> {s.userAgent}</p>
              <p><strong>IP Address:</strong> {s.ip}</p>
              <p><strong>Last Active:</strong> {new Date(s.lastActive).toLocaleString()}</p>
            </div>
            <button
              onClick={() => terminateSession(s.id)}
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            >
              Terminate
            </button>
          </li>
        ))}
      </ul>
      {sessions.length === 0 && <p>No active sessions found.</p>}
    </div>
  );
}
