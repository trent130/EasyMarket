"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { profileApi } from '../../../src/services/api/profileApi';
import { User } from '../../../src/types/common';
import { handleApiError } from '../../../src/utils/errorHandling';
import { Profile } from '../../../src/components/Profile/Profile';
import React from 'react';

export default function UserProfile() {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    useEffect(() => {
        loadUserProfile();
    }, []);

    async function loadUserProfile() {
        try {
            const response = await fetch('/api/user/profile');
            if (!response.ok) {
                throw new Error('Failed to load profile');
            }
            const userData = await response.json();
            setUser(userData);
        } catch (err) {
            setError(handleApiError(err));
            router.push('/auth/signin');
        } finally {
            setLoading(false);
        }
    }

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div className="error-message">{error}</div>;
    }

    return (
        <div className="profile-page-container">
            {user && React.createElement(Profile, { user: user, onUpdate: loadUserProfile })}
        </div>
    );
}
