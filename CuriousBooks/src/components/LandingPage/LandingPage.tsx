import React, { FC, useState, useEffect } from 'react';
import NavBar from '../NavBar/NavBar';
import HeroBanner from '../HeroBanner/HeroBanner';
import FeaturedCategories from '../FeaturedCategories/FeaturedCategories';
import FeatureProductSection from '../FeatureProductSection/FeatureProductSection';
import Footer from '../Footer/Footer';
import { booksApi } from '../../services/api';
import { logger } from '../../services/logger';
import type { Book, User } from '../../services/types';
import './LandingPage.css';

interface LandingPageProps {
  cartItems?: Book[];
  onAddToCart?: (book: Book) => void;
  isLoggedIn?: boolean;
  user?: User | null;
  userAvatar?: string | null;
  onLogout?: () => void;
}

const LandingPage: FC<LandingPageProps> = ({ 
  cartItems = [], 
  onAddToCart,
  isLoggedIn = false,
  user = null,
  userAvatar = null,
  onLogout,
}) => {
  const [books, setBooks] = useState<Book[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadBooks = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const featuredBooks = await booksApi.getFeatured(4);
        setBooks(featuredBooks);
        logger.application.info('Featured books loaded', { count: featuredBooks.length, component: 'LandingPage' });
      } catch (err) {
        logger.error.log(err instanceof Error ? err : 'Failed to load featured books', {
          component: 'LandingPage',
          errorCode: 'FEATURED_BOOKS_LOAD_ERROR',
        });
        setError('Failed to load featured books. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadBooks();
  }, []);

  return (
    <div className="landing-page" data-testid="LandingPage">
      <NavBar 
        cartItemCount={cartItems.length} 
        isLoggedIn={isLoggedIn}
        user={user}
        userAvatar={userAvatar}
        onLogout={onLogout}
      />
      <main className="landing-page__main">
        <HeroBanner />
        <FeaturedCategories />
        {isLoading ? (
          <div className="landing-page__loading">
            <div className="loading-spinner"></div>
            <p>Loading featured books...</p>
          </div>
        ) : error ? (
          <div className="landing-page__error">
            <p>{error}</p>
          </div>
        ) : (
          <FeatureProductSection 
            title="Featured Books" 
            books={books}
            onAddToCart={onAddToCart}
          />
        )}
      </main>
      <Footer />
    </div>
  );
};

export default LandingPage;
