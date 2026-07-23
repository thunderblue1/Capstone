import { FC } from 'react';
import BookCard from '../BookCard/BookCard';
import type { Book } from '../../services/types';
import './BookSuggestions.css';

export interface BookSuggestionsProps {
  books: Book[];
  onAddToCart?: (book: Book) => void;
  isLoading?: boolean;
  title?: string;
  subtitle?: string;
}

const BookSuggestions: FC<BookSuggestionsProps> = ({ 
  books, 
  onAddToCart,
  isLoading = false,
  title = 'Recommended Books',
  subtitle = 'Personalized picks based on your search and reading history',
}) => {
  if (books.length === 0 && !isLoading) {
    return null;
  }

  if (isLoading) {
    return (
      <section className="book-suggestions book-suggestions--loading" data-testid="BookSuggestions">
        <div className="book-suggestions__container">
          <h2 className="book-suggestions__title">
            <span className="ai-badge">AI</span>
            {title}
          </h2>
          <div className="book-suggestions__loading">
            <div className="loading-pulse"></div>
            <p>Finding recommendations...</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="book-suggestions" data-testid="BookSuggestions">
      <div className="book-suggestions__container">
        <h2 className="book-suggestions__title">
          <span className="ai-badge">AI</span>
          {title}
        </h2>
        <p className="book-suggestions__subtitle">
          {subtitle}
        </p>
        <div className="book-suggestions__grid">
          {books.map((book) => (
            <BookCard 
              key={book.id} 
              book={book} 
              onAddToCart={onAddToCart}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default BookSuggestions;
