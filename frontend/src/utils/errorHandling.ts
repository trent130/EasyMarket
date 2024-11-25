export class ApiError extends Error {
    constructor(
        public status: number,
        public message: string,
        public details?: any
    ) {
        super(message);
        this.name = 'ApiError';
    }
}

export function handleApiError(error: any) {
    if (error instanceof ApiError) {
        // Handle specific API errors
        switch (error.status) {
            case 401:
                // Handle unauthorized
                break;
            case 403:
                // Handle forbidden
                break;
            case 404:
                // Handle not found
                break;
            default:
                // Handle other errors
                break;
        }
    }
    
    // Log error for debugging
    console.error('API Error:', error);
    
    // Return user-friendly message
    return 'An error occurred. Please try again later.';
} 