import { lazy, Suspense } from 'react';
import type { BookSuggestionsProps } from './BookSuggestions';

const LazyBookSuggestions = lazy(() => import('./BookSuggestions'));

const BookSuggestions = (props: BookSuggestionsProps) => (
  <Suspense fallback={null}>
    <LazyBookSuggestions {...props} />
  </Suspense>
);

export default BookSuggestions;
