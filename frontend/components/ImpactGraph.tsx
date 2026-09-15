'use client';

import { Background, Controls, Edge, MarkerType, Node, ReactFlow } from '@xyflow/react';
import type { Artifact, ImpactFinding, PolicyContract } from '@/types';

interface Props {
  contract: PolicyContract;
  artifacts: Artifact[];
  findings: ImpactFinding[];
  onSelect: (artifactId: string) => void;
}

const positions: Record<string, { x: number; y: number }> = {
  'policy-doc': { x: 40, y: 50 },
  faq: { x: 40, y: 210 },
  bot: { x: 580, y: 50 },
  form: { x: 580, y: 210 },
  api: { x: 310, y: 340 },
};

function nodeClass(status: string, severity: string) {
  if (status === 'compliant') return 'graph-node graph-node-good';
  if (severity === 'critical') return 'graph-node graph-node-critical';
  if (status === 'stale') return 'graph-node graph-node-stale';
  return 'graph-node';
}

export default function ImpactGraph({ contract, artifacts, findings, onSelect }: Props) {
  const findingMap = new Map(findings.map((f) => [f.artifact_id, f]));

  const nodes: Node[] = [
    {
      id: 'policy',
      position: { x: 310, y: 160 },
      data: {
        label: (
          <div className="graph-policy-content">
            <small>POLICY CHANGE</small>
            <strong>{contract.old_rule.value} → {contract.new_rule.value} days</strong>
            <span>{contract.policy_name}</span>
          </div>
        ),
      },
      className: 'graph-node graph-policy',
    },
    ...artifacts.map((artifact) => {
      const finding = findingMap.get(artifact.id)!;
      return {
        id: artifact.id,
        position: positions[artifact.id] ?? { x: 0, y: 0 },
        data: {
          label: (
            <div className="graph-artifact-content">
              <small>{artifact.artifact_type}</small>
              <strong>{artifact.name}</strong>
              <span>{finding.status === 'stale' ? 'Mismatch detected' : finding.status === 'compliant' ? 'Up to date' : 'Review'}</span>
            </div>
          ),
        },
        className: nodeClass(finding.status, finding.severity),
      } satisfies Node;
    }),
  ];

  const edges: Edge[] = artifacts.map((artifact) => {
    const finding = findingMap.get(artifact.id)!;
    return {
      id: `policy-${artifact.id}`,
      source: 'policy',
      target: artifact.id,
      animated: finding.status === 'stale',
      markerEnd: { type: MarkerType.ArrowClosed },
      style: {
        stroke: finding.status === 'compliant' ? '#31c48d' : finding.severity === 'critical' ? '#ff5572' : '#d6a93d',
        strokeWidth: finding.severity === 'critical' ? 2.4 : 1.5,
      },
    };
  });

  return (
    <div className="graph-shell">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        minZoom={0.65}
        maxZoom={1.35}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable
        onNodeClick={(_, node) => {
          if (node.id !== 'policy') onSelect(node.id);
        }}
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={26} size={1} color="#263147" />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
