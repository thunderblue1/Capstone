import React, { FC } from 'react';
import './StarRating.css';

interface StarRatingProps {
  rating: number;
  maxRating?: number;
  size?: 'sm' | 'md' | 'lg';
  showNumber?: boolean;
}

const StarRating: FC<StarRatingProps> = ({ 
  rating, 
  maxRating = 5, 
  size = 'md',
  showNumber = false 
}) => {
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  const emptyStars = maxRating - fullStars - (hasHalfStar ? 1 : 0);

  return (
    <div className={`star-rating star-rating--${size}`} aria-label={`Rating: ${rating} out of ${maxRating} stars`}>
      <div className="stars-container">
        {/* Full stars */}
        {[...Array(fullStars)].map((_, i) => (
          <span key={`full-${i}`} className="star star--filled">★</span>
        ))}
        
        {/* Half star */}
        {hasHalfStar && (
          <span className="star star--half">
            <span className="star-half-filled">★</span>
            <span className="star-half-empty">★</span>
          </span>
        )}
        
        {/* Empty stars */}
        {[...Array(emptyStars)].map((_, i) => (
          <span key={`empty-${i}`} className="star star--empty">★</span>
        ))}
      </div>
      
      {showNumber && (
        <span className="rating-number">{rating.toFixed(1)}</span>
      )}
    </div>
  );
};

export default StarRating;







