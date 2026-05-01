import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import BookSearchBox from './BookSearchBox';

describe('<BookSearchBox />', () => {
  test('it should mount', () => {
    render(<BookSearchBox />);

    const bookSearchBox = screen.getByTestId('BookSearchBox');

    expect(bookSearchBox).toBeInTheDocument();
  });
});
