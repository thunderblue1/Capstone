import { lazy, Suspense } from 'react';
import type { BookCardProps } from './BookCard';

const LazyBookCard = lazy(() => import('./BookCard'));

const BookCard = (props: BookCardProps) => (
  <Suspense fallback={null}>
    <LazyBookCard {...props} />
  </Suspense>
);

export default BookCard;
