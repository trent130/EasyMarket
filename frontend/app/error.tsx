'use client';

import { useEffect } from 'react';
import { Button } from './components/ui/button';

export default function GlobalErrorBoundary({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        // Log the error to an error reporting service
        console.error('Global Error:', error);
    }, [error]);

    return (
        <div className="error-page">
            <h2>Something went wrong!</h2>
            <p>{error.message}</p>
            <Button onClick={() => reset()}>
                Try again
            </Button>
        </div>
    );
}