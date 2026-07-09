import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { createMockBook } from '../../test/fixtures';
import CartPage from './CartPage';

const book = createMockBook({ id: 'book-42', title: 'Cart Test Book', price: 10 });

function renderCart(overrides: Partial<Parameters<typeof CartPage>[0]> = {}) {
  const onRemoveFromCart = vi.fn();
  const onUpdateQuantity = vi.fn();
  const onClearCart = vi.fn();

  render(
    <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <CartPage
        cartItems={[{ bookId: book.id, quantity: 2, book }]}
        onRemoveFromCart={onRemoveFromCart}
        onUpdateQuantity={onUpdateQuantity}
        onClearCart={onClearCart}
        {...overrides}
      />
    </MemoryRouter>,
  );

  return { onRemoveFromCart, onUpdateQuantity, onClearCart };
}

describe('TC-10 Cart UI — add and remove', () => {
  test('renders cart items with quantity and totals', () => {
    renderCart();

    expect(screen.getByTestId('CartPage')).toBeInTheDocument();
    expect(screen.getByText('Cart Test Book')).toBeInTheDocument();
    expect(document.querySelector('.quantity-value')).toHaveTextContent('2');
    expect(screen.getByText('Total').closest('.summary-total')).toHaveTextContent('$21.60');
  });

  test('increase quantity calls onUpdateQuantity', () => {
    const { onUpdateQuantity } = renderCart();

    fireEvent.click(screen.getByLabelText('Increase quantity'));
    expect(onUpdateQuantity).toHaveBeenCalledWith(book.id, 3);
  });

  test('decrease quantity calls onUpdateQuantity', () => {
    const { onUpdateQuantity } = renderCart();

    fireEvent.click(screen.getByLabelText('Decrease quantity'));
    expect(onUpdateQuantity).toHaveBeenCalledWith(book.id, 1);
  });

  test('remove item calls onRemoveFromCart', () => {
    const { onRemoveFromCart } = renderCart();

    fireEvent.click(screen.getByLabelText('Remove item'));
    expect(onRemoveFromCart).toHaveBeenCalledWith(book.id);
  });

  test('clear cart calls onClearCart', () => {
    const { onClearCart } = renderCart();

    fireEvent.click(screen.getByText('Clear Cart'));
    expect(onClearCart).toHaveBeenCalled();
  });

  test('empty cart shows empty state', () => {
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <CartPage cartItems={[]} />
      </MemoryRouter>,
    );

    expect(screen.getByText('Your cart is empty')).toBeInTheDocument();
  });
});
