import re
from app.state_codes import INDIAN_STATE_CODES, VALID_STATE_CODES

# ─── GSTIN Checksum ────────────────────────────────────────────────────────────
GSTIN_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def clean_input(value: str) -> str:
    """Remove spaces, dashes, dots and uppercase — common user input mistakes."""
    return value.strip().upper().replace(" ", "").replace("-", "").replace(".", "")


def compute_gstin_checksum(gstin_14: str) -> str:
    factor = 1
    total = 0
    cp = len(GSTIN_CHARS)
    for i in range(len(gstin_14) - 1, -1, -1):
        code_point = GSTIN_CHARS.index(gstin_14[i])
        code_point *= factor
        if code_point >= cp:
            code_point = (code_point // cp) + (code_point % cp)
        total += code_point
        factor = 2 if factor == 1 else 1
    return GSTIN_CHARS[(cp - (total % cp)) % cp]


# ─── Official GST Regex Patterns (from gst.gov.in Returns API docs) ────────────
GSTIN_PATTERNS = {
    "NORMAL":     re.compile(r'^[0-9]{2}[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9A-Za-z]{1}[Zz1-9A-Ja-j]{1}[0-9a-zA-Z]{1}$'),
    "UNBODY":     re.compile(r'^[0-9]{4}[A-Z]{3}[0-9]{5}[UO]{1}[N][A-Z0-9]{1}$'),
    "GOVT_DEPT":  re.compile(r'^[0-9]{2}[a-zA-Z]{4}[0-9]{5}[a-zA-Z]{1}[0-9]{1}[Z]{1}[0-9]{1}$'),
    "NRI":        re.compile(r'^[0-9]{4}[a-zA-Z]{3}[0-9]{5}[N][R][0-9a-zA-Z]{1}$'),
    "TDS":        re.compile(r'^[0-9]{2}[a-zA-Z]{4}[a-zA-Z0-9]{1}[0-9]{4}[a-zA-Z]{1}[1-9A-Za-z]{1}[D]{1}[0-9a-zA-Z]{1}$'),
    "TCS":        re.compile(r'^[0-9]{2}[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9A-Za-z]{1}[C]{1}[0-9a-zA-Z]{1}$'),
    "OIDAR":      re.compile(r'^[9][9][0-9]{2}[a-zA-Z]{3}[0-9]{5}[O][S][0-9a-zA-Z]{1}$'),
}

GSTIN_TYPE_DESCRIPTIONS = {
    "NORMAL":    "Regular / Composition / ISD Taxpayer",
    "UNBODY":    "UN Body / Embassy",
    "GOVT_DEPT": "Government Department",
    "NRI":       "Non-Resident Indian Taxpayer",
    "TDS":       "Tax Deducted at Source (TDS) Deductor",
    "TCS":       "Tax Collected at Source (TCS) Collector",
    "OIDAR":     "Online Information Database Access and Retrieval (OIDAR)",
}


def detect_gstin_type(gstin: str) -> str | None:
    """Returns the GSTIN taxpayer type based on official GST regex patterns."""
    for gstin_type, pattern in GSTIN_PATTERNS.items():
        if pattern.match(gstin):
            return gstin_type
    return None


def validate_gstin_format(gstin: str) -> dict:
    """
    Full GSTIN validation supporting all 7 official taxpayer types
    from the gst.gov.in Returns API specification.
    """
    original_input = gstin
    gstin = clean_input(gstin)

    result = {
        "gstin": gstin,
        "original_input": original_input.strip(),
        "input_was_cleaned": original_input.strip().upper() != gstin,
        "is_valid_format": False,
        "gstin_type": None,
        "gstin_type_description": None,
        "state_code": None,
        "state": None,
        "pan": None,
        "entity_number": None,
        "checksum_valid": False,
        "errors": [],
        "fix_suggestion": None,
    }

    # Length check
    if len(gstin) != 15:
        result["errors"].append(
            f"GSTIN must be exactly 15 characters. Got {len(gstin)}."
        )
        result["fix_suggestion"] = (
            "Count your GSTIN characters. A valid example: 27ABCDE1234F1Z5 (15 chars). "
            "Check for missing or extra characters."
        )
        return result

    # Detect taxpayer type from official patterns
    gstin_type = detect_gstin_type(gstin)

    if gstin_type is None:
        result["errors"].append(
            "GSTIN does not match any valid Indian taxpayer format."
        )
        result["fix_suggestion"] = (
            "Verify the GSTIN from your GST registration certificate or "
            "the GST portal at gst.gov.in. A standard GSTIN looks like: 27ABCDE1234F1Z5"
        )
        return result

    result["gstin_type"] = gstin_type
    result["gstin_type_description"] = GSTIN_TYPE_DESCRIPTIONS[gstin_type]

    # State code (applies to NORMAL, GOVT_DEPT, TDS, TCS types)
    if gstin_type in ("NORMAL", "GOVT_DEPT", "TDS", "TCS"):
        state_code = gstin[:2]
        if state_code not in VALID_STATE_CODES:
            result["errors"].append(
                f"Invalid state code '{state_code}'. Not a recognised Indian state/UT code."
            )
            result["fix_suggestion"] = (
                f"The first 2 digits of a GSTIN represent the state code. "
                f"'{state_code}' is not a valid Indian state code. "
                f"Example: 27 = Maharashtra, 29 = Karnataka, 07 = Delhi."
            )
            return result
        result["state_code"] = state_code
        result["state"] = INDIAN_STATE_CODES[state_code]

    # PAN extraction — only for NORMAL type (chars 3–12)
    if gstin_type == "NORMAL":
        pan = gstin[2:12]
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan):
            result["errors"].append(
                f"PAN portion '{pan}' inside GSTIN is invalid."
            )
            result["fix_suggestion"] = (
                "Characters 3–12 of a normal GSTIN must be a valid PAN "
                "(5 letters + 4 digits + 1 letter). Example: ABCDE1234F"
            )
            return result
        result["pan"] = pan
        result["entity_number"] = gstin[12]

    # Checksum validation — only for NORMAL type
    if gstin_type == "NORMAL":
        try:
            expected = compute_gstin_checksum(gstin[:14])
            actual = gstin[14]
            result["is_valid_format"] = True
            if actual != expected:
                result["checksum_valid"] = False
                result["errors"].append(
                    f"Checksum character mismatch. Expected '{expected}', got '{actual}'."
                )
                result["fix_suggestion"] = (
                    "The last character of a GSTIN is a checksum digit. "
                    "This usually means the GSTIN was typed incorrectly. "
                    "Please verify from your GST registration certificate."
                )
            else:
                result["checksum_valid"] = True
        except ValueError as e:
            result["errors"].append(f"Checksum error: {str(e)}")
    else:
        # For non-NORMAL types, format match is sufficient — no checksum rule
        result["is_valid_format"] = True
        result["checksum_valid"] = True

    return result


# ─── PAN Validation ────────────────────────────────────────────────────────────
PAN_TAXPAYER_TYPES = {
    "P": "Individual",
    "C": "Company",
    "H": "Hindu Undivided Family (HUF)",
    "F": "Firm / Partnership",
    "A": "Association of Persons (AOP)",
    "T": "Trust",
    "B": "Body of Individuals (BOI)",
    "L": "Local Authority",
    "J": "Artificial Juridical Person",
    "G": "Government",
}


def validate_pan_format(pan: str) -> dict:
    pan = clean_input(pan)
    is_valid = bool(re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan))
    taxpayer_type = PAN_TAXPAYER_TYPES.get(pan[3], "Unknown") if is_valid else None

    return {
        "pan": pan,
        "is_valid_format": is_valid,
        "taxpayer_type": taxpayer_type,
        "holder_type_code": pan[3] if is_valid else None,
        "message": "PAN format is valid." if is_valid else "PAN format is invalid. Expected: 5 letters + 4 digits + 1 letter (e.g. ABCDE1234F).",
        "fix_suggestion": None if is_valid else (
            "A valid PAN has 10 characters: 5 uppercase letters, 4 digits, 1 uppercase letter. "
            "Example: ABCDE1234F. Check your PAN card or income tax portal."
        ),
    }


# ─── TAN Validation ────────────────────────────────────────────────────────────
def validate_tan_format(tan: str) -> dict:
    tan = clean_input(tan)
    is_valid = bool(re.match(r'^[A-Z]{4}[0-9]{5}[A-Z]$', tan))

    return {
        "tan": tan,
        "is_valid_format": is_valid,
        "message": "TAN format is valid." if is_valid else "TAN format is invalid. Expected: 4 letters + 5 digits + 1 letter (e.g. PUNE12345B).",
        "fix_suggestion": None if is_valid else (
            "A valid TAN has 10 characters: 4 uppercase letters, 5 digits, 1 uppercase letter. "
            "Example: PUNE12345B. Check your TAN allotment letter from the Income Tax Department."
        ),
    }