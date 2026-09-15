import Link from "next/link";
import { ArrowLeft, ShieldCheck } from "lucide-react";

export default function NotFound() {
  return (
    <main className="rp-error-page">
      <section className="rp-error-card">
        <div className="rp-error-icon">
          <ShieldCheck size={30} />
        </div>

        <p className="rp-eyebrow">
          404 · RIPPLEPROOF
        </p>

        <h1>Evidence path not found.</h1>

        <p>
          The page or RippleProof run you requested
          does not exist or is no longer available.
        </p>

        <Link
          href="/"
          className="rp-error-retry"
        >
          <ArrowLeft size={18} />
          Return home
        </Link>
      </section>
    </main>
  );
}