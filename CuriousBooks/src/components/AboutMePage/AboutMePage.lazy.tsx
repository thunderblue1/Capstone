import React, { lazy, Suspense } from 'react';

const LazyAboutMePage = lazy(() => import('./AboutMePage'));

const AboutMePage = (props: JSX.IntrinsicAttributes & { children?: React.ReactNode; }) => (
  <Suspense fallback={null}>
    <LazyAboutMePage {...props} />
  </Suspense>
);

export default AboutMePage;
