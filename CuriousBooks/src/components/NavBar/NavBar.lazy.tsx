import { lazy, Suspense, type ComponentProps } from 'react';

const LazyNavBar = lazy(() => import('./NavBar'));

const NavBar = (props: ComponentProps<typeof LazyNavBar>) => (
  <Suspense fallback={null}>
    <LazyNavBar {...props} />
  </Suspense>
);

export default NavBar;
