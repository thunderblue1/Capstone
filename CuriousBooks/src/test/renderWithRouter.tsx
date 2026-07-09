import { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

const routerFuture = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
} as const;

export function renderWithRouter(ui: ReactElement, options?: RenderOptions) {
  return render(<MemoryRouter future={routerFuture}>{ui}</MemoryRouter>, options);
}
