import { CheckCircle2, FlaskConical, Play, XCircle } from 'lucide-react';
import type { VerificationReport } from '@/types';

interface Props {
  before?: VerificationReport;
  after?: VerificationReport;
  approved: boolean;
  verifying: boolean;
  onVerify: () => void;
}

function renderBool(value: unknown) {
  if (value === true) return 'Eligible';
  if (value === false) return 'Ineligible';
  return String(value);
}

export default function VerificationPanel({ before, after, approved, verifying, onVerify }: Props) {
  return (
    <section className="section-card" id="verification">
      <div className="section-heading-row">
        <div>
          <span className="eyebrow">EXECUTABLE PROOF</span>
          <h2>Behaviour verification</h2>
          <p>The LLM explains the policy. Deterministic boundary tests prove the behaviour.</p>
        </div>
        <button className="button button-primary" onClick={onVerify} disabled={!approved || verifying || Boolean(after)}>
          <Play size={17} /> {verifying ? 'Running tests…' : after ? 'Verification complete' : 'Run verification'}
        </button>
      </div>

      {before && !after && (
        <div className="before-warning">
          <XCircle size={20} />
          <div><strong>Before fix: policy drift confirmed.</strong><span>{before.failed} of {before.total} boundary tests fail against the old 30-day implementation.</span></div>
        </div>
      )}

      {after && (
        <>
          <div className={`verification-banner ${after.verified ? 'verified' : 'failed'}`}>
            <div>
              {after.verified ? <CheckCircle2 size={28} /> : <XCircle size={28} />}
              <div><strong>{after.passed}/{after.total} tests passed</strong><span>{after.verified ? 'Policy behaviour verified' : 'Verification failed'}</span></div>
            </div>
            <FlaskConical size={34} />
          </div>

          <div className="table-shell">
            <table>
              <thead><tr><th>Scenario</th><th>Expected</th><th>Actual</th><th>Result</th></tr></thead>
              <tbody>
                {after.cases.map((test) => (
                  <tr key={test.name}>
                    <td>{test.name}</td>
                    <td>{renderBool(test.expected)}</td>
                    <td>{renderBool(test.actual)}</td>
                    <td><span className={`test-result ${test.passed ? 'pass' : 'fail'}`}>{test.passed ? 'PASS' : 'FAIL'}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
}
