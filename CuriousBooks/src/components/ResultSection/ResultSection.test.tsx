import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { createMockBook } from '../../test/fixtures';
import ResultSection from './ResultSection';

describe('<ResultSection />', () => {
  test('it should mount', () => {
    render(<ResultSection title="Results" books={[createMockBook()]} />);

    const resultSection = screen.getByTestId('ResultSection');

    expect(resultSection).toBeInTheDocument();
  });
});
