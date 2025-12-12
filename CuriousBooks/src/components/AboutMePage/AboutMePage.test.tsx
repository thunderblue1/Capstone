import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import AboutMePage from './AboutMePage';

describe('<AboutMePage />', () => {
  test('it should mount', () => {
    render(<AboutMePage />);
    
    const aboutMePage = screen.getByTestId('AboutMePage');

    expect(aboutMePage).toBeInTheDocument();
  });
});