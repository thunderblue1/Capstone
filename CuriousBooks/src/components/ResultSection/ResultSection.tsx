import { FC } from 'react';
import BookCard from '../BookCard/BookCard';
import type { Book } from '../../services/types';
import './ResultSection.css';

export interface ResultSectionProps {
  title: string;
  books: Book[];
  onAddToCart?: (book: Book) => void;
  variant?: 'default' | 'highlighted';
}

const ResultSection: FC<ResultSectionProps> = ({ 
  title, 
  books, 
  onAddToCart,
  variant = 'default'
}) => {
  return (
    <section className={`result-section result-section--${variant}`} data-testid="ResultSection">
      <div className="result-section__container">
        <h2 className="result-section__title">{title}</h2>
        <div className="result-section__grid">
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

export default ResultSection;
