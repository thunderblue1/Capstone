/**
 * ResultsPage Component
 * =====================
 * 
 * Purpose:
 *   Displays search results, category browsing, or all books listing.
 *   Includes recommendation suggestions and pagination support.
 * 
 * Features:
 *   - Search results display with query highlighting
 *   - Category-based book filtering
 *   - Book recommendations based on search context
 *   - Additional results section for expanded browsing
 *   - Loading and error state handling
 * 
 * URL Query Parameters:
 *   - q: Search query string
 *   - category: Category name filter
 *   (If neither provided, shows all books)
 * 
 * Data Flow:
 *   1. Reads search params via useSearchParams()
 *   2. Fetches results via booksApi.search() or booksApi.getByCategory()
 *   3. Fetches recommendations via recommendationsApi
 *   4. Displays in ResultSection and BookSuggestions components
 * 
 * Props:
 *   - cartItems: Current cart for navbar badge
 *   - onAddToCart: Callback to add book to cart
 *   - isLoggedIn: Authentication state
 *   - user: Current user object
 *   - userAvatar: User avatar URL
 *   - onLogout: Logout handler
 * 
 * Usage:
 *   <Route path="/search" element={<ResultsPage {...props} />} />
 */
import { FC, useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import NavBar from '../NavBar/NavBar';
import ResultSection from '../ResultSection/ResultSection';
import BookSuggestions from '../BookSuggestions/BookSuggestions';
import Footer from '../Footer/Footer';
import { booksApi, recommendationsApi } from '../../services/api';
import { logger } from '../../services/logger';
import type { Book, User } from '../../services/types';
import './ResultsPage.css';

interface ResultsPageProps {
  cartItems?: Book[];
  onAddToCart?: (book: Book) => void;
  isLoggedIn?: boolean;
  user?: User | null;
  userAvatar?: string | null;
  cartItemCount?: number;
  onLogout?: () => void;
}

const ResultsPage: FC<ResultsPageProps> = ({ 
  onAddToCart,
  isLoggedIn = false,
  user = null,
  userAvatar = null,
  cartItemCount = 0,
  onLogout,
}) => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const category = searchParams.get('category') || '';
  
  const [results, setResults] = useState<Book[]>([]);
  const [recommendations, setRecommendations] = useState<Book[]>([]);
  const [moreResults, setMoreResults] = useState<Book[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadResults = async () => {
      setIsLoading(true);
      setIsLoadingRecommendations(true);
      setError(null);
      
      try {
        // Load search results or category books
        if (query) {
          const searchResponse = await booksApi.search(query);
          setResults(searchResponse.results);
          
          // Get search-based recommendations
          const excludeIds = searchResponse.results.map(b => b.id);
          const recsResponse = await recommendationsApi.getSearchBased(query, 4, excludeIds);
          setRecommendations(recsResponse.recommendations);
          setIsLoadingRecommendations(false);
          
          // Load more results (page 2)
          if (searchResponse.pages > 1) {
            const moreResponse = await booksApi.search(query, 2);
            setMoreResults(moreResponse.results);
          }
        } else if (category) {
          const categoryResponse = await booksApi.getByCategory(category);
          setResults(categoryResponse.books);
          
          // Get recommendations based on category
          const excludeIds = categoryResponse.books.map(b => b.id);
          const recsResponse = await recommendationsApi.get(4, excludeIds);
          setRecommendations(recsResponse.recommendations);
          setIsLoadingRecommendations(false);
        } else {
          // No query or category - show all books
          const allBooksResponse = await booksApi.getAll({ perPage: 20 });
          setResults(allBooksResponse.books);
          
          const recsResponse = await recommendationsApi.get(4);
          setRecommendations(recsResponse.recommendations);
          setIsLoadingRecommendations(false);
        }
      } catch (err) {
        logger.error.log(err instanceof Error ? err : 'Failed to load results', {
          component: 'ResultsPage',
          errorCode: 'RESULTS_LOAD_ERROR',
          query,
          category,
        });
        setError('Failed to load results. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadResults();
  }, [query, category]);

  const searchTitle = query 
    ? `Search results for "${query}"`
    : category 
      ? `Books in ${category}`
      : 'All Books';

  return (
    <div className="results-page" data-testid="ResultsPage">
      <NavBar 
        cartItemCount={cartItemCount}
        isLoggedIn={isLoggedIn}
        user={user}
        userAvatar={userAvatar}
        onLogout={onLogout}
      />
      <main className="results-page__main">
        <div className="results-page__header">
          <div className="results-page__container">
            <h1 className="results-page__title">Book Search Results</h1>
            {(query || category) && (
              <p className="results-page__subtitle">{searchTitle}</p>
            )}
          </div>
        </div>

        {isLoading ? (
          <div className="results-page__loading">
            <div className="loading-spinner"></div>
            <p>Searching for books...</p>
          </div>
        ) : error ? (
          <div className="results-page__error">
            <p>{error}</p>
          </div>
        ) : (
          <>
            <ResultSection 
              title="Book Search Results" 
              books={results}
              onAddToCart={onAddToCart}
            />

            <BookSuggestions 
              books={recommendations}
              onAddToCart={onAddToCart}
              isLoading={isLoadingRecommendations}
            />

            {moreResults.length > 0 && (
              <ResultSection 
                title="More Book Search Results" 
                books={moreResults}
                onAddToCart={onAddToCart}
                variant="highlighted"
              />
            )}
          </>
        )}
      </main>
      <Footer />
    </div>
  );
};

export default ResultsPage;
