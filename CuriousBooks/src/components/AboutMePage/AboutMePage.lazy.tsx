import { lazy, Suspense, type ComponentProps } from 'react';

const LazyAboutMePage = lazy(() => import('./AboutMePage'));

const AboutMePage = (props: ComponentProps<typeof LazyAboutMePage>) => (
  <Suspense fallback={null}>
    <LazyAboutMePage {...props} />
  </Suspense>
);

export default AboutMePage;
