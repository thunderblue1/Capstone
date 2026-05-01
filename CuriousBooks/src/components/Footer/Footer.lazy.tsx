import { lazy, Suspense, type ComponentProps } from 'react';

const LazyFooter = lazy(() => import('./Footer'));

const Footer = (props: ComponentProps<typeof LazyFooter>) => (
  <Suspense fallback={null}>
    <LazyFooter {...props} />
  </Suspense>
);

export default Footer;
