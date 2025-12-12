import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import ResultSection from './ResultSection';

describe('<ResultSection />', () => {
  test('it should mount', () => {
    render(<ResultSection />);
    
    const resultSection = screen.getByTestId('ResultSection');

    expect(resultSection).toBeInTheDocument();
  });
});