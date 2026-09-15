import { AlertTriangle, CheckCircle2, FileCode2, ShieldAlert } from 'lucide-react';
import type { Artifact, ImpactFinding } from '@/types';

interface Props {
  artifact?: Artifact;
  finding?: ImpactFinding;
}

export default function ImpactPanel({ artifact, finding }: Props) {
  if (!artifact || !finding) {
    return (
      <aside className="detail-panel empty-panel">
        <ShieldAlert size={28} />
        <h3>Select an artifact</h3>
        <p>Click a node in the dependency graph to inspect the exact evidence behind RippleProof&apos;s finding.</p>
      </aside>
    );
  }

  const good = finding.status === 'compliant';

  return (
    <aside className="detail-panel">
      <div className="detail-topline">
        <span className={`status-pill status-${finding.status}`}>{finding.status}</span>
        <span className={`severity-pill severity-${finding.severity}`}>{finding.severity}</span>
      </div>
      <div className="detail-title-row">
        <FileCode2 size={22} />
        <div>
          <h3>{artifact.name}</h3>
          <span>{artifact.artifact_type} · {artifact.relationship}</span>
        </div>
      </div>
      <div className="confidence-row">
        <span>Impact confidence</span>
        <strong>{Math.round(finding.confidence * 100)}%</strong>
      </div>
      <div className="confidence-track"><div style={{ width: `${finding.confidence * 100}%` }} /></div>

      <div className="detail-section">
        <label>Why this matters</label>
        <p>{finding.reason}</p>
      </div>

      <div className="detail-section">
        <label>Evidence</label>
        <pre>{finding.evidence}</pre>
        {artifact.source_path && <span className="source-path">{artifact.source_path}</span>}
      </div>

      <div className={`evidence-verdict ${good ? 'good' : 'bad'}`}>
        {good ? <CheckCircle2 size={18} /> : <AlertTriangle size={18} />}
        {good ? 'Already aligned with the new policy.' : 'Action required before this change is safe.'}
      </div>
    </aside>
  );
}
