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

/**
 * Page to set up security questions for a user.
 *
 * This page allows an authenticated user to set up security questions and
 * answers for their account. The user is presented with a form containing three
 * questions and answer fields. The user can select a question from a list of
 * predefined questions and enter an answer for that question. If the user has
 * already set up their security questions, they are informed of this and no form
 * is presented.
 *
 * After the user submits the form, the security questions and answers are
 * validated and stored in the database. If the validation fails, an error
 * message is displayed to the user. If the validation succeeds, the user is
 * informed of the success and the page is rendered again with a success message.
 */

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

/**
 * Checks if the user has already set up security questions.
 *
 * This function sends a request to the server to determine if the user
 * has set up security questions. If the user has set up security questions,
 * a success message is displayed indicating that the setup is complete.
 * In case of an error during the request, the error is logged to the console.
 */
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

  /**
   * Handles the form submission by sending the security questions and answers
   * to the server to be stored. If the user has not filled in all questions and
   * answers, an error is displayed. If the request to the server fails, an
   * error is displayed. If the request succeeds, a success message is
   * displayed.
   *
   * @param {React.FormEvent} e - The form event
   */
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
