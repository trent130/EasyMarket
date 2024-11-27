interface FetchOptions extends RequestInit {
    params?: Record<string, string | number>;
}

export async function fetchWrapper<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
    const { params, ...fetchOptions } = options;
    
    // Build URL with query parameters
    const url = new URL(endpoint, process.env.REACT_APP_API_BASE_URL);
    if (params) {
        Object.entries(params).forEach(([key, value]) => {
            url.searchParams.append(key, String(value));
        });
    }

    // Add default headers
    const headers = {
        'Content-Type': 'application/json',
        ...fetchOptions.headers,
    };

    try {
        const response = await fetch(url.toString(), {
            ...fetchOptions,
            headers,
            credentials: 'include', // Include cookies
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }

        return response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
} 