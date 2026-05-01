import { lazy, Suspense, type ComponentProps } from 'react';

const LazyBookSynopsisPage = lazy(() => import('./BookSynopsisPage'));

const BookSynopsisPage = (props: ComponentProps<typeof LazyBookSynopsisPage>) => (
  <Suspense fallback={null}>
    <LazyBookSynopsisPage {...props} />
  </Suspense>
);

export default BookSynopsisPage;
