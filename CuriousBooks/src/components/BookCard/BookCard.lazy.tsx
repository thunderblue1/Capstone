import React, { lazy, Suspense } from 'react';

const LazyBookCard = lazy(() => import('./BookCard'));

const BookCard = (props: JSX.IntrinsicAttributes & { children?: React.ReactNode; }) => (
  <Suspense fallback={null}>
    <LazyBookCard {...props} />
  </Suspense>
);

export default BookCard;
