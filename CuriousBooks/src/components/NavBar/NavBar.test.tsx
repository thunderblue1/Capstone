import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import NavBar from './NavBar';

describe('<NavBar />', () => {
  test('it should mount', () => {
    render(<NavBar />);

    const navBar = screen.getByTestId('NavBar');

    expect(navBar).toBeInTheDocument();
  });
});
