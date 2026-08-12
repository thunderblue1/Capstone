import { useEffect, useState } from 'react';
import {
  getStoredRateLimitUntil,
  subscribeRateLimit,
} from '../../services/api';
import './RateLimitBanner.css';

function formatRemaining(ms: number): string {
  const totalSec = Math.max(0, Math.ceil(ms / 1000));
  const minutes = Math.floor(totalSec / 60);
  const seconds = totalSec % 60;
  if (minutes <= 0) {
    return `${seconds}s`;
  }
  return `${minutes}m ${seconds.toString().padStart(2, '0')}s`;
}

/**
 * Idempotent temporary-denial notice driven only by 429 Retry-After payloads.
 * No status polling endpoint — countdown is local until the stored expiry.
 */
export default function RateLimitBanner() {
  const [untilMs, setUntilMs] = useState<number | null>(() => getStoredRateLimitUntil());
  const [now, setNow] = useState(() => Date.now());
  const [dismissedUntil, setDismissedUntil] = useState<number | null>(null);

  useEffect(() => subscribeRateLimit((nextUntil) => {
    setUntilMs(nextUntil);
    setDismissedUntil(null);
  }), []);

  useEffect(() => {
    if (untilMs == null) return undefined;
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, [untilMs]);

  useEffect(() => {
    if (untilMs != null && untilMs <= now) {
      setUntilMs(null);
      sessionStorage.removeItem('curiousbooks_rate_limit_until');
    }
  }, [untilMs, now]);

  if (untilMs == null || untilMs <= now) {
    return null;
  }
  if (dismissedUntil === untilMs) {
    return null;
  }

  const remaining = untilMs - now;

  return (
    <div className="rate-limit-banner" role="status" aria-live="polite">
      <p className="rate-limit-banner__text">
        Too many requests. Access is temporarily limited. You can try again in{' '}
        <strong>{formatRemaining(remaining)}</strong>.
      </p>
      <button
        type="button"
        className="rate-limit-banner__dismiss"
        onClick={() => setDismissedUntil(untilMs)}
        aria-label="Dismiss notice"
      >
        Dismiss
      </button>
    </div>
  );
}
