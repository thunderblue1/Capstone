import { vi } from 'vitest';
import { createMockBook } from './fixtures';

const mockBook = createMockBook();

const emptyBooksResponse = {
  books: [mockBook],
  total: 1,
  pages: 1,
  currentPage: 1,
  perPage: 20,
  hasNext: false,
  hasPrev: false,
};

const emptySearchResponse = {
  results: [mockBook],
  total: 1,
  pages: 1,
  currentPage: 1,
  query: '',
};

const emptyRecommendationsResponse = {
  recommendations: [mockBook],
  algorithm: 'popularity',
  personalized: false,
};

export function createMockApiModule() {
  return {
    booksApi: {
      getAll: vi.fn().mockResolvedValue(emptyBooksResponse),
      getFeatured: vi.fn().mockResolvedValue([mockBook]),
      search: vi.fn().mockResolvedValue(emptySearchResponse),
      getByCategory: vi.fn().mockResolvedValue({
        ...emptyBooksResponse,
        category: { id: 1, name: 'Fiction', parentId: null },
      }),
      getById: vi.fn().mockResolvedValue(mockBook),
      getReviews: vi.fn().mockResolvedValue({
        reviews: [],
        total: 0,
        pages: 0,
        currentPage: 1,
        averageRating: 0,
        reviewCount: 0,
      }),
      getGenres: vi.fn().mockResolvedValue(['Fiction']),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
    },
    categoriesApi: {
      getAll: vi.fn().mockResolvedValue([{ id: 1, name: 'Fiction', parentId: null }]),
      getById: vi.fn().mockResolvedValue({ id: 1, name: 'Fiction', parentId: null }),
      getByName: vi.fn().mockResolvedValue({ id: 1, name: 'Fiction', parentId: null }),
      getBooks: vi.fn().mockResolvedValue({
        ...emptyBooksResponse,
        category: { id: 1, name: 'Fiction', parentId: null },
      }),
    },
    recommendationsApi: {
      get: vi.fn().mockResolvedValue(emptyRecommendationsResponse),
      getPersonalized: vi.fn().mockResolvedValue({ ...emptyRecommendationsResponse, personalized: true }),
      getSimilar: vi.fn().mockResolvedValue({ book: mockBook, similar: [mockBook], algorithm: 'content_heuristic' }),
      getSearchBased: vi.fn().mockResolvedValue({ ...emptyRecommendationsResponse, algorithm: 'search_context', query: '' }),
    },
    authApi: {
      register: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
      refresh: vi.fn(),
      getCurrentUser: vi.fn(),
      updateProfile: vi.fn(),
      changePassword: vi.fn(),
    },
    reviewsApi: {
      getAll: vi.fn().mockResolvedValue({ reviews: [], total: 0, pages: 0, currentPage: 1 }),
      getById: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
      getByBook: vi.fn().mockResolvedValue({
        bookId: mockBook.id,
        reviews: [],
        total: 0,
        pages: 0,
        currentPage: 1,
        averageRating: 0,
        reviewCount: 0,
      }),
    },
    ordersApi: {
      getAll: vi.fn().mockResolvedValue({ orders: [], total: 0, pages: 0, currentPage: 1 }),
      getById: vi.fn(),
      checkout: vi.fn(),
      pay: vi.fn(),
      cancel: vi.fn(),
      validateCart: vi.fn().mockResolvedValue({ valid: true, items: [], subtotal: 0, tax: 0, total: 0 }),
      getStripeConfig: vi.fn().mockResolvedValue({ publishableKey: 'pk_test_mock' }),
      createStripeIntent: vi.fn(),
      confirmStripePayment: vi.fn(),
    },
    api: {},
  };
}
