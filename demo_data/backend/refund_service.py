def is_refund_eligible(purchase_age_days: int) -> bool:
    return purchase_age_days <= 30
