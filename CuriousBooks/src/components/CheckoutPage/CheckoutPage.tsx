import { FC, useState, useEffect, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';
import NavBar from '../NavBar/NavBar';
import Footer from '../Footer/Footer';
import type { User, CartItem } from '../../services/types';
import { ordersApi } from '../../services/api';
import { logger } from '../../services/logger';
import './CheckoutPage.css';

interface CartItemWithBook extends CartItem {
  book: {
    id: string;
    title: string;
    author: string;
    price: number;
  };
}

interface CheckoutPageProps {
  cartItems: CartItemWithBook[];
  onClearCart?: () => void;
  isLoggedIn?: boolean;
  user?: User | null;
  userAvatar?: string | null;
  onLogout?: () => void;
}

interface ShippingFormData {
  customerName: string;
  customerEmail: string;
  line1: string;
  line2: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
}

const CheckoutForm: FC<{
  cartItems: CartItemWithBook[];
  user: User | null;
  onSuccess: (orderId: string) => void;
}> = ({ cartItems, user, onSuccess }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [paymentIntentId, setPaymentIntentId] = useState<string | null>(null);
  const [formData, setFormData] = useState<ShippingFormData>({
    customerName: user?.firstName && user?.lastName 
      ? `${user.firstName} ${user.lastName}` 
      : user?.username || '',
    customerEmail: user?.email || '',
    line1: '',
    line2: '',
    city: '',
    state: '',
    postalCode: '',
    country: 'US',
  });

  // Calculate totals
  const subtotal = cartItems.reduce((sum, item) => sum + (item.book.price * item.quantity), 0);
  const tax = subtotal * 0.08;
  const total = subtotal + tax;

  // Create payment intent when all required shipping fields are filled
  useEffect(() => {
    // Only create if we don't already have a client secret
    if (clientSecret) return;

    // Check if all required shipping fields are filled
    if (!formData.line1 || !formData.city || !formData.state || !formData.postalCode || !formData.customerEmail || !formData.customerName) {
      return;
    }

    const createIntent = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const items = cartItems.map(item => ({
          bookId: item.bookId,
          quantity: item.quantity,
        }));

        const response = await ordersApi.createStripeIntent({
          items,
          customerEmail: formData.customerEmail,
          customerName: formData.customerName,
          shippingAddress: {
            line1: formData.line1,
            line2: formData.line2,
            city: formData.city,
            state: formData.state,
            postalCode: formData.postalCode,
            country: formData.country,
          },
        });

        setClientSecret(response.clientSecret);
        setPaymentIntentId(response.paymentIntentId);
      } catch (err: any) {
        logger.error.log(err, { component: 'CheckoutForm' });
        const errorMessage = err.message || err.toString() || 'Failed to initialize payment';
        setError(errorMessage);
        console.error('Payment intent creation error:', err);
      } finally {
        setLoading(false);
      }
    };

    createIntent();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData.line1, formData.city, formData.state, formData.postalCode, formData.customerEmail, formData.customerName, formData.country]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();

    if (!stripe || !elements || !clientSecret || !paymentIntentId) {
      return;
    }

    setLoading(true);
    setError(null);

    const cardElement = elements.getElement(CardElement);
    if (!cardElement) {
      setError('Card element not found');
      setLoading(false);
      return;
    }

    try {
      // Confirm payment with Stripe
      const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: cardElement,
          billing_details: {
            name: formData.customerName,
            email: formData.customerEmail,
            address: {
              line1: formData.line1,
              line2: formData.line2 || undefined,
              city: formData.city,
              state: formData.state,
              postal_code: formData.postalCode,
              country: formData.country,
            },
          },
        },
      });

      if (stripeError) {
        setError(stripeError.message || 'Payment failed');
        setLoading(false);
        return;
      }

      if (paymentIntent?.status === 'succeeded') {
        // Confirm payment on backend and create order
        const items = cartItems.map(item => ({
          bookId: item.bookId,
          quantity: item.quantity,
        }));

        const response = await ordersApi.confirmStripePayment({
          paymentIntentId,
          items,
          customerEmail: formData.customerEmail,
          customerName: formData.customerName,
          shippingAddress: {
            line1: formData.line1,
            line2: formData.line2,
            city: formData.city,
            state: formData.state,
            postalCode: formData.postalCode,
            country: formData.country,
          },
        });

        logger.application.info('Order created successfully', { 
          orderId: response.order.id,
          component: 'CheckoutForm' 
        });

        onSuccess(response.order.id);
      }
    } catch (err: any) {
      logger.error.log(err, { component: 'CheckoutForm' });
      setError(err.message || 'Failed to process payment');
      setLoading(false);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const cardElementOptions = {
    style: {
      base: {
        fontSize: '16px',
        color: '#424770',
        '::placeholder': {
          color: '#aab7c4',
        },
      },
      invalid: {
        color: '#9e2146',
      },
    },
  };

  return (
    <form onSubmit={handleSubmit} className="checkout-form">
      <div className="checkout-form__section">
        <h3>Shipping Information</h3>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="customerName">Full Name *</label>
            <input
              type="text"
              id="customerName"
              required
              value={formData.customerName}
              onChange={(e) => setFormData({ ...formData, customerName: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label htmlFor="customerEmail">Email *</label>
            <input
              type="email"
              id="customerEmail"
              required
              value={formData.customerEmail}
              onChange={(e) => setFormData({ ...formData, customerEmail: e.target.value })}
            />
          </div>
        </div>
        <div className="form-group">
          <label htmlFor="line1">Address Line 1 *</label>
          <input
            type="text"
            id="line1"
            required
            value={formData.line1}
            onChange={(e) => setFormData({ ...formData, line1: e.target.value })}
          />
        </div>
        <div className="form-group">
          <label htmlFor="line2">Address Line 2</label>
          <input
            type="text"
            id="line2"
            value={formData.line2}
            onChange={(e) => setFormData({ ...formData, line2: e.target.value })}
          />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="city">City *</label>
            <input
              type="text"
              id="city"
              required
              value={formData.city}
              onChange={(e) => setFormData({ ...formData, city: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label htmlFor="state">State *</label>
            <input
              type="text"
              id="state"
              required
              value={formData.state}
              onChange={(e) => setFormData({ ...formData, state: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label htmlFor="postalCode">ZIP Code *</label>
            <input
              type="text"
              id="postalCode"
              required
              value={formData.postalCode}
              onChange={(e) => setFormData({ ...formData, postalCode: e.target.value })}
            />
          </div>
        </div>
        <div className="form-group">
          <label htmlFor="country">Country *</label>
          <select
            id="country"
            required
            value={formData.country}
            onChange={(e) => setFormData({ ...formData, country: e.target.value })}
          >
            <option value="US">United States</option>
            <option value="CA">Canada</option>
            <option value="GB">United Kingdom</option>
          </select>
        </div>
      </div>

      <div className="checkout-form__section">
        <h3>Payment Information</h3>
        <div className="card-element-container">
          <CardElement options={cardElementOptions} />
        </div>
      </div>

      {error && (
        <div className="checkout-error">
          {error}
        </div>
      )}

      <div className="checkout-summary">
        <div className="summary-row">
          <span>Subtotal</span>
          <span>{formatPrice(subtotal)}</span>
        </div>
        <div className="summary-row">
          <span>Tax</span>
          <span>{formatPrice(tax)}</span>
        </div>
        <div className="summary-row summary-total">
          <span>Total</span>
          <span>{formatPrice(total)}</span>
        </div>
      </div>

      <button
        type="submit"
        className="checkout-submit-btn"
        disabled={!stripe || loading || !clientSecret}
      >
        {loading ? 'Processing...' : `Pay ${formatPrice(total)}`}
      </button>
    </form>
  );
};

const CheckoutPage: FC<CheckoutPageProps> = ({
  cartItems,
  onClearCart,
  isLoggedIn = false,
  user = null,
  userAvatar = null,
  onLogout,
}) => {
  const navigate = useNavigate();
  const [stripePromise, setStripePromise] = useState<Promise<any> | null>(null);
  const [orderId, setOrderId] = useState<string | null>(null);

  const totalItemCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);

  useEffect(() => {
    if (!isLoggedIn) {
      // Navigate to login with redirect info to return to checkout after login
      navigate('/login?redirect=/checkout&from=checkout');
      return;
    }

    if (cartItems.length === 0) {
      navigate('/cart');
      return;
    }

    // Load Stripe
    const loadStripeConfig = async () => {
      try {
        const config = await ordersApi.getStripeConfig();
        if (config.publishableKey) {
          setStripePromise(loadStripe(config.publishableKey));
        } else {
          logger.error.log('Stripe publishable key not configured', { component: 'CheckoutPage' });
        }
      } catch (err) {
        logger.error.log(err, { component: 'CheckoutPage' });
      }
    };

    loadStripeConfig();
  }, [isLoggedIn, cartItems.length, navigate]);

  const handleSuccess = (orderId: string) => {
    setOrderId(orderId);
    onClearCart?.();
    setTimeout(() => {
      navigate(`/orders/${orderId}`);
    }, 2000);
  };

  if (orderId) {
    return (
      <div className="checkout-page">
        <NavBar
          cartItemCount={0}
          isLoggedIn={isLoggedIn}
          user={user}
          userAvatar={userAvatar}
          onLogout={onLogout}
        />
        <main className="checkout-page__main">
          <div className="checkout-success">
            <div className="success-icon">✓</div>
            <h2>Payment Successful!</h2>
            <p>Your order has been placed successfully.</p>
            <p>Order ID: {orderId}</p>
            <p>Redirecting to order details...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (!stripePromise) {
    return (
      <div className="checkout-page">
        <NavBar
          cartItemCount={totalItemCount}
          isLoggedIn={isLoggedIn}
          user={user}
          userAvatar={userAvatar}
          onLogout={onLogout}
        />
        <main className="checkout-page__main">
          <div className="checkout-loading">
            <p>Loading checkout...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="checkout-page">
      <NavBar
        cartItemCount={totalItemCount}
        isLoggedIn={isLoggedIn}
        user={user}
        userAvatar={userAvatar}
        onLogout={onLogout}
      />
      <main className="checkout-page__main">
        <div className="checkout-container">
          <h1 className="checkout-title">Checkout</h1>
          <Elements stripe={stripePromise}>
            <CheckoutForm cartItems={cartItems} user={user} onSuccess={handleSuccess} />
          </Elements>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default CheckoutPage;

