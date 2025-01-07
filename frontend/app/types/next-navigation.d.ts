
declare module 'next/navigation' {
    export function useParams<T extends Record<string, string> = Record<string, string>>(): T;

  export function get(arg0: string) {
    throw new Error('Function not implemented.');
  }
}