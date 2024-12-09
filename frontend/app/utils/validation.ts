export function isValidSlug(slug: string): boolean {
    // Basic slug validation
    const slugRegex = /^[a-z0-9]+(-[a-z0-9]+)*$/;
    return slugRegex.test(slug);
}