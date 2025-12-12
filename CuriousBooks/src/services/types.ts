/**
 * Type definitions for CuriousBooks API
 * These interfaces match the backend API responses
 */

export interface Book {
  id: string;
  title: string;
  author: string;
  isbn: string;
  publisher: string;
  publicationDate: string;
  language: string;
  genre: string;
  description: string;
  pageCount: number;
  price: number;
  currency: string;
  stockQuantity: number;
  imageUrl: string;
  averageRating: number;
  reviewCount: number;
  popularityScore: number;
  categoryId: number | null;
  createdAt: string;
  updatedAt: string;
  category?: Category;
}

export interface Category {
  id: number;
  name: string;
  parentId: number | null;
  parent?: Category;
  subcategories?: Category[];
}

export interface Review {
  id: string;
  bookId: string;
  userId?: string;
  reviewerName: string;
  rating: number;
  text: string;
  date: string;
  book?: Book;
}

export interface User {
  id: string;
  username: string;
  email?: string;
  firstName: string | null;
  lastName: string | null;
  createdAt: string;
}

export interface OrderItem {
  id: string;
  orderId: string;
  bookId: string;
  quantity: number;
  unitPrice: number;
  subtotal: number;
  book?: Book;
}

export interface Order {
  id: string;
  userId: string;
  totalAmount: number;
  currency: string;
  status: 'Pending' | 'Paid' | 'Shipped' | 'Delivered' | 'Cancelled';
  createdAt: string;
  updatedAt: string;
  items: OrderItem[];
  user?: User;
}

export interface CartItem {
  bookId: string;
  quantity: number;
}

export interface CartValidation {
  valid: boolean;
  items: ValidatedCartItem[];
  subtotal: number;
  tax: number;
  total: number;
  errors?: CartError[];
}

export interface ValidatedCartItem {
  bookId: string;
  book: Book;
  quantity: number;
  unitPrice: number;
  subtotal: number;
  available: number;
  valid: boolean;
}

export interface CartError {
  bookId?: string;
  error: string;
}

export interface AuthResponse {
  message: string;
  user: User;
  accessToken: string;
  refreshToken: string;
}

export interface PaginatedResponse<T> {
  total: number;
  pages: number;
  currentPage: number;
  perPage?: number;
  hasNext?: boolean;
  hasPrev?: boolean;
  items?: T[];
}

export interface BooksResponse extends PaginatedResponse<Book> {
  books: Book[];
}

export interface SearchResponse extends PaginatedResponse<Book> {
  results: Book[];
  query: string;
}

export interface ReviewsResponse extends PaginatedResponse<Review> {
  reviews: Review[];
  averageRating: number;
  reviewCount: number;
  bookId?: string;
}

export interface CategoriesResponse {
  categories: Category[];
}

export interface RecommendationsResponse {
  recommendations: Book[];
  algorithm: string;
  personalized: boolean;
  basedOn?: {
    genres: string[];
    categoryIds: number[];
  };
}

export interface SimilarBooksResponse {
  book: Book;
  similar: Book[];
  algorithm: string;
}

