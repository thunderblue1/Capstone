import { screen } from '@testing-library/react';
import { renderWithRouter as render } from '../../test/renderWithRouter';
import '@testing-library/jest-dom';
import ResultsPage from './ResultsPage';

describe('<ResultsPage />', () => {
  test('it should mount', async () => {
    render(<ResultsPage />);

    const resultsPage = await screen.findByTestId('ResultsPage');

    expect(resultsPage).toBeInTheDocument();
  });
});
