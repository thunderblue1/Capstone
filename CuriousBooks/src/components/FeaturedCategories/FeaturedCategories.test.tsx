import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import FeaturedCategories from './FeaturedCategories';

describe('<FeaturedCategories />', () => {
  test('it should mount', () => {
    render(<FeaturedCategories />);
    
    const featuredCategories = screen.getByTestId('FeaturedCategories');

    expect(featuredCategories).toBeInTheDocument();
  });
});