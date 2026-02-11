/**
 * OrdersPage Component
 * ===================
 * 
 * Purpose:
 *   Displays a list of all user orders with key information.
 *   Allows navigation to individual order details.
 * 
 * Features:
 *   - List of all user orders
 *   - Order summary (date, status, total)
 *   - Link to order details
 *   - Loading and error state handling
 *   - Empty state when no orders exist
 * 
 * Data Flow:
 *   1. Checks authentication status
 *   2. Fetches orders via ordersApi.getAll()
 *   3. Displays orders in a list format
 * 
 * Props:
 *   - isLoggedIn: Authentication state
 *   - user: Current user object
 *   - userAvatar: User avatar URL
 *   - onLogout: Logout handler
 *   - cartItemCount: Number of items in cart
 * 
 * Usage:
 *   <Route path="/orders" element={<OrdersPage {...props} />} />
 */
import React, { FC, useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import NavBar from '../NavBar/NavBar';
import Footer from '../Footer/Footer';
import { ordersApi, ApiError } from '../../services/api';
import { logger } from '../../services/logger';
import type { Order, User } from '../../services/types';
import './OrdersPage.css';

interface OrdersPageProps {
  isLoggedIn?: boolean;
  user?: User | null;
  userAvatar?: string | null;
  onLogout?: () => void;
  cartItemCount?: number;
}

const OrdersPage: FC<OrdersPageProps> = ({
  isLoggedIn = false,
  user = null,
  userAvatar = null,
  onLogout,
  cartItemCount = 0,
}) => {
  const navigate = useNavigate();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoggedIn) {
      navigate('/login?redirect=' + encodeURIComponent('/orders'));
      return;
    }

    const fetchOrders = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await ordersApi.getAll();
        setOrders(response.orders);
        logger.application.info('Orders loaded', { orderCount: response.orders.length, component: 'OrdersPage' });
      } catch (err) {
        logger.error.log(err, { component: 'OrdersPage' });
        if (err instanceof ApiError) {
          if (err.status === 401) {
            navigate('/login?redirect=' + encodeURIComponent('/orders'));
          } else {
            setError(err.message || 'Failed to load orders');
          }
        } else {
          setError('An unexpected error occurred');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, [isLoggedIn, navigate]);

  const formatPrice = (price: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(price);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Paid':
        return 'status-paid';
      case 'Shipped':
        return 'status-shipped';
      case 'Delivered':
        return 'status-delivered';
      case 'Cancelled':
        return 'status-cancelled';
      default:
        return 'status-pending';
    }
  };

  if (loading) {
    return (
      <div className="orders-page">
        <NavBar
          isLoggedIn={isLoggedIn}
          user={user}
          userAvatar={userAvatar}
          onLogout={onLogout}
          cartItemCount={cartItemCount}
        />
        <main className="orders-main">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading orders...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (error) {
    return (
      <div className="orders-page">
        <NavBar
          isLoggedIn={isLoggedIn}
          user={user}
          userAvatar={userAvatar}
          onLogout={onLogout}
          cartItemCount={cartItemCount}
        />
        <main className="orders-main">
          <div className="error-container">
            <h2>Error</h2>
            <p>{error}</p>
            <Link to="/" className="back-button">Return to Home</Link>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="orders-page">
      <NavBar
        isLoggedIn={isLoggedIn}
        user={user}
        userAvatar={userAvatar}
        onLogout={onLogout}
        cartItemCount={cartItemCount}
      />
      <main className="orders-main">
        <div className="orders-container">
          <div className="orders-header">
            <h1>My Orders</h1>
            <p className="orders-subtitle">View and manage your order history</p>
          </div>

          {orders.length === 0 ? (
            <div className="orders-empty">
              <div className="orders-empty__icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
                  <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
                  <path d="M9 12h6" />
                  <path d="M9 16h6" />
                </svg>
              </div>
              <h2>No orders yet</h2>
              <p>You haven't placed any orders. Start shopping to see your orders here!</p>
              <Link to="/search" className="btn-primary">
                Start Shopping
              </Link>
            </div>
          ) : (
            <div className="orders-list">
              {orders.map((order) => (
                <Link key={order.id} to={`/orders/${order.id}`} className="order-card">
                  <div className="order-card__header">
                    <div className="order-card__info">
                      <h3>Order #{order.id}</h3>
                      <p className="order-card__date">{formatDate(order.createdAt)}</p>
                    </div>
                    <div className={`order-card__status ${getStatusColor(order.status)}`}>
                      {order.status}
                    </div>
                  </div>
                  <div className="order-card__body">
                    <div className="order-card__items">
                      <p className="order-card__items-count">
                        {order.items.length} {order.items.length === 1 ? 'item' : 'items'}
                      </p>
                      {order.items.length > 0 && order.items[0].book && (
                        <p className="order-card__items-preview">
                          {order.items[0].book.title}
                          {order.items.length > 1 && ` and ${order.items.length - 1} more`}
                        </p>
                      )}
                    </div>
                    <div className="order-card__total">
                      {formatPrice(order.totalAmount, order.currency)}
                    </div>
                  </div>
                  <div className="order-card__footer">
                    <span className="order-card__view-details">View Details →</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default OrdersPage;

