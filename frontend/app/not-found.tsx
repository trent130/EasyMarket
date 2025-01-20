'use client';

import { CloudFog, Compass } from "lucide-react";
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="relative min-h-screen overflow-hidden flex items-center justify-center">
      {/* Animated fog effect */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-t from-white/5 to-transparent animate-pulse" />
        <div className="absolute inset-0 opacity-50">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="absolute inset-0 transform animate-float text-black"
              style={{
                animation: `float ${20 + i * 4}s linear infinite`,
                animationDelay: `${i * -10}s`,
                opacity: 0.1
              }}
            >
              <div className="h-full w-full bg-gradient-to-br from-white/20 to-transparent rounded-full blur-3xl" />
            </div>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="relative z-10 text-center px-4">
        <div className="mb-8 flex justify-center">
          <CloudFog className="h-24 w-24 text-slate-400 animate-pulse" />
        </div>
        <h1 className="text-7xl font-bold text-white mb-4">404</h1>
        <h2 className="text-3xl font-semibold text-slate-300 mb-6">Lost in the Fog</h2>
        <p className="text-slate-400 max-w-md mx-auto mb-8">
          The page you're looking for seems to have vanished into the mist. Let's help you find your way back.
        </p>
        <Link
          href="/home"
          className="inline-flex items-center px-6 py-3 text-lg font-medium text-white bg-slate-700/50 rounded-full hover:bg-slate-600/50 transition-colors duration-200 backdrop-blur-sm group"
        >
          <Compass className="mr-2 h-5 w-5 group-hover:animate-spin" />
          Navigate Home
        </Link>
      </div>
    </div>
  );
}