import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { createMockBook } from '../../test/fixtures';
import FeatureProductSection from './FeatureProductSection';

describe('<FeatureProductSection />', () => {
  test('it should mount', () => {
    render(<FeatureProductSection books={[createMockBook()]} />);

    const featureProductSection = screen.getByTestId('FeatureProductSection');

    expect(featureProductSection).toBeInTheDocument();
  });
});
