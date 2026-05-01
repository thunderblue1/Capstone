import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { createMockBook } from '../../test/fixtures';
import BookCard from './BookCard';

describe('<BookCard />', () => {
  test('it should mount', () => {
    render(<BookCard book={createMockBook()} />);

    const bookCard = screen.getByTestId('BookCard');

    expect(bookCard).toBeInTheDocument();
  });
});
