import { screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProfilePage from './ProfilePage';
import type { User } from '../../services/types';

const routerFuture = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
} as const;

const mockUser: User = {
  id: 'user-1',
  username: 'reader',
  email: 'reader@example.com',
  firstName: 'Ada',
  lastName: 'Lovelace',
  role: 'customer',
  createdAt: '2024-01-15T00:00:00.000Z',
};

describe('<ProfilePage />', () => {
  test('it should mount and show account details', () => {
    render(
      <MemoryRouter future={routerFuture}>
        <ProfilePage isLoggedIn user={mockUser} />
      </MemoryRouter>,
    );

    expect(screen.getByTestId('ProfilePage')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'My Profile' })).toBeInTheDocument();
    expect(screen.getByDisplayValue('Ada')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Lovelace')).toBeInTheDocument();
    expect(screen.getByDisplayValue('reader')).toBeInTheDocument();
    expect(screen.getByDisplayValue('reader@example.com')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /View My Orders/i })).toHaveAttribute(
      'href',
      '/orders',
    );
  });
});
