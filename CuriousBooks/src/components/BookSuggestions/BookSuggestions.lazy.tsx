import React, { lazy, Suspense } from 'react';

const LazyBookSuggestions = lazy(() => import('./BookSuggestions'));

const BookSuggestions = (props: JSX.IntrinsicAttributes & { children?: React.ReactNode; }) => (
  <Suspense fallback={null}>
    <LazyBookSuggestions {...props} />
  </Suspense>
);

export default BookSuggestions;
