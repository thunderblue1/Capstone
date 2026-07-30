/**
 * Helpers for post-login return navigation via `?redirect=`.
 */

/** Only allow same-app relative paths (blocks open redirects). */
export function getSafeRedirectPath(redirect: string | null | undefined): string {
  if (!redirect || !redirect.startsWith('/') || redirect.startsWith('//')) {
    return '/';
  }
  if (redirect === '/login' || redirect.startsWith('/login?')) {
    return '/';
  }
  return redirect;
}

/** Build a login URL that returns the user to `returnTo` after auth. */
export function buildLoginPath(returnTo?: string): string {
  const safe = getSafeRedirectPath(returnTo);
  if (safe === '/') {
    return '/login';
  }
  return `/login?redirect=${encodeURIComponent(safe)}`;
}
