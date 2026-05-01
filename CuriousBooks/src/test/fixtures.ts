import type { Book } from '../services/types';

export function createMockBook(overrides: Partial<Book> = {}): Book {
  const now = new Date().toISOString();
  return {
    id: 'book-1',
    title: 'Test Book',
    author: 'Test Author',
    isbn: '9780000000000',
    publisher: 'Test Publisher',
    publicationDate: '2020-01-01',
    language: 'en',
    genre: 'Fiction',
    description: 'Test description for unit tests.',
    pageCount: 100,
    price: 9.99,
    currency: 'USD',
    stockQuantity: 10,
    imageUrl: '',
    averageRating: 4,
    reviewCount: 2,
    popularityScore: 1,
    categoryId: null,
    createdAt: now,
    updatedAt: now,
    ...overrides,
  };
}
