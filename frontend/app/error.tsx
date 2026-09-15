"use client";

import { AlertTriangle, RefreshCcw } from "lucide-react";

export default function ErrorPage({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="rp-error-page">
      <section className="rp-error-card">
        <div className="rp-error-icon">
          <AlertTriangle size={30} />
        </div>

        <p className="rp-eyebrow">
          REQUEST COULD NOT BE COMPLETED
        </p>

        <h1>RippleProof hit a temporary problem.</h1>

        <p>
          Your existing evidence has not been changed.
          The AI provider or database may be temporarily
          unavailable.
        </p>

        <button
          type="button"
          className="rp-error-retry"
          onClick={reset}
        >
          <RefreshCcw size={18} />
          Try again
        </button>
      </section>
    </main>
  );
}