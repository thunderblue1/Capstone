/**
 * ProfilePage Component
 * =====================
 *
 * Displays the signed-in user's account details and lets them update
 * name/username or change their password.
 */
import { FC, useEffect, useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import NavBar from '../NavBar/NavBar';
import Footer from '../Footer/Footer';
import { authApi, ApiError } from '../../services/api';
import { buildLoginPath } from '../../services/loginRedirect';
import { logger } from '../../services/logger';
import type { User } from '../../services/types';
import './ProfilePage.css';

interface ProfilePageProps {
  isLoggedIn?: boolean;
  user?: User | null;
  userAvatar?: string | null;
  cartItemCount?: number;
  onLogout?: () => void;
  onUserUpdate?: (user: User) => void;
}

const ProfilePage: FC<ProfilePageProps> = ({
  isLoggedIn = false,
  user = null,
  userAvatar = null,
  cartItemCount = 0,
  onLogout,
  onUserUpdate,
}) => {
  const navigate = useNavigate();
  const [firstName, setFirstName] = useState(user?.firstName || '');
  const [lastName, setLastName] = useState(user?.lastName || '');
  const [username, setUsername] = useState(user?.username || '');
  const [profileError, setProfileError] = useState('');
  const [profileSuccess, setProfileSuccess] = useState('');
  const [isSavingProfile, setIsSavingProfile] = useState(false);

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [isSavingPassword, setIsSavingPassword] = useState(false);

  useEffect(() => {
    if (!isLoggedIn) {
      navigate(buildLoginPath('/profile'));
    }
  }, [isLoggedIn, navigate]);

  useEffect(() => {
    setFirstName(user?.firstName || '');
    setLastName(user?.lastName || '');
    setUsername(user?.username || '');
  }, [user]);

  const displayName = user?.firstName
    ? `${user.firstName} ${user.lastName || ''}`.trim()
    : user?.username || 'User';

  const memberSince = user?.createdAt
    ? new Date(user.createdAt).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : null;

  const handleProfileSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setProfileError('');
    setProfileSuccess('');

    if (!username.trim()) {
      setProfileError('Username is required');
      return;
    }

    setIsSavingProfile(true);
    try {
      const response = await authApi.updateUser({
        firstName: firstName.trim() || undefined,
        lastName: lastName.trim() || undefined,
        username: username.trim(),
      });
      onUserUpdate?.(response.user);
      setProfileSuccess('Profile updated successfully');
      logger.application.info('Profile updated', {
        userId: response.user.id,
        component: 'ProfilePage',
      });
    } catch (err) {
      logger.error.log(err instanceof Error ? err : 'Failed to update profile', {
        component: 'ProfilePage',
      });
      if (err instanceof ApiError) {
        if (err.status === 401) {
          navigate(buildLoginPath('/profile'));
          return;
        }
        setProfileError(err.message || 'Failed to update profile');
      } else {
        setProfileError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsSavingProfile(false);
    }
  };

  const handlePasswordSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');

    if (!currentPassword || !newPassword) {
      setPasswordError('Please fill in all password fields');
      return;
    }
    if (newPassword.length < 8) {
      setPasswordError('New password must be at least 8 characters');
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match');
      return;
    }

    setIsSavingPassword(true);
    try {
      await authApi.changePassword(currentPassword, newPassword);
      setPasswordSuccess('Password changed successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      logger.application.info('Password changed', { component: 'ProfilePage' });
    } catch (err) {
      logger.error.log(err instanceof Error ? err : 'Failed to change password', {
        component: 'ProfilePage',
      });
      if (err instanceof ApiError) {
        if (err.status === 401) {
          navigate(buildLoginPath('/profile'));
          return;
        }
        setPasswordError(err.message || 'Failed to change password');
      } else {
        setPasswordError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsSavingPassword(false);
    }
  };

  if (!isLoggedIn || !user) {
    return null;
  }

  return (
    <div className="profile-page" data-testid="ProfilePage">
      <NavBar
        cartItemCount={cartItemCount}
        isLoggedIn={isLoggedIn}
        user={user}
        userAvatar={userAvatar}
        onLogout={onLogout}
      />
      <main className="profile-page__main">
        <div className="profile-page__container">
          <header className="profile-page__header">
            <h1>My Profile</h1>
            <p>Manage your account details and security</p>
          </header>

          <section className="profile-summary">
            <div className="profile-summary__avatar">
              {userAvatar ? (
                <img src={userAvatar} alt={`${displayName}'s avatar`} />
              ) : (
                <span>
                  {(user.firstName || user.username || 'U').charAt(0).toUpperCase()}
                </span>
              )}
            </div>
            <div className="profile-summary__info">
              <h2>{displayName}</h2>
              <p className="profile-summary__email">{user.email}</p>
              <div className="profile-summary__meta">
                {user.role && (
                  <span className="profile-badge">{user.role}</span>
                )}
                {memberSince && (
                  <span className="profile-summary__joined">
                    Member since {memberSince}
                  </span>
                )}
              </div>
            </div>
            <Link to="/orders" className="profile-summary__orders-link">
              View My Orders
            </Link>
          </section>

          <div className="profile-panels">
            <section className="profile-panel">
              <h3>Account Details</h3>
              <form onSubmit={handleProfileSubmit} className="profile-form">
                {profileError && (
                  <div className="profile-form__message profile-form__message--error">
                    {profileError}
                  </div>
                )}
                {profileSuccess && (
                  <div className="profile-form__message profile-form__message--success">
                    {profileSuccess}
                  </div>
                )}

                <div className="form-group">
                  <label htmlFor="profile-email">Email</label>
                  <input
                    id="profile-email"
                    type="email"
                    value={user.email || ''}
                    disabled
                    readOnly
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="profile-first-name">First Name</label>
                    <input
                      id="profile-first-name"
                      type="text"
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                      disabled={isSavingProfile}
                      autoComplete="given-name"
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="profile-last-name">Last Name</label>
                    <input
                      id="profile-last-name"
                      type="text"
                      value={lastName}
                      onChange={(e) => setLastName(e.target.value)}
                      disabled={isSavingProfile}
                      autoComplete="family-name"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="profile-username">Username</label>
                  <input
                    id="profile-username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    disabled={isSavingProfile}
                    autoComplete="username"
                    required
                  />
                </div>

                <button
                  type="submit"
                  className="profile-form__submit"
                  disabled={isSavingProfile}
                >
                  {isSavingProfile ? 'Saving...' : 'Save Changes'}
                </button>
              </form>
            </section>

            <section className="profile-panel">
              <h3>Change Password</h3>
              <form onSubmit={handlePasswordSubmit} className="profile-form">
                {passwordError && (
                  <div className="profile-form__message profile-form__message--error">
                    {passwordError}
                  </div>
                )}
                {passwordSuccess && (
                  <div className="profile-form__message profile-form__message--success">
                    {passwordSuccess}
                  </div>
                )}

                <div className="form-group">
                  <label htmlFor="current-password">Current Password</label>
                  <input
                    id="current-password"
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    disabled={isSavingPassword}
                    autoComplete="current-password"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="new-password">New Password</label>
                  <input
                    id="new-password"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    disabled={isSavingPassword}
                    autoComplete="new-password"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="confirm-password">Confirm New Password</label>
                  <input
                    id="confirm-password"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    disabled={isSavingPassword}
                    autoComplete="new-password"
                  />
                </div>

                <button
                  type="submit"
                  className="profile-form__submit"
                  disabled={isSavingPassword}
                >
                  {isSavingPassword ? 'Updating...' : 'Update Password'}
                </button>
              </form>
            </section>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default ProfilePage;
