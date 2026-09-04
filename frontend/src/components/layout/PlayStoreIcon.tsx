/** A small inline recreation of the Google Play triangular play-button
 * mark, used as a recognizable "available on Play Store" badge without
 * pulling in an external image asset or a brand icon pack.
 */
export function PlayStoreIcon({ size = 16, className = "" }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      className={className}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="play-store-blue" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#00d2ff" />
          <stop offset="100%" stopColor="#3a7bd5" />
        </linearGradient>
        <linearGradient id="play-store-green" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#32d180" />
          <stop offset="100%" stopColor="#1fa356" />
        </linearGradient>
        <linearGradient id="play-store-yellow" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#ffd54f" />
          <stop offset="100%" stopColor="#ffb300" />
        </linearGradient>
        <linearGradient id="play-store-red" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#ff5f6d" />
          <stop offset="100%" stopColor="#e63950" />
        </linearGradient>
      </defs>
      <path d="M4 3.5v17c0 .3.15.55.4.7l9.1-9.2-9.1-9.2c-.25.15-.4.4-.4.7z" fill="url(#play-store-blue)" />
      <path d="M16.6 12l-3.1 3.1 3.5 3.5 4.2-2.4c.5-.3.5-1.1 0-1.4L16.6 12z" fill="url(#play-store-yellow)" />
      <path d="M13.5 8.9L16.6 12l4.6-2.7c.5-.3.5-1.1 0-1.4l-4.2-2.4-3.5 3.4z" fill="url(#play-store-red)" />
      <path d="M4.4 21.2c.2.15.5.15.75 0l8.35-4.8-3.5-3.5-9.6 8.3z" fill="url(#play-store-green)" />
    </svg>
  );
}
