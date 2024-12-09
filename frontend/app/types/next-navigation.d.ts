
declare module 'next/navigation' {
    export function useParams<T extends Record<string, string> = Record<string, string>>(): T;
}