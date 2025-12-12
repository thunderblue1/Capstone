import React, { lazy, Suspense } from 'react';

const LazyResultsPage = lazy(() => import('./ResultsPage'));

const ResultsPage = (props: JSX.IntrinsicAttributes & { children?: React.ReactNode; }) => (
  <Suspense fallback={null}>
    <LazyResultsPage {...props} />
  </Suspense>
);

export default ResultsPage;
