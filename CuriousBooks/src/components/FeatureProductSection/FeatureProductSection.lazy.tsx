import React, { lazy, Suspense } from 'react';

const LazyFeatureProductSection = lazy(() => import('./FeatureProductSection'));

const FeatureProductSection = (props: JSX.IntrinsicAttributes & { children?: React.ReactNode; }) => (
  <Suspense fallback={null}>
    <LazyFeatureProductSection {...props} />
  </Suspense>
);

export default FeatureProductSection;
