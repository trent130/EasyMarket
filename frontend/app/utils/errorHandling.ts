import axios from 'axios';

export class ApiError extends Error {
    public status: number;
    public details?: unknown;

    constructor(
        status: number, 
        message: string, 
        details?: unknown
    ) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.details = details;
    }
}

export function handleApiError(error: unknown): string {
    // Check if it's an axios error or a custom ApiError
    if (error instanceof ApiError) {
        switch (error.status) {
            case 400:
                return 'Invalid request. Please check your input.';
            case 401:
                return 'Unauthorized. Please log in again.';
            case 403:
                return 'You do not have permission to perform this action.';
            case 404:
                return 'The requested resource was not found.';
            case 500:
                return 'An internal server error occurred. Please try again later.';
            default:
                return error.message || 'An unexpected error occurred.';
        }
    }

    // Handle axios errors
    if (axios.isAxiosError(error)) {
        const axiosError = error;
        if (axiosError.response) {
            // The request was made and the server responded with a status code
            return handleApiError(
                new ApiError(
                    axiosError.response.status, 
                    axiosError.response.data?.message || 'An error occurred',
                    axiosError.response.data
                )
            );
        } else if (axiosError.request) {
            // The request was made but no response was received
            return 'No response received from the server. Please check your internet connection.';
        } else {
            // Something happened in setting up the request
            return 'Error setting up the request. Please try again.';
        }
    }

    // Handle other types of errors
    if (error instanceof Error) {
        return error.message || 'An unexpected error occurred.';
    }

    // Fallback for unhandled error types
    return 'An unknown error occurred.';
}

// Utility function for logging errors
export function logError(error: unknown, context?: string) {
    const errorMessage = handleApiError(error);
    console.error(`${context ? `[${context}] ` : ''}${errorMessage}`, error);
}

// Custom error handler for React components
export function createErrorHandler(context?: string) {
    return (error: unknown) => {
        const errorMessage = handleApiError(error);
        // You can add additional error reporting logic here
        // For example, sending error to a monitoring service
        logError(error, context);
        return errorMessage;
    };
}