'use client';

import Link from "next/link";


export default function NotFound() {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <h1 className="text-4xl font-bold mb-4">404 - Page Not Found</h1>
        <p className="text-gray-600">The page you are looking for does not exist.</p>
        <Link href="/" className="mt-4 text-blue-500 hover:underline">
          Return to Home
        </Link>
      </div>
    );
  }