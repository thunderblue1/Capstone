import { screen } from '@testing-library/react';
import { renderWithRouter as render } from '../../test/renderWithRouter';
import '@testing-library/jest-dom';
import NavBar from './NavBar';

describe('<NavBar />', () => {
  test('it should mount', () => {
    render(<NavBar />);

    const navBar = screen.getByTestId('NavBar');

    expect(navBar).toBeInTheDocument();
  });
});
