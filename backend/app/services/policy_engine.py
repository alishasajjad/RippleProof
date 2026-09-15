import re
from app.schemas.contracts import PolicyChangeRequest, PolicyContract, PolicyRule


class PolicyEngine:
    """Deterministic MVP parser for threshold-style policies.

    LLM interpretation can be plugged in later, but the demo remains testable
    and reproducible without an external model dependency.
    """

    NUMBER_RE = re.compile(r'(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>days?|hours?|months?|years?)?', re.I)

    def parse_change(self, request: PolicyChangeRequest) -> PolicyContract:
        old_match = self.NUMBER_RE.search(request.old_text)
        new_match = self.NUMBER_RE.search(request.new_text)
        if not old_match or not new_match:
            raise ValueError('Could not extract numeric thresholds from policy text.')

        old_value = float(old_match.group('value'))
        new_value = float(new_match.group('value'))
        if old_value.is_integer():
            old_value = int(old_value)
        if new_value.is_integer():
            new_value = int(new_value)

        unit = (new_match.group('unit') or old_match.group('unit') or '').lower() or None
        boundary = sorted(set([0, max(0, new_value - 1), new_value, new_value + 1, old_value, old_value + 1]))

        return PolicyContract(
            policy_name=request.policy_name,
            subject='refund',
            attribute='purchase_age_days',
            old_rule=PolicyRule(field='purchase_age_days', operator='<=', value=old_value, unit=unit),
            new_rule=PolicyRule(field='purchase_age_days', operator='<=', value=new_value, unit=unit),
            change_type='threshold_reduction' if new_value < old_value else 'threshold_increase',
            risk_domain='financial',
            boundary_values=boundary,
        )
