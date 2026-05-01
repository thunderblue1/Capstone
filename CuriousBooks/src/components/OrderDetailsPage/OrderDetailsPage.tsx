import { FC, useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import NavBar from '../NavBar/NavBar';
import Footer from '../Footer/Footer';
import { ordersApi, ApiError } from '../../services/api';
import { logger } from '../../services/logger';
import type { Order, User } from '../../services/types';
import './OrderDetailsPage.css';

interface OrderDetailsPageProps {
  isLoggedIn?: boolean;
  user?: User | null;
  userAvatar?: string | null;
  onLogout?: () => void;
  cartItemCount?: number;
}

const OrderDetailsPage: FC<OrderDetailsPageProps> = ({
  isLoggedIn = false,
  user = null,
  userAvatar = null,
  onLogout,
  cartItemCount = 0,
}) => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoggedIn) {
      navigate('/login?redirect=' + encodeURIComponent(`/orders/${id}`));
      return;
    }

    const fetchOrder = async () => {
      if (!id) {
        setError('Order ID is required');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const orderData = await ordersApi.getById(id);
        setOrder(orderData);
        logger.application.info('Order details loaded', { orderId: id, component: 'OrderDetailsPage' });
      } catch (err) {
        logger.error.log(err, { component: 'OrderDetailsPage' });
        if (err instanceof ApiError) {
          if (err.status === 404) {
            setError('Order not found');
          } else if (err.status === 401) {
            navigate('/login?redirect=' + encodeURIComponent(`/orders/${id}`));
          } else {
            setError(err.message || 'Failed to load order details');
          }
        } else {
          setError('An unexpected error occurred');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchOrder();
  }, [id, isLoggedIn, navigate]);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: order?.currency || 'USD',
    }).format(price);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
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
      <div className="order-details-page">
        <NavBar
          isLoggedIn={isLoggedIn}
          user={user}
          userAvatar={userAvatar}
          onLogout={onLogout}
          cartItemCount={cartItemCount}
        />
        <main className="order-details-main">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading order details...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="order-details-page">
        <NavBar
          isLoggedIn={isLoggedIn}
          user={user}
          userAvatar={userAvatar}
          onLogout={onLogout}
          cartItemCount={cartItemCount}
        />
        <main className="order-details-main">
          <div className="error-container">
            <h2>Error</h2>
            <p>{error || 'Order not found'}</p>
            <Link to="/" className="back-button">Return to Home</Link>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  const subtotal = order.items.reduce((sum, item) => sum + (item.subtotal || 0), 0);
  const tax = subtotal * 0.08;
  const total = subtotal + tax;

  return (
    <div className="order-details-page">
      <NavBar
        isLoggedIn={isLoggedIn}
        user={user}
        userAvatar={userAvatar}
        onLogout={onLogout}
        cartItemCount={cartItemCount}
      />
      <main className="order-details-main">
        <div className="order-details-container">
          <div className="order-header">
            <div>
              <h1>Order Details</h1>
              <p className="order-number">Order #{order.id}</p>
            </div>
            <div className={`order-status ${getStatusColor(order.status)}`}>
              {order.status}
            </div>
          </div>

          <div className="order-info-grid">
            <div className="order-section">
              <h2>Order Information</h2>
              <div className="info-row">
                <span className="info-label">Order Date:</span>
                <span className="info-value">{formatDate(order.createdAt)}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Status:</span>
                <span className={`info-value ${getStatusColor(order.status)}`}>
                  {order.status}
                </span>
              </div>
              {order.stripePaymentIntentId && (
                <div className="info-row">
                  <span className="info-label">Payment ID:</span>
                  <span className="info-value" style={{ fontFamily: 'monospace', fontSize: '0.9rem' }}>
                    {order.stripePaymentIntentId}
                  </span>
                </div>
              )}
              {order.updatedAt && order.updatedAt !== order.createdAt && (
                <div className="info-row">
                  <span className="info-label">Last Updated:</span>
                  <span className="info-value">{formatDate(order.updatedAt)}</span>
                </div>
              )}
            </div>

            {order.items && order.items.length > 0 && (
              <div className="order-section">
                <h2>Items</h2>
                <div className="order-items-list">
                  {order.items.map((item) => (
                    <div key={item.id} className="order-item">
                      <div className="item-info">
                        {item.book && (
                          <>
                            <h3>{item.book.title}</h3>
                            <p className="item-author">by {item.book.author}</p>
                          </>
                        )}
                        <p className="item-quantity">Quantity: {item.quantity}</p>
                        <p className="item-price">
                          {formatPrice(item.unitPrice)} × {item.quantity} = {formatPrice(item.subtotal || 0)}
                        </p>
                      </div>
                      {item.book && (
                        <div className="item-image">
                          <img
                            src={item.book.imageUrl || 'https://via.placeholder.com/80x120?text=Book'}
                            alt={item.book.title}
                            onError={(e) => {
                              const target = e.target as HTMLImageElement;
                              target.src = 'https://via.placeholder.com/80x120?text=Book';
                              target.style.backgroundColor = '#f0f0f0';
                            }}
                          />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="order-section">
              <h2>Order Summary</h2>
              <div className="summary-row">
                <span>Subtotal:</span>
                <span>{formatPrice(subtotal)}</span>
              </div>
              <div className="summary-row">
                <span>Tax (8%):</span>
                <span>{formatPrice(tax)}</span>
              </div>
              <div className="summary-row summary-total">
                <span>Total:</span>
                <span>{formatPrice(order.totalAmount || total)}</span>
              </div>
            </div>
          </div>

          <div className="order-actions">
            <Link to="/" className="back-button">Continue Shopping</Link>
            <Link to="/orders" className="orders-button">View All Orders</Link>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default OrderDetailsPage;

