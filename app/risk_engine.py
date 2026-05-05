"""
Risk scoring engine for GSTIN-based vendor verification.
Scores are computed from available signals:
  - Format validity
  - Checksum validity
  - Business registration status
  - Filing activity presence
"""

from typing import Optional


def compute_risk_score(
    gstin: str,
    is_valid_format: bool,
    checksum_valid: bool,
    business: Optional[dict],
    filings: Optional[list],
) -> dict:
    """
    Returns a risk assessment dict with score (0-100), level, and reasons.
    Lower score = lower risk.
    """
    score = 0
    reasons = []
    flags = []

    # Format check
    if not is_valid_format:
        score += 40
        flags.append("GSTIN format is invalid")
    else:
        reasons.append("GSTIN format is valid")

    # Checksum check
    if is_valid_format and not checksum_valid:
        score += 25
        flags.append("GSTIN checksum failed — possible data entry error or fake GSTIN")
    elif checksum_valid:
        reasons.append("GSTIN checksum is valid")

    # Business details presence
    if business is None:
        score += 20
        flags.append("No business details found for this GSTIN")
    else:
        status = business.get("status", "").lower()
        if status == "active":
            reasons.append("Business registration status is Active")
        elif status in ("cancelled", "suspended"):
            score += 30
            flags.append(f"Business registration status is '{business.get('status')}' — high risk")
        else:
            score += 10
            flags.append(f"Business status is unclear: '{business.get('status')}'")

        if business.get("taxpayer_type"):
            reasons.append(f"Taxpayer type: {business.get('taxpayer_type')}")

    # Filing activity
    if filings is None or len(filings) == 0:
        score += 15
        flags.append("No GST return filing records found — compliance unverified")
    else:
        recent = filings[0]
        if recent.get("status", "").lower() == "filed":
            reasons.append(f"Most recent return ({recent.get('return_type')} - {recent.get('period')}) was filed on time")
        else:
            score += 10
            flags.append("Most recent return filing status is not 'Filed'")

    # Cap at 100
    score = min(score, 100)

    # Risk level bands
    if score <= 20:
        level = "Low"
    elif score <= 50:
        level = "Medium"
    else:
        level = "High"

    return {
        "gstin": gstin,
        "risk_score": score,
        "risk_level": level,
        "reasons": reasons,
        "flags": flags,
        "note": "Risk score is computed from available validation signals. It is not a legal or compliance determination.",
    }