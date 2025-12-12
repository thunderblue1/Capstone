import React, { lazy, Suspense } from 'react';

const LazyResultSection = lazy(() => import('./ResultSection'));

const ResultSection = (props: JSX.IntrinsicAttributes & { children?: React.ReactNode; }) => (
  <Suspense fallback={null}>
    <LazyResultSection {...props} />
  </Suspense>
);

export default ResultSection;
