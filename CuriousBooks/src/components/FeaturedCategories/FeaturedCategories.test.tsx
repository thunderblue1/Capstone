import { screen } from '@testing-library/react';
import { renderWithRouter as render } from '../../test/renderWithRouter';
import '@testing-library/jest-dom';
import FeaturedCategories from './FeaturedCategories';

describe('<FeaturedCategories />', () => {
  test('it should mount', async () => {
    render(<FeaturedCategories />);

    const featuredCategories = await screen.findByTestId('FeaturedCategories');

    expect(featuredCategories).toBeInTheDocument();
  });
});
