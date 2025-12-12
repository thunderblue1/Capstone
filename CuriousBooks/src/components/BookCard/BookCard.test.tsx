import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import BookCard from './BookCard';

describe('<BookCard />', () => {
  test('it should mount', () => {
    render(<BookCard />);
    
    const bookCard = screen.getByTestId('BookCard');

    expect(bookCard).toBeInTheDocument();
  });
});