/**
 * Resolve book cover filenames (from API imageUrl) to bundled asset URLs.
 * Covers live in src/assets/book_cover_images/; imageUrl is a filename only.
 */

const DEFAULT_COVER_FILENAME = 'default.jpg';

const coverModules = import.meta.glob('../assets/book_cover_images/*.{jpg,jpeg,png,webp,JPG,JPEG,PNG,WEBP}', {
  eager: true,
  query: '?url',
  import: 'default',
}) as Record<string, string>;

const coversByFilename: Record<string, string> = {};
for (const [path, url] of Object.entries(coverModules)) {
  const filename = path.replace(/\\/g, '/').split('/').pop();
  if (filename) {
    coversByFilename[filename] = url;
  }
}

/** Basename of a cover value that may accidentally include a path. */
export function coverFilename(imageUrl: string | null | undefined): string {
  if (!imageUrl) return DEFAULT_COVER_FILENAME;
  const filename = imageUrl.replace(/\\/g, '/').split('/').pop()?.trim();
  return filename || DEFAULT_COVER_FILENAME;
}

/**
 * Returns a Vite-resolved asset URL for the cover file, or null when the
 * cover is missing/default or not present under assets/book_cover_images.
 */
export function resolveBookCoverUrl(imageUrl: string | null | undefined): string | null {
  const filename = coverFilename(imageUrl);
  if (filename === DEFAULT_COVER_FILENAME) return null;
  return coversByFilename[filename] ?? null;
}

export { DEFAULT_COVER_FILENAME };
