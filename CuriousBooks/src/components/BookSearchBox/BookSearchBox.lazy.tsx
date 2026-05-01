import { lazy, Suspense, type ComponentProps } from 'react';

const LazyBookSearchBox = lazy(() => import('./BookSearchBox'));

const BookSearchBox = (props: ComponentProps<typeof LazyBookSearchBox>) => (
  <Suspense fallback={null}>
    <LazyBookSearchBox {...props} />
  </Suspense>
);

export default BookSearchBox;
