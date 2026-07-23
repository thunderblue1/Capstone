import { screen } from '@testing-library/react';
import { vi } from 'vitest';
import { renderWithRouter as render } from '../../test/renderWithRouter';
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

describe('<BookCard />', () => {
  test('it should mount', () => {
    render(<BookCard book={createMockBook()} />);

    const bookCard = screen.getByTestId('BookCard');

    expect(bookCard).toBeInTheDocument();
  });

  test('shows cover image when imageUrl filename resolves', () => {
    render(
      <BookCard
        book={createMockBook({
          title: 'Covered Book',
          imageUrl: 'covered-book.jpg',
        })}
      />
    );

    const cover = screen.getByRole('img', { name: 'Covered Book' });
    expect(cover).toHaveAttribute('src', '/mock-assets/covered-book.jpg');
  });

  test('shows SVG placeholder when cover image is missing', () => {
    const { container } = render(
      <BookCard book={createMockBook({ imageUrl: '' })} />
    );

    expect(screen.queryByRole('img')).not.toBeInTheDocument();
    expect(container.querySelector('.book-cover-placeholder')).toBeInTheDocument();
  });

  test('shows SVG placeholder for default.jpg', () => {
    const { container } = render(
      <BookCard book={createMockBook({ imageUrl: 'default.jpg' })} />
    );

    expect(screen.queryByRole('img')).not.toBeInTheDocument();
    expect(container.querySelector('.book-cover-placeholder')).toBeInTheDocument();
  });
});
