import { BadgeCheck, Copy, Fingerprint } from 'lucide-react';
import type { ProofReceipt as Receipt } from '@/types';

export default function ProofReceipt({ receipt }: { receipt: Receipt }) {
  async function copyHash() {
    await navigator.clipboard.writeText(receipt.evidence_hash);
  }

  return (
    <section className="receipt-card" id="receipt">
      <div className="receipt-heading">
        <div className="receipt-seal"><BadgeCheck size={28} /></div>
        <div>
          <span className="eyebrow">RIPPLEPROOF EVIDENCE</span>
          <h2>Policy Change Verification Receipt</h2>
          <p>{receipt.policy_name} · {receipt.change_summary}</p>
        </div>
        <span className="verified-stamp">VERIFIED</span>
      </div>

      <div className="receipt-metrics">
        <div><span>Artifacts examined</span><strong>{receipt.artifacts_examined}</strong></div>
        <div><span>Affected artifacts</span><strong>{receipt.affected_artifacts}</strong></div>
        <div><span>Approved fixes</span><strong>{receipt.approved_fixes}</strong></div>
        <div><span>Tests passed</span><strong>{receipt.tests_passed}/{receipt.verification_tests}</strong></div>
        <div><span>Policy coverage</span><strong>{receipt.policy_coverage_percent}%</strong></div>
        <div><span>Behaviour</span><strong>{receipt.behavior_verification}</strong></div>
      </div>

      <div className="hash-row">
        <Fingerprint size={18} />
        <div><span>Evidence SHA-256</span><code>{receipt.evidence_hash}</code></div>
        <button onClick={copyHash} title="Copy evidence hash"><Copy size={16} /></button>
      </div>
    </section>
  );
}
