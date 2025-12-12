/**
 * BookSynopsisPage Component
 * ==========================
 * 
 * Purpose:
 *   Displays detailed information about a single book including metadata,
 *   description, pricing, stock status, and customer reviews. Allows users
 *   to add books to cart and submit reviews.
 * 
 * Features:
 *   - Book metadata display (title, author, ISBN, publisher, etc.)
 *   - Star rating display with average and review count
 *   - Price display with out-of-stock indicator
 *   - Add to cart functionality
 *   - Customer reviews list
 *   - Review submission form (authenticated users only)
 * 
 * Data Flow:
 *   1. Extracts book ID from URL params via useParams()
 *   2. Fetches book details via booksApi.getById()
 *   3. Fetches reviews via booksApi.getReviews()
 *   4. Cart actions propagate to parent via onAddToCart prop
 * 
 * Props:
 *   - cartItems: Current cart contents for navbar badge
 *   - onAddToCart: Callback when user clicks "Add to Cart"
 *   - isLoggedIn: Whether user is authenticated
 *   - user: Current user object for review form
 *   - userAvatar: User avatar URL for display
 *   - onLogout: Callback for logout action
 * 
 * Usage:
 *   <Route path="/book/:id" element={<BookSynopsisPage {...props} />} />
 */
import React, { FC, useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import NavBar from '../NavBar/NavBar';
import StarRating from '../StarRating/StarRating';
import Review from '../Review/Review';
import ReviewForm from '../ReviewForm/ReviewForm';
import Footer from '../Footer/Footer';
import { booksApi } from '../../services/api';
import { logger } from '../../services/logger';
import type { Book, Review as ReviewType, User } from '../../services/types';
import './BookSynopsisPage.css';

interface BookSynopsisPageProps {
  cartItems?: Book[];
  onAddToCart?: (book: Book) => void;
  isLoggedIn?: boolean;
  user?: User | null;
  userAvatar?: string | null;
  onLogout?: () => void;
}

const BookSynopsisPage: FC<BookSynopsisPageProps> = ({ 
  cartItems = [], 
  onAddToCart,
  isLoggedIn = false,
  user = null,
  userAvatar = null,
  onLogout,
}) => {
  /* ─────────────────────────────────────────────────────────────
   * URL PARAMS & STATE
   * Extract book ID from route and manage component state
   * ───────────────────────────────────────────────────────────── */
  const { id } = useParams<{ id: string }>();
  const [book, setBook] = useState<Book | null>(null);
  const [reviews, setReviews] = useState<ReviewType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /* ─────────────────────────────────────────────────────────────
   * REVIEW SUBMISSION HANDLER
   * Updates local state when a new review is submitted
   * Recalculates average rating optimistically
   * ───────────────────────────────────────────────────────────── */
  const handleReviewSubmitted = useCallback((newReview: ReviewType) => {
    // Add new review to top of list
    setReviews(prev => [newReview, ...prev]);
    // Update book's review count and recalculate average rating
    if (book) {
      setBook(prev => prev ? { 
        ...prev, 
        reviewCount: prev.reviewCount + 1,
        // Weighted average calculation for new rating
        averageRating: ((prev.averageRating * prev.reviewCount) + newReview.rating) / (prev.reviewCount + 1)
      } : null);
    }
  }, [book]);

  /* ─────────────────────────────────────────────────────────────
   * DATA FETCHING EFFECT
   * Loads book details and reviews when component mounts
   * or when book ID changes
   * ───────────────────────────────────────────────────────────── */
  useEffect(() => {
    const loadBook = async () => {
      if (!id) return;
      
      setIsLoading(true);
      setError(null);
      
      try {
        // Fetch book details from API
        const bookData = await booksApi.getById(id);
        setBook(bookData);
        
        // Fetch reviews for this book
        const reviewsResponse = await booksApi.getReviews(id);
        setReviews(reviewsResponse.reviews);
      } catch (err) {
        // Log error with context for debugging
        logger.error.log(err instanceof Error ? err : 'Failed to load book', {
          component: 'BookSynopsisPage',
          errorCode: 'BOOK_LOAD_ERROR',
          bookId: id,
        });
        setError('Failed to load book details.');
        setBook(null);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadBook();
  }, [id]);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (isLoading) {
    return (
      <div className="book-synopsis-page" data-testid="BookSynopsisPage">
        <NavBar 
          cartItemCount={cartItems.length}
          isLoggedIn={isLoggedIn}
          user={user}
          userAvatar={userAvatar}
          onLogout={onLogout}
        />
        <main className="book-synopsis-page__main">
          <div className="book-synopsis-page__loading">
            <div className="loading-spinner"></div>
            <p>Loading book details...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (error || !book) {
    return (
      <div className="book-synopsis-page" data-testid="BookSynopsisPage">
        <NavBar 
          cartItemCount={cartItems.length}
          isLoggedIn={isLoggedIn}
          user={user}
          userAvatar={userAvatar}
          onLogout={onLogout}
        />
        <main className="book-synopsis-page__main">
          <div className="book-synopsis-page__not-found">
            <h2>Book Not Found</h2>
            <p>{error || "The book you're looking for doesn't exist."}</p>
            <Link to="/" className="btn-primary">Return Home</Link>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="book-synopsis-page" data-testid="BookSynopsisPage">
      <NavBar 
        cartItemCount={cartItems.length}
        isLoggedIn={isLoggedIn}
        user={user}
        userAvatar={userAvatar}
        onLogout={onLogout}
      />
      <main className="book-synopsis-page__main">
        <section className="synopsis-section">
          <div className="synopsis-section__container">
            <div className="synopsis-section__image">
              <div className="book-cover-large">
                {book.imageUrl && !book.imageUrl.includes('default') ? (
                  <img src={book.imageUrl} alt={book.title} className="book-cover-image" />
                ) : (
                  <svg viewBox="0 0 200 280" className="book-cover-placeholder-large">
                    <defs>
                      <linearGradient id={`grad-large-${book.id}`} x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#00bcd4" />
                        <stop offset="100%" stopColor="#4caf50" />
                      </linearGradient>
                    </defs>
                    <rect width="200" height="280" fill={`url(#grad-large-${book.id})`} />
                    <ellipse cx="120" cy="90" rx="40" ry="30" fill="white" opacity="0.9" />
                    <ellipse cx="90" cy="95" rx="30" ry="24" fill="white" opacity="0.9" />
                    <ellipse cx="145" cy="100" rx="25" ry="20" fill="white" opacity="0.9" />
                    <polygon points="0,280 70,180 140,280" fill="#7cb342" />
                    <polygon points="80,280 170,160 200,280" fill="#558b2f" />
                  </svg>
                )}
              </div>
            </div>
            
            <div className="synopsis-section__details">
              <h1 className="book-title">{book.title}</h1>
              
              <div className="book-meta-grid">
                <div className="meta-item">
                  <span className="meta-label">ISBN:</span>
                  <span className="meta-value">{book.isbn}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Author:</span>
                  <span className="meta-value">{book.author}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Publisher:</span>
                  <span className="meta-value">{book.publisher}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Publication Date:</span>
                  <span className="meta-value">{book.publicationDate ? formatDate(book.publicationDate) : 'N/A'}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Language:</span>
                  <span className="meta-value">{book.language}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Genre:</span>
                  <span className="meta-value">{book.genre}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Page Count:</span>
                  <span className="meta-value">{book.pageCount} pages</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Average Rating:</span>
                  <span className="meta-value">
                    <StarRating rating={book.averageRating} size="md" showNumber />
                  </span>
                </div>
              </div>
              
              <div className="book-price-section">
                <span className="price-label">Price:</span>
                <span className="price-value">{formatPrice(book.price)}</span>
                {book.stockQuantity <= 0 && (
                  <span className="out-of-stock">Out of Stock</span>
                )}
              </div>
              
              <div className="book-description">
                <h3>Description</h3>
                <p>{book.description}</p>
              </div>
              
              <div className="book-actions">
                <button 
                  className="btn-accent btn-large"
                  onClick={() => onAddToCart?.(book)}
                  disabled={book.stockQuantity <= 0}
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="9" cy="21" r="1" />
                    <circle cx="20" cy="21" r="1" />
                    <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
                  </svg>
                  {book.stockQuantity > 0 ? 'Add to Cart' : 'Out of Stock'}
                </button>
                <Link to="/search" className="btn-secondary btn-large">
                  Continue Shopping
                </Link>
              </div>
            </div>
          </div>
        </section>

        <section className="reviews-section">
          <div className="reviews-section__container">
            <h2 className="reviews-section__title">Customer Reviews</h2>
            
            {/* Review Form */}
            <ReviewForm
              bookId={book.id}
              bookTitle={book.title}
              user={user}
              isLoggedIn={isLoggedIn}
              onReviewSubmitted={handleReviewSubmitted}
            />
            
            {/* Existing Reviews */}
            {reviews.length > 0 ? (
              <div className="reviews-container">
                {reviews.map((review) => (
                  <Review key={review.id} review={review} />
                ))}
              </div>
            ) : (
              <p className="no-reviews">No reviews yet. Be the first to review this book!</p>
            )}
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
};

export default BookSynopsisPage;
