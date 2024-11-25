"use client";

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';

const SECURITY_QUESTIONS = [
  "What was the name of your first pet?",
  "In what city were you born?",
  "What is your mother's maiden name?",
  "What high school did you attend?",
  "What was the make of your first car?",
  "What is your favorite movie?",
];

export default function SecurityQuestions() {
  const [questions, setQuestions] = useState(['', '', '']);
  const [answers, setAnswers] = useState(['', '', '']);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
    } else if (status === 'authenticated') {
      checkExistingQuestions();
    }
  }, [status, router]);

  const checkExistingQuestions = async () => {
    try {
      const response = await fetch('/api/auth/security-questions');
      const data = await response.json();

      if (data.hasSecurityQuestions) {
        setSuccess('You have already set up your security questions.');
      }
    } catch (error) {
      console.error('Error checking existing questions:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (questions.some(q => !q) || answers.some(a => !a)) {
      setError('Please fill in all questions and answers');
      return;
    }

    try {
      const response = await fetch('/api/auth/security-questions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          securityQuestions: questions.map((question, index) => ({
            question,
            answer: answers[index],
          })),
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(data.message);
      } else {
        setError(data.error || 'An error occurred');
      }
    } catch (error) {
      setError('An error occurred. Please try again.');
    }
  };

  return (
    <div className="max-w-md mx-auto mt-8">
      <h1 className="text-2xl font-bold mb-4">Set Up Security Questions</h1>
      {success ? (
        <p className="text-green-500">{success}</p>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          {[0, 1, 2].map((index) => (
            <div key={index}>
              <select
                value={questions[index]}
                onChange={(e) => setQuestions(questions.map((q, i) => i === index ? e.target.value : q))}
                className="w-full p-2 border rounded"
              >
                <option value="">Select a question</option>
                {SECURITY_QUESTIONS.map((q) => (
                  <option key={q} value={q}>
                    {q}
                  </option>
                ))}
              </select>
              <input
                type="text"
                value={answers[index]}
                onChange={(e) => setAnswers(answers.map((a, i) => i === index ? e.target.value : a))}
                placeholder="Your answer"
                className="w-full mt-2 p-2 border rounded"
              />
            </div>
          ))}
          {error && <p className="text-red-500">{error}</p>}
          <button type="submit" className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600">
            Set Security Questions
          </button>
        </form>
      )}
    </div>
  );
}
