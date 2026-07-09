import { screen } from '@testing-library/react';
import { renderWithRouter as render } from '../../test/renderWithRouter';
import '@testing-library/jest-dom';
import LandingPage from './LandingPage';

describe('<LandingPage />', () => {
  test('it should mount', async () => {
    render(<LandingPage />);

    const landingPage = await screen.findByTestId('LandingPage');

    expect(landingPage).toBeInTheDocument();
  });
});
