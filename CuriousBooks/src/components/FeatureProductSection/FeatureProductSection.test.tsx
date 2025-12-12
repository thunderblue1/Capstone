import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import FeatureProductSection from './FeatureProductSection';

describe('<FeatureProductSection />', () => {
  test('it should mount', () => {
    render(<FeatureProductSection />);
    
    const featureProductSection = screen.getByTestId('FeatureProductSection');

    expect(featureProductSection).toBeInTheDocument();
  });
});