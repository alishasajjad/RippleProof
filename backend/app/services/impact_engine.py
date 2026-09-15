import re
from app.schemas.contracts import Artifact, ImpactFinding, PolicyContract


class ImpactEngine:
    def analyze(self, contract: PolicyContract, artifacts: list[Artifact]) -> list[ImpactFinding]:
        findings: list[ImpactFinding] = []
        old_value = str(contract.old_rule.value)
        new_value = str(contract.new_rule.value)

        for artifact in artifacts:
            content_lower = artifact.content.lower()
            mentions_refund = 'refund' in content_lower or 'eligible' in content_lower
            contains_old = bool(re.search(rf'\b{re.escape(old_value)}\b', artifact.content))
            contains_new = bool(re.search(rf'\b{re.escape(new_value)}\b', artifact.content))
            affected = mentions_refund and (contains_old or contains_new)

            if not affected:
                status = 'unknown'
                severity = 'low'
                confidence = 0.55
                reason = 'No direct semantic dependency detected in MVP rules.'
                evidence = 'No matching threshold reference found.'
            elif contains_new and not contains_old:
                status = 'compliant'
                severity = 'low'
                confidence = 0.99
                reason = f'Artifact already reflects the new {new_value}-day policy.'
                evidence = self._extract_evidence(artifact.content, new_value)
            else:
                status = 'stale'
                severity = self._severity_for(artifact.artifact_type)
                confidence = 0.99 if contains_old else 0.85
                reason = f'Artifact still reflects the previous {old_value}-day rule.'
                evidence = self._extract_evidence(artifact.content, old_value)

            findings.append(ImpactFinding(
                artifact_id=artifact.id,
                artifact_name=artifact.name,
                affected=affected,
                severity=severity,
                confidence=confidence,
                relationship=artifact.relationship,
                evidence=evidence,
                reason=reason,
                status=status,
            ))
        return findings

    @staticmethod
    def _severity_for(artifact_type: str) -> str:
        return {
            'API': 'critical',
            'CODE': 'critical',
            'FORM': 'high',
            'CHATBOT': 'high',
            'WEBSITE': 'medium',
            'DOCUMENT': 'medium',
        }.get(artifact_type, 'medium')

    @staticmethod
    def _extract_evidence(content: str, value: str) -> str:
        for line in content.splitlines():
            if value in line:
                return line.strip()[:240]
        return content[:240]
