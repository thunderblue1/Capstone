import React, { lazy, Suspense } from 'react';

const LazyBookSynopsisPage = lazy(() => import('./BookSynopsisPage'));

const BookSynopsisPage = (props: JSX.IntrinsicAttributes & { children?: React.ReactNode; }) => (
  <Suspense fallback={null}>
    <LazyBookSynopsisPage {...props} />
  </Suspense>
);

export default BookSynopsisPage;
