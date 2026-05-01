import { FC } from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

interface FooterProps {}

const Footer: FC<FooterProps> = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer" data-testid="Footer">
      <div className="footer__container">
        <div className="footer__section footer__brand">
          <Link to="/" className="footer__logo">
            <span className="footer__logo-icon">📚</span>
            <span className="footer__logo-text">Curious Books</span>
          </Link>
          <p className="footer__tagline">
            Seamless transitions from one great find to the next.
          </p>
        </div>

        <div className="footer__section footer__products">
          <h4 className="footer__heading">Products</h4>
          <ul className="footer__list">
            <li><Link to="/search?category=books">Books</Link></li>
            <li><Link to="/search?category=stationary">Stationary</Link></li>
            <li><Link to="/search?category=gifts">Gifts</Link></li>
          </ul>
        </div>

        <div className="footer__section footer__contact">
          <h4 className="footer__heading">Contact</h4>
          <ul className="footer__list footer__contact-list">
            <li>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                <polyline points="22,6 12,13 2,6" />
              </svg>
              <a href="mailto:admin@keen.engineer">admin@keen.engineer</a>
            </li>
            <li>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
              </svg>
              <span>1 (555) 8888</span>
            </li>
            <li>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              <span>333 Grey Color RD, OK</span>
            </li>
          </ul>
        </div>
      </div>

      <div className="footer__bottom">
        <p>&copy; {currentYear} Keen Engineering LLC. All rights reserved.</p>
        <div className="footer__social">
          <a href="#" aria-label="Facebook" className="social-link">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z" />
            </svg>
          </a>
          <a href="#" aria-label="Twitter" className="social-link">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z" />
            </svg>
          </a>
          <a href="#" aria-label="Instagram" className="social-link">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
              <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
              <line x1="17.5" y1="6.5" x2="17.51" y2="6.5" />
            </svg>
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
