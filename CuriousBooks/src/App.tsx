import React, { useState, useCallback } from 'react';
import { Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage/LandingPage';
import ResultsPage from './components/ResultsPage/ResultsPage';
import BookSynopsisPage from './components/BookSynopsisPage/BookSynopsisPage';
import AboutMePage from './components/AboutMePage/AboutMePage';
import LoginPage from './components/LoginPage/LoginPage';
import CartPage from './components/CartPage/CartPage';
import CheckoutPage from './components/CheckoutPage/CheckoutPage';
import OrderDetailsPage from './components/OrderDetailsPage/OrderDetailsPage';
import OrdersPage from './components/OrdersPage/OrdersPage';
import ManagerBooksPage from './components/ManagerBooksPage/ManagerBooksPage';
import type { Book, User, CartItem } from './services/types';
import { logger } from './services/logger';
import './App.css';

// Extended cart item with book data
interface CartItemWithBook extends CartItem {
  book: Book;
}

function App() {
  const [cartItems, setCartItems] = useState<CartItemWithBook[]>([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [userAvatar, setUserAvatar] = useState<string | null>(null);

  const handleAddToCart = useCallback((book: Book) => {
    setCartItems(prev => {
      // Check if book already in cart
      const existingItem = prev.find(item => item.bookId === book.id);
      if (existingItem) {
        // Increment quantity if already in cart
        logger.application.info('Book quantity increased in cart', { bookId: book.id, bookTitle: book.title, quantity: existingItem.quantity + 1 });
        return prev.map(item => 
          item.bookId === book.id 
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      logger.application.info('Book added to cart', { bookId: book.id, bookTitle: book.title });
      return [...prev, { bookId: book.id, quantity: 1, book }];
    });
  }, []);

  const handleRemoveFromCart = useCallback((bookId: string) => {
    logger.application.info('Book removed from cart', { bookId });
    setCartItems(prev => prev.filter(item => item.bookId !== bookId));
  }, []);

  const handleUpdateQuantity = useCallback((bookId: string, quantity: number) => {
    if (quantity <= 0) {
      handleRemoveFromCart(bookId);
      return;
    }
    logger.application.info('Cart quantity updated', { bookId, quantity });
    setCartItems(prev => 
      prev.map(item => 
        item.bookId === bookId 
          ? { ...item, quantity }
          : item
      )
    );
  }, [handleRemoveFromCart]);

  const handleClearCart = useCallback(() => {
    logger.application.info('Cart cleared');
    setCartItems([]);
  }, []);

  const handleLogin = useCallback((email: string, password: string, user?: User) => {
    logger.application.info('Login successful', { email, component: 'App' });
    setIsLoggedIn(true);
    
    // Set user data from API response or create fallback
    const userData: User = user || {
      id: 'user_' + Date.now(),
      username: email.split('@')[0],
      email: email,
      firstName: email.split('@')[0].charAt(0).toUpperCase() + email.split('@')[0].slice(1),
      lastName: null,
      createdAt: new Date().toISOString(),
    };
    setCurrentUser(userData);
    
    // Set avatar (could be from user profile or generated)
    // Using UI Avatars service for demo - generates avatar from initials
    const name = userData.firstName || userData.username;
    setUserAvatar(`https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=2e7d32&color=fff&size=128`);
  }, []);

  const handleLogout = useCallback(() => {
    logger.application.info('User logged out', { userId: currentUser?.id, component: 'App' });
    setIsLoggedIn(false);
    setCurrentUser(null);
    setUserAvatar(null);
  }, [currentUser?.id]);

  // Calculate total cart item count (sum of quantities)
  const totalCartItemCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);

  // Common props for pages with NavBar
  const navBarProps = {
    isLoggedIn,
    user: currentUser,
    userAvatar,
    onLogout: handleLogout,
    cartItemCount: totalCartItemCount,
  };

  return (
    <div className="app">
      <Routes>
        <Route 
          path="/" 
          element={
            <LandingPage 
              cartItems={cartItems.map(item => item.book)} 
              onAddToCart={handleAddToCart}
              {...navBarProps}
            />
          } 
        />
        <Route 
          path="/search" 
          element={
            <ResultsPage 
              cartItems={cartItems.map(item => item.book)} 
              onAddToCart={handleAddToCart}
              {...navBarProps}
            />
          } 
        />
        <Route 
          path="/book/:id" 
          element={
            <BookSynopsisPage 
              cartItems={cartItems.map(item => item.book)} 
              onAddToCart={handleAddToCart}
              {...navBarProps}
            />
          } 
        />
        <Route 
          path="/about" 
          element={<AboutMePage cartItems={cartItems.map(item => item.book)} {...navBarProps} />} 
        />
        <Route 
          path="/login" 
          element={<LoginPage onLogin={handleLogin} />} 
        />
        <Route 
          path="/cart" 
          element={
            <CartPage 
              cartItems={cartItems}
              onRemoveFromCart={handleRemoveFromCart}
              onUpdateQuantity={handleUpdateQuantity}
              onClearCart={handleClearCart}
              {...navBarProps}
            />
          } 
        />
        <Route 
          path="/checkout" 
          element={
            <CheckoutPage 
              cartItems={cartItems}
              onClearCart={handleClearCart}
              {...navBarProps}
            />
          } 
        />
        <Route 
          path="/orders" 
          element={
            <OrdersPage {...navBarProps} />
          } 
        />
        <Route 
          path="/orders/:id" 
          element={
            <OrderDetailsPage {...navBarProps} />
          } 
        />
        <Route 
          path="/profile" 
          element={
            isLoggedIn ? (
              <AboutMePage cartItems={cartItems.map(item => item.book)} {...navBarProps} />
            ) : (
              <LoginPage onLogin={handleLogin} />
            )
          } 
        />
        <Route 
          path="/manage/books" 
          element={
            <ManagerBooksPage {...navBarProps} />
          } 
        />
      </Routes>
    </div>
  );
}

export default App;











