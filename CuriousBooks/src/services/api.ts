/**
 * CuriousBooks API Service
 * ========================
 * 
 * Purpose:
 *   Centralized API client for all communication with the Flask backend.
 *   Provides typed interfaces for all API endpoints with automatic
 *   authentication token management.
 * 
 * Architecture:
 *   - Base URL configured via VITE_API_URL environment variable
 *   - JWT tokens stored in localStorage (access + refresh)
 *   - Automatic token refresh on 401 responses
 *   - Consistent error handling via ApiError class
 * 
 * API Modules:
 *   - booksApi: Book listing, search, and details
 *   - categoriesApi: Category listing and book filtering
 *   - authApi: Authentication (login, register, logout)
 *   - reviewsApi: Review CRUD operations
 *   - ordersApi: Cart validation and checkout
 *   - recommendationsApi: Book recommendations
 * 
 * Authentication Flow:
 *   1. Login/Register returns access and refresh tokens
 *   2. Access token added to Authorization header automatically
 *   3. On 401, refresh token used to get new access token
 *   4. On refresh failure, tokens cleared (user logged out)
 * 
 * Usage:
 *   import { booksApi, authApi } from './services/api';
 *   const books = await booksApi.getFeatured(4);
 *   const user = await authApi.login(email, password);
 * 
 * Error Handling:
 *   All methods throw ApiError on failure with status code and message.
 *   Catch and handle in components:
 *   try {
 *     await api.books.getById(id);
 *   } catch (err) {
 *     if (err instanceof ApiError && err.status === 404) { ... }
 *   }
 */

import type {
  Book,
  Category,
  Review,
  User,
  Order,
  CartItem,
  CartValidation,
  AuthResponse,
  BooksResponse,
  SearchResponse,
  ReviewsResponse,
  CategoriesResponse,
  RecommendationsResponse,
  SimilarBooksResponse,
} from './types';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
const API_KEY = import.meta.env.VITE_API_KEY as string | undefined;

// Token storage keys
const ACCESS_TOKEN_KEY = 'curiousbooks_access_token';
const REFRESH_TOKEN_KEY = 'curiousbooks_refresh_token';

/**
 * Get stored access token
 */
function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

/**
 * Get stored refresh token
 */
function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Store tokens
 */
function setTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

/**
 * Clear tokens (logout)
 */
function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

/**
 * Base fetch wrapper with error handling and auth
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (API_KEY) {
    (headers as Record<string, string>)['X-API-Key'] = API_KEY;
  }

  // Add auth token if available
  const token = getAccessToken();
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch (error: any) {
    // Handle network errors (connection refused, timeout, etc.)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new ApiError(
        0,
        `Cannot connect to server. Make sure the backend is running at ${API_BASE_URL}`
      );
    }
    throw new ApiError(0, error.message || 'Network error occurred');
  }

  // Handle 401 - try to refresh token
  if (response.status === 401 && getRefreshToken()) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      // Retry the request with new token
      (headers as Record<string, string>)['Authorization'] = `Bearer ${getAccessToken()}`;
      const retryResponse = await fetch(url, { ...options, headers });
      if (!retryResponse.ok) {
        throw new ApiError(retryResponse.status, await retryResponse.text());
      }
      return retryResponse.json();
    }
  }

  if (!response.ok) {
    let errorMessage: string;
    try {
      const errorData = await response.json();
      errorMessage = errorData.error || errorData.message || 'An error occurred';
    } catch {
      errorMessage = response.statusText;
    }
    throw new ApiError(response.status, errorMessage);
  }

  return response.json();
}

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Refresh the access token
 */
async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${refreshToken}`,
      },
    });

    if (!response.ok) {
      clearTokens();
      return false;
    }

    const data = await response.json();
    localStorage.setItem(ACCESS_TOKEN_KEY, data.accessToken);
    return true;
  } catch {
    clearTokens();
    return false;
  }
}

// ============================================
// BOOKS API
// ============================================

export const booksApi = {
  /**
   * Get all books with optional filtering and pagination
   */
  getAll: async (params?: {
    page?: number;
    perPage?: number;
    categoryId?: number;
    genre?: string;
    minPrice?: number;
    maxPrice?: number;
    inStock?: boolean;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
  }): Promise<BooksResponse> => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          // Convert camelCase to snake_case
          const snakeKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
          searchParams.set(snakeKey, String(value));
        }
      });
    }
    const query = searchParams.toString();
    return apiFetch<BooksResponse>(`/books${query ? `?${query}` : ''}`);
  },

  /**
   * Get featured books
   */
  getFeatured: async (limit = 4): Promise<Book[]> => {
    const response = await apiFetch<{ books: Book[] }>(`/books/featured?limit=${limit}`);
    return response.books;
  },

  /**
   * Search books
   */
  search: async (query: string, page = 1, perPage = 20): Promise<SearchResponse> => {
    return apiFetch<SearchResponse>(
      `/books/search?q=${encodeURIComponent(query)}&page=${page}&per_page=${perPage}`
    );
  },

  /**
   * Get books by category name
   */
  getByCategory: async (categoryName: string, page = 1, perPage = 20): Promise<BooksResponse> => {
    return apiFetch<BooksResponse>(
      `/books/category/${encodeURIComponent(categoryName)}?page=${page}&per_page=${perPage}`
    );
  },

  /**
   * Get a single book by ID
   */
  getById: async (id: string): Promise<Book> => {
    return apiFetch<Book>(`/books/${id}`);
  },

  /**
   * Get reviews for a book
   */
  getReviews: async (bookId: string, page = 1, perPage = 10): Promise<ReviewsResponse> => {
    return apiFetch<ReviewsResponse>(
      `/books/${bookId}/reviews?page=${page}&per_page=${perPage}`
    );
  },

  /**
   * Get all unique genres
   */
  getGenres: async (): Promise<string[]> => {
    const response = await apiFetch<{ genres: string[] }>('/books/genres');
    return response.genres;
  },

  /**
   * Create a new book (Manager only)
   */
  create: async (bookData: {
    title: string;
    author: string;
    isbn13: string;
    price: number;
    publisher?: string;
    publicationDate?: string;
    language?: string;
    genre?: string;
    description?: string;
    pageCount?: number;
    currency?: string;
    stockQuantity?: number;
    coverImageUrl?: string;
    categoryId?: number;
  }): Promise<{ message: string; book: Book }> => {
    return apiFetch('/books', {
      method: 'POST',
      body: JSON.stringify(bookData),
    });
  },

  /**
   * Update an existing book (Manager only)
   */
  update: async (bookId: string, bookData: Partial<{
    title: string;
    author: string;
    isbn13: string;
    publisher: string;
    publicationDate: string;
    language: string;
    genre: string;
    description: string;
    pageCount: number;
    price: number;
    currency: string;
    stockQuantity: number;
    coverImageUrl: string;
    categoryId: number;
  }>): Promise<{ message: string; book: Book }> => {
    return apiFetch(`/books/${bookId}`, {
      method: 'PUT',
      body: JSON.stringify(bookData),
    });
  },

  /**
   * Delete a book (Manager only)
   */
  delete: async (bookId: string): Promise<{ message: string }> => {
    return apiFetch(`/books/${bookId}`, {
      method: 'DELETE',
    });
  },
};

// ============================================
// CATEGORIES API
// ============================================

export const categoriesApi = {
  /**
   * Get all categories
   */
  getAll: async (options?: { rootOnly?: boolean; includeSubcategories?: boolean }): Promise<Category[]> => {
    const params = new URLSearchParams();
    if (options?.rootOnly) params.set('root_only', 'true');
    if (options?.includeSubcategories) params.set('include_subcategories', 'true');
    const query = params.toString();
    const response = await apiFetch<CategoriesResponse>(`/categories${query ? `?${query}` : ''}`);
    return response.categories;
  },

  /**
   * Get a single category by ID
   */
  getById: async (id: number): Promise<Category> => {
    return apiFetch<Category>(`/categories/${id}`);
  },

  /**
   * Get a category by name
   */
  getByName: async (name: string): Promise<Category> => {
    return apiFetch<Category>(`/categories/name/${encodeURIComponent(name)}`);
  },

  /**
   * Get books in a category
   */
  getBooks: async (categoryId: number, page = 1, perPage = 20): Promise<BooksResponse & { category: Category }> => {
    return apiFetch(`/categories/${categoryId}/books?page=${page}&per_page=${perPage}`);
  },
};

// ============================================
// AUTH API
// ============================================

export const authApi = {
  /**
   * Register a new user
   */
  register: async (data: {
    email: string;
    password: string;
    username: string;
    firstName?: string;
    lastName?: string;
  }): Promise<AuthResponse> => {
    const response = await apiFetch<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    setTokens(response.accessToken, response.refreshToken);
    return response;
  },

  /**
   * Login with email and password
   */
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await apiFetch<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    setTokens(response.accessToken, response.refreshToken);
    return response;
  },

  /**
   * Logout - clear tokens
   */
  logout: (): void => {
    clearTokens();
  },

  /**
   * Get current user
   */
  getCurrentUser: async (): Promise<User> => {
    return apiFetch<User>('/auth/me');
  },

  /**
   * Update current user
   */
  updateUser: async (data: {
    firstName?: string;
    lastName?: string;
    username?: string;
  }): Promise<{ message: string; user: User }> => {
    return apiFetch('/auth/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Change password
   */
  changePassword: async (currentPassword: string, newPassword: string): Promise<{ message: string }> => {
    return apiFetch('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ currentPassword, newPassword }),
    });
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: (): boolean => {
    return !!getAccessToken();
  },
};

// ============================================
// REVIEWS API
// ============================================

export const reviewsApi = {
  /**
   * Get reviews with optional filtering
   */
  getAll: async (params?: { bookId?: number; userId?: number; page?: number; perPage?: number }): Promise<ReviewsResponse> => {
    const searchParams = new URLSearchParams();
    if (params) {
      if (params.bookId) searchParams.set('book_id', String(params.bookId));
      if (params.userId) searchParams.set('user_id', String(params.userId));
      if (params.page) searchParams.set('page', String(params.page));
      if (params.perPage) searchParams.set('per_page', String(params.perPage));
    }
    const query = searchParams.toString();
    return apiFetch<ReviewsResponse>(`/reviews${query ? `?${query}` : ''}`);
  },

  /**
   * Get reviews for a specific book
   */
  getByBook: async (bookId: string, page = 1, perPage = 10): Promise<ReviewsResponse> => {
    return apiFetch<ReviewsResponse>(`/reviews/book/${bookId}?page=${page}&per_page=${perPage}`);
  },

  /**
   * Create a new review (requires authentication)
   */
  create: async (bookId: string, rating: number, text?: string): Promise<{ message: string; review: Review }> => {
    return apiFetch('/reviews', {
      method: 'POST',
      body: JSON.stringify({ bookId, rating, text }),
    });
  },

  /**
   * Update a review (requires authentication)
   */
  update: async (reviewId: string, data: { rating?: number; text?: string }): Promise<{ message: string; review: Review }> => {
    return apiFetch(`/reviews/${reviewId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete a review (requires authentication)
   */
  delete: async (reviewId: string): Promise<{ message: string }> => {
    return apiFetch(`/reviews/${reviewId}`, {
      method: 'DELETE',
    });
  },
};

// ============================================
// ORDERS API
// ============================================

export const ordersApi = {
  /**
   * Get user's orders (requires authentication)
   */
  getAll: async (params?: { status?: string; page?: number; perPage?: number }): Promise<{ orders: Order[]; total: number; pages: number; currentPage: number }> => {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set('status', params.status);
    if (params?.page) searchParams.set('page', String(params.page));
    if (params?.perPage) searchParams.set('per_page', String(params.perPage));
    const query = searchParams.toString();
    return apiFetch(`/orders${query ? `?${query}` : ''}`);
  },

  /**
   * Get a single order (requires authentication)
   */
  getById: async (orderId: string): Promise<Order> => {
    return apiFetch<Order>(`/orders/${orderId}`);
  },

  /**
   * Checkout - create order from cart items (requires authentication)
   */
  checkout: async (items: CartItem[]): Promise<{ message: string; order: Order }> => {
    return apiFetch('/orders/checkout', {
      method: 'POST',
      body: JSON.stringify({ items }),
    });
  },

  /**
   * Validate cart without creating order
   */
  validateCart: async (items: CartItem[]): Promise<CartValidation> => {
    return apiFetch<CartValidation>('/orders/cart/validate', {
      method: 'POST',
      body: JSON.stringify({ items }),
    });
  },

  /**
   * Pay for an order (requires authentication)
   */
  pay: async (orderId: string): Promise<{ message: string; order: Order }> => {
    return apiFetch(`/orders/${orderId}/pay`, {
      method: 'POST',
    });
  },

  /**
   * Cancel an order (requires authentication)
   */
  cancel: async (orderId: string): Promise<{ message: string; order: Order }> => {
    return apiFetch(`/orders/${orderId}/cancel`, {
      method: 'POST',
    });
  },

  /**
   * Get Stripe configuration (publishable key)
   */
  getStripeConfig: async (): Promise<{ publishableKey: string }> => {
    return apiFetch('/orders/stripe/config');
  },

  /**
   * Create Stripe payment intent (requires authentication)
   */
  createStripeIntent: async (data: {
    items: CartItem[];
    customerEmail?: string;
    customerName?: string;
    shippingAddress?: {
      line1: string;
      line2?: string;
      city: string;
      state: string;
      postalCode: string;
      country: string;
    };
  }): Promise<{
    clientSecret: string;
    paymentIntentId: string;
    amount: number;
    currency: string;
  }> => {
    return apiFetch('/orders/stripe/create-intent', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Confirm Stripe payment and create order (requires authentication)
   */
  confirmStripePayment: async (data: {
    paymentIntentId: string;
    items: CartItem[];
    customerEmail?: string;
    customerName?: string;
    shippingAddress?: {
      line1: string;
      line2?: string;
      city: string;
      state: string;
      postalCode: string;
      country: string;
    };
  }): Promise<{ message: string; order: Order }> => {
    return apiFetch('/orders/stripe/confirm', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

// ============================================
// RECOMMENDATIONS API
// ============================================

export const recommendationsApi = {
  /**
   * Get general recommendations
   */
  get: async (limit = 8, excludeIds?: string[]): Promise<RecommendationsResponse> => {
    const params = new URLSearchParams();
    params.set('limit', String(limit));
    excludeIds?.forEach(id => params.append('exclude', id));
    return apiFetch<RecommendationsResponse>(`/recommendations?${params.toString()}`);
  },

  /**
   * Get personalized recommendations (requires authentication)
   */
  getPersonalized: async (limit = 8): Promise<RecommendationsResponse> => {
    return apiFetch<RecommendationsResponse>(`/recommendations/personalized?limit=${limit}`);
  },

  /**
   * Get similar books
   */
  getSimilar: async (bookId: string, limit = 4): Promise<SimilarBooksResponse> => {
    return apiFetch<SimilarBooksResponse>(`/recommendations/similar/${bookId}?limit=${limit}`);
  },

  /**
   * Get search-based recommendations
   */
  getSearchBased: async (query: string, limit = 4, excludeIds?: string[]): Promise<RecommendationsResponse> => {
    const params = new URLSearchParams();
    params.set('q', query);
    params.set('limit', String(limit));
    excludeIds?.forEach(id => params.append('exclude', id));
    return apiFetch<RecommendationsResponse>(`/recommendations/search-based?${params.toString()}`);
  },
};

// ============================================
// UNIFIED API OBJECT
// ============================================

export const api = {
  books: booksApi,
  categories: categoriesApi,
  auth: authApi,
  reviews: reviewsApi,
  orders: ordersApi,
  recommendations: recommendationsApi,
};

export default api;

