import { lazy, Suspense, type ComponentProps } from 'react';

const LazyLandingPage = lazy(() => import('./LandingPage'));

const LandingPage = (props: ComponentProps<typeof LazyLandingPage>) => (
  <Suspense fallback={null}>
    <LazyLandingPage {...props} />
  </Suspense>
);

export default LandingPage;
