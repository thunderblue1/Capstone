import React, { FC } from 'react';
import StarRating from '../StarRating/StarRating';
import type { Review as ReviewType } from '../../services/types';
import './Review.css';

interface ReviewProps {
  review: ReviewType;
}

const Review: FC<ReviewProps> = ({ review }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="review" data-testid="Review">
      <div className="review__header">
        <div className="review__avatar">
          {review.reviewerName.charAt(0).toUpperCase()}
        </div>
        <div className="review__meta">
          <span className="review__reviewer">
            <span className="label">Reviewer:</span> {review.reviewerName}
          </span>
          <div className="review__rating">
            <span className="label">Rating:</span>
            <StarRating rating={review.rating} size="sm" />
          </div>
        </div>
        <span className="review__date">{formatDate(review.date)}</span>
      </div>
      <p className="review__text">{review.text}</p>
    </div>
  );
};

export default Review;













