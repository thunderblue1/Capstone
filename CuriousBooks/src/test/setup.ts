import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { createMockApiModule } from './mockApi';

vi.mock('../services/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api')>();
  return {
    ...actual,
    ...createMockApiModule(),
  };
});
