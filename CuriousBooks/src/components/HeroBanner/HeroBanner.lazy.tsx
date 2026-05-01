import { lazy, Suspense, type ComponentProps } from 'react';

const LazyHeroBanner = lazy(() => import('./HeroBanner'));

const HeroBanner = (props: ComponentProps<typeof LazyHeroBanner>) => (
  <Suspense fallback={null}>
    <LazyHeroBanner {...props} />
  </Suspense>
);

export default HeroBanner;
