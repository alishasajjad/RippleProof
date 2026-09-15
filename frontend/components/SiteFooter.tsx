import Link from "next/link";

export default function SiteFooter() {
  return (
    <footer className="rp-footer">
      <div className="rp-footer-glow" />

      <div className="rp-footer-container">
        <div className="rp-footer-main">
          {/* BRAND */}
          <div className="rp-footer-brand">
            <Link href="/" className="rp-footer-logo">
              <span className="rp-footer-logo-icon">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  aria-hidden="true"
                >
                  <path
                    d="M12 3L19 6.5V11.5C19 16.1 16.1 19.6 12 21C7.9 19.6 5 16.1 5 11.5V6.5L12 3Z"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinejoin="round"
                  />

                  <path
                    d="M9 12L11 14L15.5 9.5"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </span>

              <span>
                <strong>RippleProof</strong>
                <small>Policy Change Intelligence</small>
              </span>
            </Link>

            <p className="rp-footer-description">
              Trace business-policy changes across documents, prompts, forms
              and software behaviour, review proposed repairs and produce
              executable evidence that the organization actually follows the
              new rule.
            </p>

            <div className="rp-footer-trust-line">
              <span>
                <span className="rp-footer-status-dot" />
                System operational
              </span>

              <span>Human-in-the-loop</span>

              <span>Evidence-first</span>
            </div>
          </div>

          {/* PRODUCT */}
          <div className="rp-footer-column">
            <h4>Product</h4>

            <Link href="/custom">Analyze policy</Link>
            <Link href="/runs">Run history</Link>
            <Link href="/evaluation">Evaluation</Link>
            <Link href="/">Product overview</Link>
          </div>

          {/* CAPABILITIES */}
          <div className="rp-footer-column">
            <h4>Capabilities</h4>

            <span>Semantic impact analysis</span>
            <span>Dependency discovery</span>
            <span>Human-reviewed repairs</span>
            <span>Executable verification</span>
          </div>

          {/* TRUST */}
          <div className="rp-footer-column">
            <h4>Trust & Evidence</h4>

            <span>PostgreSQL audit trail</span>
            <span>Deterministic boundary tests</span>
            <span>SHA-256 evidence receipts</span>
            <span>Human approval workflow</span>
          </div>
        </div>

        {/* ARCHITECTURE STRIP */}
        <div className="rp-footer-architecture">
          <div className="rp-footer-architecture-label">
            <span className="rp-footer-pulse" />

            <div>
              <strong>Evidence-first architecture</strong>

              <small>
                AI interprets meaning. Deterministic software establishes proof.
              </small>
            </div>
          </div>

          <div className="rp-footer-stack">
            <span>Next.js</span>
            <span>FastAPI</span>
            <span>Groq</span>
            <span>PostgreSQL</span>
            <span>Docker</span>
          </div>
        </div>

        {/* BOTTOM */}
        <div className="rp-footer-bottom">
          <div>
            © 2026 <strong>RippleProof</strong>. All rights reserved.
          </div>

          <div className="rp-footer-bottom-center">
            Semantic policy change intelligence with executable proof.
          </div>

          <div className="rp-footer-hackathon">
            Built for
            <span>AI Builders Hackathon 2026</span>
          </div>
        </div>
      </div>
    </footer>
  );
}