import React, { lazy, Suspense } from 'react';

const LazyFeaturedCategories = lazy(() => import('./FeaturedCategories'));

const FeaturedCategories = (props: JSX.IntrinsicAttributes & { children?: React.ReactNode; }) => (
  <Suspense fallback={null}>
    <LazyFeaturedCategories {...props} />
  </Suspense>
);

export default FeaturedCategories;
