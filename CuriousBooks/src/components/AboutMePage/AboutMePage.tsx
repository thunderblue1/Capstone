import { FC } from 'react';
import NavBar from '../NavBar/NavBar';
import Footer from '../Footer/Footer';
import type { Book, User } from '../../services/types';
import './AboutMePage.css';

interface AboutMePageProps {
  cartItems?: Book[];
  isLoggedIn?: boolean;
  user?: User | null;
  userAvatar?: string | null;
  cartItemCount?: number;
  onLogout?: () => void;
}

const AboutMePage: FC<AboutMePageProps> = ({ 
  isLoggedIn = false,
  user = null,
  userAvatar = null,
  cartItemCount = 0,
  onLogout,
}) => {
  return (
    <div className="about-page" data-testid="AboutMePage">
      <NavBar 
        cartItemCount={cartItemCount}
        isLoggedIn={isLoggedIn}
        user={user}
        userAvatar={userAvatar}
        onLogout={onLogout}
      />
      <main className="about-page__main">
        <section className="about-hero">
          <div className="about-hero__overlay"></div>
          <div className="about-hero__content">
            <h1>About Curious Books</h1>
            <p>Your journey to discovery starts here</p>
          </div>
        </section>

        <section className="about-content">
          <div className="about-content__container">
            <div className="about-card">
              <div className="about-card__icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                  <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
                </svg>
              </div>
              <h2>Our Story</h2>
              <p>
                We are dedicated to finding the exact book you need just as soon as you need it. 
                Founded with a passion for literature and technology, Curious Books brings together 
                the timeless joy of reading with cutting-edge AI recommendations.
              </p>
            </div>

            <div className="about-card">
              <div className="about-card__icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                  <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
              </div>
              <h2>Our Mission</h2>

              <p>
                We believe that every reader deserves personalized recommendations that match 
                their unique tastes and interests. Our AI-powered system learns from your 
                preferences to suggest books you'll love.
              </p>
            </div>

            <div className="about-card about-card--full">
              <div className="about-card__icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
              </div>
              <h2>Why Choose Us</h2>
              <div className="features-grid">
                <div className="feature">
                  <h3>AI-Powered Recommendations</h3>
                  <p>Our intelligent system learns your preferences to suggest books you'll love.</p>
                </div>
                <div className="feature">
                  <h3>Vast Selection</h3>
                  <p>Access to thousands of titles across all genres and categories.</p>
                </div>
                <div className="feature">
                  <h3>Seamless Experience</h3>
                  <p>Easy navigation from discovery to purchase, all in one place.</p>
                </div>
                <div className="feature">
                  <h3>Community Reviews</h3>
                  <p>Read honest reviews from fellow book lovers before you buy.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="about-cta">
          <div className="about-cta__container">
            <h2>Ready to Find Your Next Great Read?</h2>
            <p>Join thousands of book lovers who trust Curious Books for their reading adventures.</p>
            <a href="/search" className="btn-accent btn-large">Start Exploring</a>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
};

export default AboutMePage;
