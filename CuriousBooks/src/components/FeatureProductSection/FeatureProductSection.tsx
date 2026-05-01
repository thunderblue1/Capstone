import { FC } from 'react';
import BookCard from '../BookCard/BookCard';
import type { Book } from '../../services/types';
import './FeatureProductSection.css';

export interface FeatureProductSectionProps {
  title?: string;
  books: Book[];
  onAddToCart?: (book: Book) => void;
}

const FeatureProductSection: FC<FeatureProductSectionProps> = ({ 
  title = "Featured Books",
  books,
  onAddToCart
}) => {
  return (
    <section className="feature-product-section" data-testid="FeatureProductSection">
      <div className="feature-product-section__container">
        <h2 className="feature-product-section__title">{title}</h2>
        <div className="feature-product-section__grid">
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

export default FeatureProductSection;
