import { lazy, Suspense } from 'react';
import type { FeatureProductSectionProps } from './FeatureProductSection';

const LazyFeatureProductSection = lazy(() => import('./FeatureProductSection'));

const FeatureProductSection = (props: FeatureProductSectionProps) => (
  <Suspense fallback={null}>
    <LazyFeatureProductSection {...props} />
  </Suspense>
);

export default FeatureProductSection;
