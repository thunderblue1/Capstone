import { FC } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import NavBar from '../NavBar/NavBar';
import Footer from '../Footer/Footer';
import StarRating from '../StarRating/StarRating';
import type { Book, User, CartItem } from '../../services/types';
import './CartPage.css';

interface CartItemWithBook extends CartItem {
  book: Book;
}

interface CartPageProps {
  cartItems: CartItemWithBook[];
  onRemoveFromCart?: (bookId: string) => void;
  onUpdateQuantity?: (bookId: string, quantity: number) => void;
  onClearCart?: () => void;
  isLoggedIn?: boolean;
  user?: User | null;
  userAvatar?: string | null;
  onLogout?: () => void;
}

const CartPage: FC<CartPageProps> = ({ 
  cartItems = [], 
  onRemoveFromCart,
  onUpdateQuantity,
  onClearCart,
  isLoggedIn = false,
  user = null,
  userAvatar = null,
  onLogout,
}) => {
  const navigate = useNavigate();

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const subtotal = cartItems.reduce((sum, item) => sum + (item.book.price * item.quantity), 0);
  const tax = subtotal * 0.08; // 8% tax
  const total = subtotal + tax;
  const totalItemCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);

  const handleCheckout = () => {
    if (!isLoggedIn) {
      // Navigate to login with redirect info to return to checkout after login
      navigate('/login?redirect=/checkout&from=checkout');
      return;
    }
    navigate('/checkout');
  };

  return (
    <div className="cart-page" data-testid="CartPage">
      <NavBar 
        cartItemCount={totalItemCount}
        isLoggedIn={isLoggedIn}
        user={user}
        userAvatar={userAvatar}
        onLogout={onLogout}
      />
      <main className="cart-page__main">
        <div className="cart-container">
          <h1 className="cart-title">Shopping Cart</h1>

          {cartItems.length === 0 ? (
            <div className="cart-empty">
              <div className="cart-empty__icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="9" cy="21" r="1" />
                  <circle cx="20" cy="21" r="1" />
                  <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
                </svg>
              </div>
              <h2>Your cart is empty</h2>
              <p>Looks like you haven't added any books yet.</p>
              <Link to="/search" className="btn-primary">
                Start Shopping
              </Link>
            </div>
          ) : (
            <div className="cart-content">
              <div className="cart-items">
                <div className="cart-header-row">
                  <span>Product</span>
                  <span>Quantity</span>
                  <span>Price</span>
                  <span>Subtotal</span>
                  <span>Actions</span>
                </div>

                {cartItems.map((item) => (
                  <div key={item.bookId} className="cart-item">
                    <div className="cart-item__product">
                      <div className="cart-item__image">
                        <svg viewBox="0 0 80 100" className="book-thumb">
                          <defs>
                            <linearGradient id={`cart-grad-${item.bookId}`} x1="0%" y1="0%" x2="100%" y2="100%">
                              <stop offset="0%" stopColor="#00bcd4" />
                              <stop offset="100%" stopColor="#4caf50" />
                            </linearGradient>
                          </defs>
                          <rect width="80" height="100" fill={`url(#cart-grad-${item.bookId})`} rx="4" />
                          <ellipse cx="50" cy="35" rx="15" ry="10" fill="white" opacity="0.9" />
                          <ellipse cx="40" cy="38" rx="10" ry="8" fill="white" opacity="0.9" />
                          <polygon points="0,100 30,65 60,100" fill="#7cb342" />
                          <polygon points="40,100 70,55 80,100" fill="#558b2f" />
                        </svg>
                      </div>
                      <div className="cart-item__details">
                        <Link to={`/book/${item.book.id}`} className="cart-item__title">
                          {item.book.title}
                        </Link>
                        <p className="cart-item__author">by {item.book.author}</p>
                        <div className="cart-item__rating">
                          <StarRating rating={item.book.averageRating} size="sm" />
                        </div>
                      </div>
                    </div>
                    <div className="cart-item__quantity">
                      <div className="quantity-controls">
                        <button
                          className="quantity-btn"
                          onClick={() => onUpdateQuantity?.(item.bookId, item.quantity - 1)}
                          aria-label="Decrease quantity"
                        >
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="5" y1="12" x2="19" y2="12" />
                          </svg>
                        </button>
                        <span className="quantity-value">{item.quantity}</span>
                        <button
                          className="quantity-btn"
                          onClick={() => onUpdateQuantity?.(item.bookId, item.quantity + 1)}
                          aria-label="Increase quantity"
                        >
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="12" y1="5" x2="12" y2="19" />
                            <line x1="5" y1="12" x2="19" y2="12" />
                          </svg>
                        </button>
                      </div>
                    </div>
                    <div className="cart-item__price">
                      {formatPrice(item.book.price)}
                    </div>
                    <div className="cart-item__subtotal">
                      {formatPrice(item.book.price * item.quantity)}
                    </div>
                    <div className="cart-item__actions">
                      <button 
                        className="remove-btn"
                        onClick={() => onRemoveFromCart?.(item.bookId)}
                        aria-label="Remove item"
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="3 6 5 6 21 6" />
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                        </svg>
                        Remove
                      </button>
                    </div>
                  </div>
                ))}

                <div className="cart-actions">
                  <button className="clear-cart-btn" onClick={onClearCart}>
                    Clear Cart
                  </button>
                  <Link to="/search" className="continue-shopping">
                    Continue Shopping
                  </Link>
                </div>
              </div>

              <div className="cart-summary">
                <h2>Order Summary</h2>
                <div className="summary-row">
                  <span>Subtotal ({totalItemCount} {totalItemCount === 1 ? 'item' : 'items'})</span>
                  <span>{formatPrice(subtotal)}</span>
                </div>
                <div className="summary-row">
                  <span>Estimated Tax</span>
                  <span>{formatPrice(tax)}</span>
                </div>
                <div className="summary-row">
                  <span>Shipping</span>
                  <span className="free-shipping">FREE</span>
                </div>
                <div className="summary-divider"></div>
                <div className="summary-row summary-total">
                  <span>Total</span>
                  <span>{formatPrice(total)}</span>
                </div>
                <button className="checkout-btn" onClick={handleCheckout}>
                  Proceed to Checkout
                </button>
                <p className="secure-notice">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                  Secure checkout
                </p>
              </div>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default CartPage;











