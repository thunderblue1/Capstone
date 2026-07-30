/**
 * Resolves a safe return path to previous search results.
 * Prefers an inherited `from` location state, then the current /search URL.
 */
export function resolveSearchReturnPath(location: {
  pathname: string;
  search: string;
  state: unknown;
}): string | undefined {
  const inheritedFrom = (location.state as { from?: string } | null)?.from;
  if (inheritedFrom?.startsWith('/search')) {
    return inheritedFrom;
  }
  if (location.pathname.startsWith('/search')) {
    return `${location.pathname}${location.search}`;
  }
  return undefined;
}

/** Destination for "Continue Shopping" links; falls back to unfiltered search. */
export function getContinueShoppingPath(location: {
  pathname: string;
  search: string;
  state: unknown;
}): string {
  return resolveSearchReturnPath(location) ?? '/search';
}
