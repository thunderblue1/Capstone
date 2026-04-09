import React, { FC, useState, useRef, useEffect } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import BookSearchBox from '../BookSearchBox/BookSearchBox';
import type { User } from '../../services/types';
import './NavBar.css';

interface NavBarProps {
  isLoggedIn?: boolean;
  user?: User | null;
  userAvatar?: string | null;
  cartItemCount?: number;
  onLogout?: () => void;
}

const NavBar: FC<NavBarProps> = ({ 
  isLoggedIn = false, 
  user = null,
  userAvatar = null,
  cartItemCount = 0,
  onLogout 
}) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    setShowDropdown(false);
    onLogout?.();
    navigate('/');
  };

  const getUserInitials = () => {
    if (user?.firstName && user?.lastName) {
      return `${user.firstName.charAt(0)}${user.lastName.charAt(0)}`.toUpperCase();
    }
    if (user?.firstName) {
      return user.firstName.charAt(0).toUpperCase();
    }
    if (user?.username) {
      return user.username.charAt(0).toUpperCase();
    }
    return 'U';
  };

  const getDisplayName = () => {
    if (user?.firstName) {
      return user.firstName;
    }
    return user?.username || 'User';
  };

  return (
    <nav className="navbar" data-testid="NavBar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">📚</span>
          <span className="logo-text">Curious Books</span>
        </Link>

        <div className="navbar-menu">
          <NavLink 
            to="/" 
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            Home
          </NavLink>
          <NavLink 
            to="/search" 
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            Search All Books
          </NavLink>
          <NavLink 
            to="/about" 
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            About Us
          </NavLink>
        </div>

        <div className="navbar-search">
          <BookSearchBox />
        </div>

        <div className="navbar-actions">
          <Link to="/cart" className="cart-link" aria-label="Shopping cart">
            <svg 
              className="cart-icon" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2"
            >
              <circle cx="9" cy="21" r="1" />
              <circle cx="20" cy="21" r="1" />
              <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
            </svg>
            {cartItemCount > 0 && (
              <span className="cart-badge">{cartItemCount}</span>
            )}
          </Link>

          {isLoggedIn ? (
            <div className="profile-container" ref={dropdownRef}>
              <button 
                className="profile-button"
                onClick={() => setShowDropdown(!showDropdown)}
                aria-expanded={showDropdown}
                aria-haspopup="true"
              >
                <div className="profile-avatar">
                  {userAvatar ? (
                    <img 
                      src={userAvatar} 
                      alt={`${getDisplayName()}'s avatar`}
                      className="profile-avatar__image"
                    />
                  ) : (
                    <span className="profile-avatar__initials">
                      {getUserInitials()}
                    </span>
                  )}
                  <span className="profile-avatar__status"></span>
                </div>
                <span className="profile-name">{getDisplayName()}</span>
                <svg 
                  className={`profile-chevron ${showDropdown ? 'profile-chevron--open' : ''}`}
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor" 
                  strokeWidth="2"
                >
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </button>

              {showDropdown && (
                <div className="profile-dropdown">
                  <div className="profile-dropdown__header">
                    <div className="profile-dropdown__avatar">
                      {userAvatar ? (
                        <img src={userAvatar} alt="" />
                      ) : (
                        <span>{getUserInitials()}</span>
                      )}
                    </div>
                    <div className="profile-dropdown__info">
                      <span className="profile-dropdown__name">
                        {user?.firstName ? `${user.firstName} ${user.lastName || ''}`.trim() : user?.username}
                      </span>
                      <span className="profile-dropdown__email">{user?.email}</span>
                    </div>
                  </div>
                  
                  <div className="profile-dropdown__divider"></div>
                  
                  <Link 
                    to="/profile" 
                    className="profile-dropdown__item"
                    onClick={() => setShowDropdown(false)}
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                      <circle cx="12" cy="7" r="4" />
                    </svg>
                    My Profile
                  </Link>
                  
                  <Link 
                    to="/orders" 
                    className="profile-dropdown__item"
                    onClick={() => setShowDropdown(false)}
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                      <line x1="16" y1="13" x2="8" y2="13" />
                      <line x1="16" y1="17" x2="8" y2="17" />
                    </svg>
                    My Orders
                  </Link>
                  
                  {(user?.role === 'manager' || user?.role === 'admin') && (
                    <>
                      <div className="profile-dropdown__divider"></div>
                      <Link 
                        to="/manage/books" 
                        className="profile-dropdown__item"
                        onClick={() => setShowDropdown(false)}
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
                          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
                          <line x1="8" y1="7" x2="18" y2="7" />
                          <line x1="8" y1="11" x2="18" y2="11" />
                        </svg>
                        Manage Books
                      </Link>
                    </>
                  )}
                  
                  <div className="profile-dropdown__divider"></div>
                  
                  <button 
                    className="profile-dropdown__item profile-dropdown__item--logout"
                    onClick={handleLogout}
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                      <polyline points="16 17 21 12 16 7" />
                      <line x1="21" y1="12" x2="9" y2="12" />
                    </svg>
                    Log Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link to="/login" className="login-link">
              <svg 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2"
                className="login-icon"
              >
                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
                <polyline points="10 17 15 12 10 7" />
                <line x1="15" y1="12" x2="3" y2="12" />
              </svg>
              Login
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default NavBar;
