import { screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import BookSynopsisPage from './BookSynopsisPage';

const routerFuture = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
} as const;

function renderSynopsisPage() {
  return render(
    <MemoryRouter initialEntries={['/book/book-1']} future={routerFuture}>
      <Routes>
        <Route path="/book/:id" element={<BookSynopsisPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('<BookSynopsisPage />', () => {
  test('it should mount', async () => {
    renderSynopsisPage();

    const bookSynopsisPage = await screen.findByTestId('BookSynopsisPage');

    expect(bookSynopsisPage).toBeInTheDocument();
  });

  test('it links to category and genre recommendation browse pages', async () => {
    renderSynopsisPage();

    const categoryLink = await screen.findByRole('link', {
      name: /Recommendations in Fiction/i,
    });
    expect(categoryLink).toHaveAttribute('href', '/search?category=Fiction');

    const genreLink = screen.getByRole('link', { name: /Browse Fiction books/i });
    expect(genreLink).toHaveAttribute('href', '/search?q=Fiction');
  });

  test('Continue Shopping returns to previous search results when available', async () => {
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/book/book-1',
            state: { from: '/search?q=fiction' },
          },
        ]}
        future={routerFuture}
      >
        <Routes>
          <Route path="/book/:id" element={<BookSynopsisPage />} />
        </Routes>
      </MemoryRouter>,
    );

    const continueShopping = await screen.findByRole('link', {
      name: /Continue Shopping/i,
    });
    expect(continueShopping).toHaveAttribute('href', '/search?q=fiction');
  });

  test('Continue Shopping falls back to /search without prior search state', async () => {
    renderSynopsisPage();

    const continueShopping = await screen.findByRole('link', {
      name: /Continue Shopping/i,
    });
    expect(continueShopping).toHaveAttribute('href', '/search');
  });
});
