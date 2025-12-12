import React, { useState, useCallback } from 'react';
import { Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage/LandingPage';
import ResultsPage from './components/ResultsPage/ResultsPage';
import BookSynopsisPage from './components/BookSynopsisPage/BookSynopsisPage';
import AboutMePage from './components/AboutMePage/AboutMePage';
import LoginPage from './components/LoginPage/LoginPage';
import CartPage from './components/CartPage/CartPage';
import type { Book, User } from './services/types';
import { logger } from './services/logger';
import './App.css';

function App() {
  const [cartItems, setCartItems] = useState<Book[]>([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [userAvatar, setUserAvatar] = useState<string | null>(null);

  const handleAddToCart = useCallback((book: Book) => {
    setCartItems(prev => {
      // Check if book already in cart
      if (prev.some(item => item.id === book.id)) {
        logger.application.info('Book already in cart', { bookId: book.id, bookTitle: book.title });
        return prev;
      }
      logger.application.info('Book added to cart', { bookId: book.id, bookTitle: book.title });
      return [...prev, book];
    });
  }, []);

  const handleRemoveFromCart = useCallback((bookId: string) => {
    logger.application.info('Book removed from cart', { bookId });
    setCartItems(prev => prev.filter(item => item.id !== bookId));
  }, []);

  const handleClearCart = useCallback(() => {
    logger.application.info('Cart cleared');
    setCartItems([]);
  }, []);

  const handleLogin = useCallback((email: string, password: string, user?: User) => {
    logger.application.info('Login successful', { email, component: 'App' });
    setIsLoggedIn(true);
    
    // Set user data (in real app this would come from auth response)
    const mockUser: User = user || {
      id: 'user_' + Date.now(),
      username: email.split('@')[0],
      email: email,
      firstName: email.split('@')[0].charAt(0).toUpperCase() + email.split('@')[0].slice(1),
      lastName: null,
      createdAt: new Date().toISOString(),
    };
    setCurrentUser(mockUser);
    
    // Set avatar (could be from user profile or generated)
    // Using UI Avatars service for demo - generates avatar from initials
    const name = mockUser.firstName || mockUser.username;
    setUserAvatar(`https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=2e7d32&color=fff&size=128`);
  }, []);

  const handleLogout = useCallback(() => {
    logger.application.info('User logged out', { userId: currentUser?.id, component: 'App' });
    setIsLoggedIn(false);
    setCurrentUser(null);
    setUserAvatar(null);
  }, [currentUser?.id]);

  // Common props for pages with NavBar
  const navBarProps = {
    isLoggedIn,
    user: currentUser,
    userAvatar,
    onLogout: handleLogout,
  };

  return (
    <div className="app">
      <Routes>
        <Route 
          path="/" 
          element={
            <LandingPage 
              cartItems={cartItems} 
              onAddToCart={handleAddToCart}
              {...navBarProps}
            />
          } 
        />
        <Route 
          path="/search" 
          element={
            <ResultsPage 
              cartItems={cartItems} 
              onAddToCart={handleAddToCart}
              {...navBarProps}
            />
          } 
        />
        <Route 
          path="/book/:id" 
          element={
            <BookSynopsisPage 
              cartItems={cartItems} 
              onAddToCart={handleAddToCart}
              {...navBarProps}
            />
          } 
        />
        <Route 
          path="/about" 
          element={<AboutMePage cartItems={cartItems} {...navBarProps} />} 
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
              onClearCart={handleClearCart}
              {...navBarProps}
            />
          } 
        />
        <Route 
          path="/profile" 
          element={
            isLoggedIn ? (
              <AboutMePage cartItems={cartItems} {...navBarProps} />
            ) : (
              <LoginPage onLogin={handleLogin} />
            )
          } 
        />
      </Routes>
    </div>
  );
}

export default App;







