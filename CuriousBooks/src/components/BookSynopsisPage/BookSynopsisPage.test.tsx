import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import BookSynopsisPage from './BookSynopsisPage';

describe('<BookSynopsisPage />', () => {
  test('it should mount', () => {
    render(<BookSynopsisPage />);

    const bookSynopsisPage = screen.getByTestId('BookSynopsisPage');

    expect(bookSynopsisPage).toBeInTheDocument();
  });
});
