import { screen, fireEvent, render } from '@testing-library/react';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { vi } from 'vitest';
import '@testing-library/jest-dom';
import { createMockBook } from '../../test/fixtures';
import BookCard from './BookCard';

vi.mock('../../services/bookCovers', () => ({
  resolveBookCoverUrl: (imageUrl: string | null | undefined) => {
    if (!imageUrl || imageUrl === 'default.jpg') return null;
    const filename = imageUrl.split('/').pop();
    return filename ? `/mock-assets/${filename}` : null;
  },
  coverFilename: (imageUrl: string | null | undefined) =>
    imageUrl?.split('/').pop() || 'default.jpg',
  DEFAULT_COVER_FILENAME: 'default.jpg',
}));

const routerFuture = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
} as const;

function renderBookCard(initialPath = '/', book = createMockBook()) {
  return render(
    <MemoryRouter initialEntries={[initialPath]} future={routerFuture}>
      <Routes>
        <Route path="*" element={<BookCard book={book} />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('<BookCard />', () => {
  test('it should mount', () => {
    renderBookCard();

    const bookCard = screen.getByTestId('BookCard');

    expect(bookCard).toBeInTheDocument();
  });

  test('shows cover image when imageUrl filename resolves', () => {
    renderBookCard(
      '/',
      createMockBook({
        title: 'Covered Book',
        imageUrl: 'covered-book.jpg',
      }),
    );

    const cover = screen.getByRole('img', { name: 'Covered Book' });
    expect(cover).toHaveAttribute('src', '/mock-assets/covered-book.jpg');
  });

  test('shows SVG placeholder when cover image is missing', () => {
    const { container } = renderBookCard(
      '/',
      createMockBook({ imageUrl: '' }),
    );

    expect(screen.queryByRole('img')).not.toBeInTheDocument();
    expect(container.querySelector('.book-cover-placeholder')).toBeInTheDocument();
  });

  test('shows SVG placeholder for default.jpg', () => {
    const { container } = renderBookCard(
      '/',
      createMockBook({ imageUrl: 'default.jpg' }),
    );

    expect(screen.queryByRole('img')).not.toBeInTheDocument();
    expect(container.querySelector('.book-cover-placeholder')).toBeInTheDocument();
  });

  test('Details link preserves search results path in location state', () => {
    let capturedState: unknown;

    function CaptureRoute() {
      const location = useLocation();
      capturedState = location.state;
      return <div>Book page</div>;
    }

    render(
      <MemoryRouter initialEntries={['/search?q=mystery']} future={routerFuture}>
        <Routes>
          <Route path="/search" element={<BookCard book={createMockBook()} />} />
          <Route path="/book/:id" element={<CaptureRoute />} />
        </Routes>
      </MemoryRouter>,
    );

    fireEvent.click(screen.getByRole('link', { name: 'Details' }));

    expect(capturedState).toEqual({ from: '/search?q=mystery' });
  });
});
