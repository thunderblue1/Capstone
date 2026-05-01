import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import HeroBanner from './HeroBanner';

describe('<HeroBanner />', () => {
  test('it should mount', () => {
    render(<HeroBanner />);

    const heroBanner = screen.getByTestId('HeroBanner');

    expect(heroBanner).toBeInTheDocument();
  });
});
