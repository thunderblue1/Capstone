import { describe, expect, test } from 'vitest';
import { buildLoginPath, getSafeRedirectPath } from './loginRedirect';

describe('getSafeRedirectPath', () => {
  test('defaults to home for missing or unsafe values', () => {
    expect(getSafeRedirectPath(null)).toBe('/');
    expect(getSafeRedirectPath(undefined)).toBe('/');
    expect(getSafeRedirectPath('https://evil.example')).toBe('/');
    expect(getSafeRedirectPath('//evil.example')).toBe('/');
    expect(getSafeRedirectPath('/login')).toBe('/');
    expect(getSafeRedirectPath('/login?redirect=/cart')).toBe('/');
  });

  test('allows same-app paths including search query', () => {
    expect(getSafeRedirectPath('/cart')).toBe('/cart');
    expect(getSafeRedirectPath('/search?q=fiction')).toBe('/search?q=fiction');
    expect(getSafeRedirectPath('/book/book-1')).toBe('/book/book-1');
  });
});

describe('buildLoginPath', () => {
  test('omits redirect when returning home', () => {
    expect(buildLoginPath('/')).toBe('/login');
    expect(buildLoginPath()).toBe('/login');
    expect(buildLoginPath('/login')).toBe('/login');
  });

  test('includes encoded redirect for previous page', () => {
    expect(buildLoginPath('/cart')).toBe('/login?redirect=%2Fcart');
    expect(buildLoginPath('/search?q=mystery')).toBe(
      '/login?redirect=%2Fsearch%3Fq%3Dmystery',
    );
  });
});
