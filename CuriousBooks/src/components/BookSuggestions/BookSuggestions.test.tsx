import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import BookSuggestions from './BookSuggestions';

describe('<BookSuggestions />', () => {
  test('it should mount', () => {
    render(<BookSuggestions />);
    
    const bookSuggestions = screen.getByTestId('BookSuggestions');

    expect(bookSuggestions).toBeInTheDocument();
  });
});