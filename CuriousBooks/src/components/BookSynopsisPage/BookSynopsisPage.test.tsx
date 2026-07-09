import { screen } from '@testing-library/react';
import { renderWithRouter as render } from '../../test/renderWithRouter';
import '@testing-library/jest-dom';
import BookSynopsisPage from './BookSynopsisPage';

describe('<BookSynopsisPage />', () => {
  test('it should mount', async () => {
    render(<BookSynopsisPage />);

    const bookSynopsisPage = await screen.findByTestId('BookSynopsisPage');

    expect(bookSynopsisPage).toBeInTheDocument();
  });
});
