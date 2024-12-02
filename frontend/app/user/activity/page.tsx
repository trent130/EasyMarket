"use client";

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';

interface ActivityLog {
  timestamp: number;
  action: string;
  details: string;
}

export default function UserActivity() {
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([]);
  const [error, setError] = useState('');
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
    } else if (status === 'authenticated') {
      fetchActivityLogs();
    }
  }, [status, router]);

  const fetchActivityLogs = async () => {
    try {
      const response = await fetch('/api/user/activity');
      if (response.ok) {
        const data = await response.json();
        setActivityLogs(data);
      } else {
        setError('Failed to fetch activity logs');
      }
    } catch (error) {
      setError('An error occurred while fetching activity logs');
    }
  };

  if (status === 'loading') {
    return <div>Loading...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto mt-8 p-4">
      <h1 className="text-2xl font-bold mb-4">Your Account Activity</h1>
      {error && <p className="text-red-500 mb-4">{error}</p>}
      <ul className="space-y-4">
        {activityLogs.map((log, index) => (
          <li key={index} className="border p-4 rounded-lg">
            <p><strong>Action:</strong> {log.action}</p>
            <p><strong>Details:</strong> {log.details}</p>
            <p><strong>Time:</strong> {new Date(log.timestamp).toLocaleString()}</p>
          </li>
        ))}
      </ul>
      {activityLogs.length === 0 && <p>No activity logs found.</p>}
    </div>
  );
}
