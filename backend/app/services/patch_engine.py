import difflib
from app.schemas.contracts import Artifact, ImpactFinding, PatchProposal, PolicyContract


class PatchEngine:
    def propose(self, contract: PolicyContract, artifacts: list[Artifact], findings: list[ImpactFinding]) -> list[PatchProposal]:
        by_id = {a.id: a for a in artifacts}
        proposals: list[PatchProposal] = []
        old_value = str(contract.old_rule.value)
        new_value = str(contract.new_rule.value)

        for finding in findings:
            if finding.status != 'stale':
                continue
            artifact = by_id[finding.artifact_id]
            proposed = artifact.content.replace(old_value, new_value)
            diff = '\n'.join(difflib.unified_diff(
                artifact.content.splitlines(),
                proposed.splitlines(),
                fromfile=f'{artifact.name}:before',
                tofile=f'{artifact.name}:after',
                lineterm='',
            ))
            proposals.append(PatchProposal(
                artifact_id=artifact.id,
                artifact_name=artifact.name,
                original_content=artifact.content,
                proposed_content=proposed,
                diff=diff,
                rationale=f'Align {artifact.name} with {contract.policy_name}: {old_value} → {new_value} days.',
            ))
        return proposals
