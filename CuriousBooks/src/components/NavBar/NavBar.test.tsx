import { screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { render } from '@testing-library/react';
import { vi } from 'vitest';
import '@testing-library/jest-dom';
import NavBar from './NavBar';
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
  createdAt: '2024-01-15T00:00:00.000Z',
};

function LocationDisplay() {
  const location = useLocation();
  return <div data-testid="location">{location.pathname}</div>;
}

function renderLoggedInNav(initialPath: string, onLogout = vi.fn()) {
  render(
    <MemoryRouter initialEntries={[initialPath]} future={routerFuture}>
      <Routes>
        <Route
          path="*"
          element={
            <>
              <NavBar isLoggedIn user={mockUser} onLogout={onLogout} />
              <LocationDisplay />
            </>
          }
        />
      </Routes>
    </MemoryRouter>,
  );
  return { onLogout };
}

function clickLogout() {
  fireEvent.click(screen.getByRole('button', { name: /Ada/i }));
  fireEvent.click(screen.getByRole('button', { name: /Log Out/i }));
}

describe('<NavBar />', () => {
  test('it should mount', () => {
    render(
      <MemoryRouter future={routerFuture}>
        <NavBar />
      </MemoryRouter>,
    );

    const navBar = screen.getByTestId('NavBar');

    expect(navBar).toBeInTheDocument();
  });

  test('Login link includes redirect back to the current page', () => {
    render(
      <MemoryRouter initialEntries={['/search?q=fiction']} future={routerFuture}>
        <Routes>
          <Route path="*" element={<NavBar />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByRole('link', { name: /Login/i })).toHaveAttribute(
      'href',
      '/login?redirect=%2Fsearch%3Fq%3Dfiction',
    );
  });

  test('logout stays on the current page by default', () => {
    const { onLogout } = renderLoggedInNav('/search?q=fiction');

    clickLogout();

    expect(onLogout).toHaveBeenCalled();
    expect(screen.getByTestId('location')).toHaveTextContent('/search');
  });

  test.each([
    ['/profile', '/'],
    ['/orders', '/'],
    ['/orders/order-1', '/'],
    ['/manage/books', '/'],
  ])('logout from %s redirects to home', (initialPath, expectedPath) => {
    const { onLogout } = renderLoggedInNav(initialPath);

    clickLogout();

    expect(onLogout).toHaveBeenCalled();
    expect(screen.getByTestId('location')).toHaveTextContent(expectedPath);
  });
});
