import { screen } from '@testing-library/react';
import { renderWithRouter as render } from '../../test/renderWithRouter';
import '@testing-library/jest-dom';
import Footer from './Footer';

describe('<Footer />', () => {
  test('it should mount', () => {
    render(<Footer />);

    const footer = screen.getByTestId('Footer');

    expect(footer).toBeInTheDocument();
  });
});
