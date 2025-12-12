import React, { lazy, Suspense } from 'react';

const LazyBookSearchBox = lazy(() => import('./BookSearchBox'));

const BookSearchBox = (props: JSX.IntrinsicAttributes & { children?: React.ReactNode; }) => (
  <Suspense fallback={null}>
    <LazyBookSearchBox {...props} />
  </Suspense>
);

export default BookSearchBox;
