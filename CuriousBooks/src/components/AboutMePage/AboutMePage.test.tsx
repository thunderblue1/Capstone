import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import AboutMePage from './AboutMePage';

describe('<AboutMePage />', () => {
  test('it should mount', () => {
    render(<AboutMePage />);

    const aboutMePage = screen.getByTestId('AboutMePage');

    expect(aboutMePage).toBeInTheDocument();
  });
});
