import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import ResultsPage from './ResultsPage';

describe('<ResultsPage />', () => {
  test('it should mount', () => {
    render(<ResultsPage />);
    
    const resultsPage = screen.getByTestId('ResultsPage');

    expect(resultsPage).toBeInTheDocument();
  });
});