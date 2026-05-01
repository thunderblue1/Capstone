import { lazy, Suspense, type ComponentProps } from 'react';

const LazyFeaturedCategories = lazy(() => import('./FeaturedCategories'));

const FeaturedCategories = (props: ComponentProps<typeof LazyFeaturedCategories>) => (
  <Suspense fallback={null}>
    <LazyFeaturedCategories {...props} />
  </Suspense>
);

export default FeaturedCategories;
