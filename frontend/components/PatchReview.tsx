import { Check, Code2 } from 'lucide-react';
import type { PatchProposal } from '@/types';

interface Props {
  patches: PatchProposal[];
  approved: boolean;
  onApprove: () => void;
}

export default function PatchReview({ patches, approved, onApprove }: Props) {
  return (
    <section className="section-card" id="patches">
      <div className="section-heading-row">
        <div>
          <span className="eyebrow">HUMAN-IN-THE-LOOP</span>
          <h2>Patch review</h2>
          <p>RippleProof proposes changes, but a human stays in control before verification.</p>
        </div>
        <button className={`button ${approved ? 'button-success' : 'button-primary'}`} onClick={onApprove} disabled={approved}>
          <Check size={17} /> {approved ? 'All patches approved' : `Approve ${patches.length} patches`}
        </button>
      </div>

      <div className="patch-grid">
        {patches.map((patch) => (
          <article className="patch-card" key={patch.artifact_id}>
            <div className="patch-title">
              <Code2 size={18} />
              <strong>{patch.artifact_name}</strong>
            </div>
            <p>{patch.rationale}</p>
            <pre className="diff-block">
              {patch.diff.split('\n').map((line, i) => (
                <span key={`${patch.artifact_id}-${i}`} className={line.startsWith('+') && !line.startsWith('+++') ? 'diff-add' : line.startsWith('-') && !line.startsWith('---') ? 'diff-remove' : ''}>
                  {line || ' '}\n
                </span>
              ))}
            </pre>
          </article>
        ))}
      </div>
    </section>
  );
}
