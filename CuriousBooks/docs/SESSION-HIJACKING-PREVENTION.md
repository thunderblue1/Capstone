# Session hijacking prevention (JWT)

This app uses **JWT** for authentication. “Session hijacking” here means an attacker using a **stolen** access or refresh token to act as the user.

Below is what the app already does and what you can add to reduce risk.

---

## What’s already in place

### 1. **Token revocation (blocklist)**

- Revoked tokens are stored in the `token_blocklist` table (by `jti`).
- Every protected request checks the token against this list; revoked tokens are rejected.
- **Logout** revokes the token(s) you send, so a stolen token stops working after the user logs out.

### 2. **Refresh token rotation**

- Each time the client calls `/api/auth/refresh`, the server:
  - Issues a **new** access token **and** a **new** refresh token.
  - **Revokes the previous refresh token** (adds its `jti` to the blocklist).
- So each refresh token is single-use. If an attacker steals an old refresh token, it only works until the real user refreshes once; after that it’s revoked.

### 3. **Logout revokes both tokens**

- `POST /api/auth/logout` with the access token in the header and (optionally) `refreshToken` in the body revokes both.
- The frontend is set up to send both when the user logs out, so both are invalidated in one call.

### 4. **Short-lived access tokens**

- Access tokens expire (e.g. 1 hour in config). A stolen access token only works until it expires.
- Refresh tokens are longer-lived but are single-use and revocable (see above).

### 5. **HTTPS**

- Use **HTTPS in production** so tokens are not sent in cleartext. Without it, tokens can be stolen on the network.

---

## What you can add (optional)

### 1. **Shorter access token lifetime**

- In `api/config.py`, reduce `JWT_ACCESS_TOKEN_EXPIRES` (e.g. 15–30 minutes).
- Shorter lifetime limits how long a stolen access token is useful; the client can use the refresh token to get new access tokens when needed.

### 2. **HttpOnly cookies for tokens (stronger XSS protection)**

- Today, tokens are in **localStorage**, so any XSS can read them and hijack the session.
- Storing tokens in **HttpOnly, Secure, SameSite cookies** (set by the backend) prevents JavaScript from reading them, so most XSS cannot steal the token.
- Trade-off: you need to support cookie-based auth (e.g. CORS with credentials, same-site or carefully configured cross-site cookies). The API would set cookies on login/refresh and the client would send them with `credentials: 'include'` instead of putting tokens in localStorage.

### 3. **Binding tokens to something (e.g. fingerprint)**

- Optionally bind each token to a **stable client fingerprint** (e.g. hash of User-Agent + other stable headers). On each request, recompute the fingerprint and reject if it doesn’t match the one stored in or with the token.
- Reduces use of a token from another device/browser, but can break legitimate users (e.g. browser updates, VPNs). Often used only for high-sensitivity actions if at all.

### 4. **Rate limiting and monitoring**

- You already have rate limiting on login/register.
- Optionally log or alert on many failed validations or refresh attempts from the same IP/user to detect abuse or credential stuffing.

### 5. **Secure and HttpOnly in production**

- Ensure in production:
  - All auth endpoints are served over **HTTPS**.
  - If you later move tokens to cookies, set **Secure** and **HttpOnly** and a strict **SameSite** policy.

---

## Summary

| Risk | Mitigation in place |
|------|----------------------|
| Stolen token used after logout | Revocation (blocklist); logout revokes both tokens. |
| Stolen refresh token used long-term | Refresh token rotation; old refresh token revoked on each refresh. |
| Stolen access token used long-term | Short expiry; refresh flow issues new access tokens. |
| Token sent in cleartext | Use HTTPS in production. |
| XSS stealing token from JS | Tokens in localStorage are still readable by script; for stronger protection, move to HttpOnly cookies. |

Keeping JWT is fine; the main levers for session hijacking are **revocation**, **refresh rotation**, **short-lived access tokens**, and **HTTPS**, with **HttpOnly cookies** as the next step if you want to harden against XSS.
