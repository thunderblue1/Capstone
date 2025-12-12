import React, { FC } from 'react';
import { Link } from 'react-router-dom';
import './HeroBanner.css';

interface HeroBannerProps {}

const HeroBanner: FC<HeroBannerProps> = () => {
  return (
    <section className="hero-banner" data-testid="HeroBanner">
      <div className="hero-banner__overlay"></div>
      <div className="hero-banner__content">
        <div className="hero-banner__text">
          <h1 className="hero-banner__title">
            Deep Search For Your<br />
            <span className="hero-banner__highlight">All Time Favorite Book</span>
          </h1>
          <p className="hero-banner__subtitle">
            Discover thousands of books powered by AI recommendations
          </p>
          <Link to="/search" className="hero-banner__cta">
            Find Out More
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
        <div className="hero-banner__image">
          <div className="floating-book floating-book--1">
            <div className="book-spine"></div>
            <div className="book-cover">
              <span>Classic</span>
            </div>
          </div>
          <div className="floating-book floating-book--2">
            <div className="book-spine"></div>
            <div className="book-cover">
              <span>Adventure</span>
            </div>
          </div>
          <div className="floating-book floating-book--3">
            <div className="book-spine"></div>
            <div className="book-cover">
              <span>Mystery</span>
            </div>
          </div>
        </div>
      </div>
      <div className="hero-banner__decoration">
        <div className="deco-circle deco-circle--1"></div>
        <div className="deco-circle deco-circle--2"></div>
        <div className="deco-circle deco-circle--3"></div>
      </div>
    </section>
  );
};

export default HeroBanner;
