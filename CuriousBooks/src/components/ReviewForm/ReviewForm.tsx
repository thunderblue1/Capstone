import React, { FC, useState } from 'react';
import { Link } from 'react-router-dom';
import StarRating from '../StarRating/StarRating';
import { reviewsApi } from '../../services/api';
import { logger } from '../../services/logger';
import type { Review, User } from '../../services/types';
import './ReviewForm.css';

interface ReviewFormProps {
  bookId: string;
  bookTitle: string;
  user: User | null;
  isLoggedIn: boolean;
  onReviewSubmitted?: (review: Review) => void;
}

const ReviewForm: FC<ReviewFormProps> = ({ 
  bookId, 
  bookTitle, 
  user, 
  isLoggedIn, 
  onReviewSubmitted 
}) => {
  const [rating, setRating] = useState<number>(0);
  const [hoverRating, setHoverRating] = useState<number>(0);
  const [reviewText, setReviewText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleStarClick = (starValue: number) => {
    setRating(starValue);
    setError(null);
  };

  const handleStarHover = (starValue: number) => {
    setHoverRating(starValue);
  };

  const handleStarLeave = () => {
    setHoverRating(0);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (rating === 0) {
      setError('Please select a rating');
      return;
    }

    if (reviewText.trim().length < 10) {
      setError('Please write at least 10 characters for your review');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await reviewsApi.create(bookId, rating, reviewText.trim());
      
      logger.application.info('Review submitted successfully', {
        bookId,
        rating,
        component: 'ReviewForm',
      });

      setSuccess(true);
      setRating(0);
      setReviewText('');

      if (onReviewSubmitted && response.review) {
        onReviewSubmitted(response.review);
      }

      // Reset success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      logger.error.log(err instanceof Error ? err : 'Failed to submit review', {
        component: 'ReviewForm',
        errorCode: 'REVIEW_SUBMIT_ERROR',
        bookId,
      });
      setError('Failed to submit review. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Show login prompt if not logged in
  if (!isLoggedIn) {
    return (
      <div className="review-form review-form--login-prompt" data-testid="ReviewForm">
        <div className="review-form__login-message">
          <div className="review-form__login-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </div>
          <h3>Share Your Thoughts!</h3>
          <p>Log in to leave a review for "{bookTitle}"</p>
          <Link to="/login" className="review-form__login-btn">
            Log In to Review
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="review-form" data-testid="ReviewForm">
      <div className="review-form__header">
        <div className="review-form__user-info">
          <div className="review-form__avatar">
            {user?.firstName?.charAt(0).toUpperCase() || user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="review-form__user-details">
            <span className="review-form__username">
              {user?.firstName ? `${user.firstName} ${user.lastName || ''}`.trim() : user?.username || 'User'}
            </span>
            <span className="review-form__label">Write a Review</span>
          </div>
        </div>
      </div>

      {success && (
        <div className="review-form__success">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          Thank you! Your review has been submitted.
        </div>
      )}

      <form onSubmit={handleSubmit} className="review-form__form">
        <div className="review-form__rating-section">
          <label className="review-form__rating-label">Your Rating</label>
          <div className="review-form__stars" onMouseLeave={handleStarLeave}>
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                className={`review-form__star ${
                  star <= (hoverRating || rating) ? 'review-form__star--filled' : ''
                }`}
                onClick={() => handleStarClick(star)}
                onMouseEnter={() => handleStarHover(star)}
                aria-label={`Rate ${star} star${star > 1 ? 's' : ''}`}
              >
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                </svg>
              </button>
            ))}
            <span className="review-form__rating-text">
              {rating > 0 ? `${rating} out of 5 stars` : 'Click to rate'}
            </span>
          </div>
        </div>

        <div className="review-form__text-section">
          <label htmlFor="review-text" className="review-form__text-label">
            Your Review
          </label>
          <textarea
            id="review-text"
            className="review-form__textarea"
            placeholder="Share your experience with this book. What did you like or dislike? Would you recommend it to others?"
            value={reviewText}
            onChange={(e) => {
              setReviewText(e.target.value);
              setError(null);
            }}
            rows={5}
            maxLength={2000}
          />
          <div className="review-form__char-count">
            {reviewText.length}/2000 characters
          </div>
        </div>

        {error && (
          <div className="review-form__error">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            {error}
          </div>
        )}

        <button 
          type="submit" 
          className="review-form__submit-btn"
          disabled={isSubmitting || rating === 0}
        >
          {isSubmitting ? (
            <>
              <span className="review-form__spinner"></span>
              Submitting...
            </>
          ) : (
            <>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 2L11 13" />
                <path d="M22 2L15 22L11 13L2 9L22 2Z" />
              </svg>
              Submit Review
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default ReviewForm;

