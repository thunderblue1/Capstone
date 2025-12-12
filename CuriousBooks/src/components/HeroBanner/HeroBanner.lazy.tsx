import React, { lazy, Suspense } from 'react';

const LazyHeroBanner = lazy(() => import('./HeroBanner'));

const HeroBanner = (props: JSX.IntrinsicAttributes & { children?: React.ReactNode; }) => (
  <Suspense fallback={null}>
    <LazyHeroBanner {...props} />
  </Suspense>
);

export default HeroBanner;
