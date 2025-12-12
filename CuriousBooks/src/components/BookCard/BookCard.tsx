import React, { FC } from 'react';
import { Link } from 'react-router-dom';
import StarRating from '../StarRating/StarRating';
import type { Book } from '../../services/types';
import './BookCard.css';

interface BookCardProps {
  book: Book;
  onAddToCart?: (book: Book) => void;
}

const BookCard: FC<BookCardProps> = ({ book, onAddToCart }) => {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const truncateDescription = (text: string, maxLength: number = 80) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + '...';
  };

  return (
    <div className="book-card" data-testid="BookCard">
      <div className="book-card__image-container">
        <div className="book-card__image-placeholder">
          {/* Placeholder SVG for book cover */}
          <svg viewBox="0 0 120 160" className="book-cover-placeholder">
            <defs>
              <linearGradient id={`grad-${book.id}`} x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#00bcd4" />
                <stop offset="100%" stopColor="#4caf50" />
              </linearGradient>
            </defs>
            <rect width="120" height="160" fill={`url(#grad-${book.id})`} />
            {/* Cloud */}
            <ellipse cx="70" cy="55" rx="25" ry="18" fill="white" opacity="0.9" />
            <ellipse cx="55" cy="58" rx="18" ry="14" fill="white" opacity="0.9" />
            <ellipse cx="85" cy="60" rx="15" ry="12" fill="white" opacity="0.9" />
            {/* Hills */}
            <polygon points="0,160 40,100 80,160" fill="#7cb342" />
            <polygon points="50,160 100,90 120,160" fill="#558b2f" />
          </svg>
        </div>
      </div>

      <div className="book-card__content">
        <h3 className="book-card__title">{book.title}</h3>
        
        <div className="book-card__meta">
          <p className="book-card__author">
            <span className="label">Author:</span> {book.author}
          </p>
          <p className="book-card__genre">
            <span className="label">Genre:</span> {book.genre}
          </p>
        </div>

        <div className="book-card__rating">
          <span className="label">Average Rating:</span>
          <StarRating rating={book.averageRating} size="sm" />
        </div>

        <p className="book-card__description">
          <span className="label">Description:</span> {truncateDescription(book.description)}
        </p>

        <p className="book-card__price">
          <span className="label">Price:</span> {formatPrice(book.price)}
        </p>
      </div>

      <div className="book-card__footer">
        <Link to={`/book/${book.id}`} className="book-card__btn book-card__btn--details">
          Details
        </Link>
        <button 
          className="book-card__btn book-card__btn--cart"
          onClick={() => onAddToCart?.(book)}
        >
          Add to Cart
        </button>
      </div>
    </div>
  );
};

export default BookCard;
