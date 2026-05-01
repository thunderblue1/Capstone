import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { createMockBook } from '../../test/fixtures';
import BookSuggestions from './BookSuggestions';

describe('<BookSuggestions />', () => {
  test('it should mount', () => {
    render(<BookSuggestions books={[createMockBook()]} />);

    const bookSuggestions = screen.getByTestId('BookSuggestions');

    expect(bookSuggestions).toBeInTheDocument();
  });
});
