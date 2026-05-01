import { lazy, Suspense, type ComponentProps } from 'react';

const LazyResultsPage = lazy(() => import('./ResultsPage'));

const ResultsPage = (props: ComponentProps<typeof LazyResultsPage>) => (
  <Suspense fallback={null}>
    <LazyResultsPage {...props} />
  </Suspense>
);

export default ResultsPage;
