import { lazy, Suspense } from 'react';
import type { ResultSectionProps } from './ResultSection';

const LazyResultSection = lazy(() => import('./ResultSection'));

const ResultSection = (props: ResultSectionProps) => (
  <Suspense fallback={null}>
    <LazyResultSection {...props} />
  </Suspense>
);

export default ResultSection;
