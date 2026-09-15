from app.services.demo_service import analyze_demo, verify_demo, run_demo


def test_analysis_finds_expected_drift():
    result = analyze_demo()

    assert result['contract'].old_rule.value == 30
    assert result['contract'].new_rule.value == 14
    assert len(result['artifacts']) == 5
    assert sum(f.status == 'stale' for f in result['findings']) == 4
    assert sum(f.severity == 'critical' and f.status == 'stale' for f in result['findings']) == 1
    assert result['verification_before_fix'].verified is False


def test_verification_proves_the_fix():
    result = verify_demo()

    assert result['verification_after_fix'].verified is True
    assert result['verification_after_fix'].failed == 0
    assert result['receipt'].behavior_verification == 'PASSED'
    assert result['receipt'].approved_fixes == 4


def test_full_demo_is_backwards_compatible():
    result = run_demo()

    assert result['receipt'].artifacts_examined == 5
    assert result['receipt'].confirmed_inconsistencies == 4
    assert result['receipt'].critical_inconsistencies == 1
