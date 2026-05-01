import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import LandingPage from './LandingPage';

describe('<LandingPage />', () => {
  test('it should mount', () => {
    render(<LandingPage />);

    const landingPage = screen.getByTestId('LandingPage');

    expect(landingPage).toBeInTheDocument();
  });
});
