from fastapi import APIRouter, HTTPException
from app.validators import validate_gstin_format
from app.business_data import get_business_details, get_filing_status
from app.risk_engine import compute_risk_score

router = APIRouter()


# ─── Validate GSTIN ────────────────────────────────────────────────────────────
@router.get(
    "/validate/{gstin}",
    summary="Validate GSTIN Format",
    tags=["GSTIN"],
)
async def validate_gstin(gstin: str):
    """
    Validates an Indian GSTIN number supporting all 7 official taxpayer types:
    Normal, UN Body, Government Department, NRI, TDS, TCS, and OIDAR.

    Returns state code, state name, PAN (for Normal type), entity number,
    GSTIN taxpayer type, and checksum result.

    Automatically cleans common input mistakes like lowercase and extra spaces.
    """
    result = validate_gstin_format(gstin)

    if not result["is_valid_format"]:
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "gstin": result["gstin"],
                "is_valid_format": False,
                "error_code": "INVALID_GSTIN_FORMAT",
                "message": result["errors"][0] if result["errors"] else "Invalid GSTIN.",
                "fix_suggestion": result.get("fix_suggestion"),
            },
        )

    if result["is_valid_format"] and not result["checksum_valid"]:
        return {
            "success": True,
            "gstin": result["gstin"],
            "input_was_cleaned": result["input_was_cleaned"],
            "is_valid_format": True,
            "checksum_valid": False,
            "gstin_type": result["gstin_type"],
            "gstin_type_description": result["gstin_type_description"],
            "state_code": result["state_code"],
            "state": result["state"],
            "pan": result["pan"],
            "entity_number": result["entity_number"],
            "message": "GSTIN structure is valid but checksum failed. Possible transcription error.",
            "fix_suggestion": result.get("fix_suggestion"),
        }

    return {
        "success": True,
        "gstin": result["gstin"],
        "input_was_cleaned": result["input_was_cleaned"],
        "is_valid_format": True,
        "checksum_valid": True,
        "gstin_type": result["gstin_type"],
        "gstin_type_description": result["gstin_type_description"],
        "state_code": result["state_code"],
        "state": result["state"],
        "pan": result["pan"],
        "entity_number": result["entity_number"],
        "message": "GSTIN is valid.",
    }


# ─── Extract PAN from GSTIN ────────────────────────────────────────────────────
@router.get(
    "/extract-pan/{gstin}",
    summary="Extract PAN from GSTIN",
    tags=["GSTIN"],
)
async def extract_pan(gstin: str):
    """
    Extracts the PAN number embedded inside a Normal taxpayer GSTIN.

    Only works for Normal/Regular/Composition/ISD GSTIN types.
    Returns PAN, taxpayer type from PAN, and the source GSTIN.
    Useful for cross-matching vendor records across GST and PAN databases.
    """
    result = validate_gstin_format(gstin)

    if not result["is_valid_format"]:
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "error_code": "INVALID_GSTIN_FORMAT",
                "message": result["errors"][0] if result["errors"] else "Invalid GSTIN.",
                "fix_suggestion": result.get("fix_suggestion"),
            },
        )

    if result["gstin_type"] != "NORMAL":
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error_code": "PAN_NOT_APPLICABLE",
                "gstin_type": result["gstin_type"],
                "message": f"PAN extraction is only available for Normal taxpayer GSTINs. This GSTIN is of type '{result['gstin_type_description']}'.",
            },
        )

    from app.validators import PAN_TAXPAYER_TYPES
    pan = result["pan"]
    taxpayer_type = PAN_TAXPAYER_TYPES.get(pan[3], "Unknown") if pan else None

    return {
        "success": True,
        "gstin": result["gstin"],
        "pan": pan,
        "pan_taxpayer_type": taxpayer_type,
        "state": result["state"],
        "message": f"PAN successfully extracted from GSTIN.",
    }


# ─── Business Details ──────────────────────────────────────────────────────────
@router.get(
    "/business/{gstin}",
    summary="Get Business Details by GSTIN",
    tags=["Business Lookup"],
)
async def get_business(gstin: str):
    """
    Returns available business registration details for a GSTIN.

    Validates the GSTIN format first, then returns legal name, trade name,
    GST status, taxpayer type, constitution, registration date, state,
    and principal address.
    """
    validation = validate_gstin_format(gstin)
    if not validation["is_valid_format"]:
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "error_code": "INVALID_GSTIN_FORMAT",
                "message": validation["errors"][0] if validation["errors"] else "Invalid GSTIN.",
                "fix_suggestion": validation.get("fix_suggestion"),
            },
        )

    business = get_business_details(gstin)
    if not business:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": "BUSINESS_NOT_FOUND",
                "gstin": validation["gstin"],
                "message": "No business details found for this GSTIN in the current dataset.",
                "fix_suggestion": "Verify the GSTIN at gst.gov.in. If correct, this GSTIN may not be in our current data coverage.",
            },
        )

    return {"success": True, "gstin": validation["gstin"], **business}


# ─── GST Return Filing Status ──────────────────────────────────────────────────
@router.get(
    "/business/{gstin}/returns",
    summary="Get GST Return Filing Status",
    tags=["Business Lookup"],
)
async def get_returns(gstin: str):
    """
    Returns GST return filing summary for a GSTIN.

    Includes return type (GSTR-1, GSTR-3B etc.), filing period,
    filing date, status, and overall compliance indicator.
    """
    validation = validate_gstin_format(gstin)
    if not validation["is_valid_format"]:
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "error_code": "INVALID_GSTIN_FORMAT",
                "message": validation["errors"][0] if validation["errors"] else "Invalid GSTIN.",
            },
        )

    filings = get_filing_status(gstin)
    if not filings:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": "FILING_DATA_NOT_FOUND",
                "gstin": validation["gstin"],
                "message": "No filing records found for this GSTIN.",
            },
        )

    recent_statuses = [f["status"].lower() for f in filings[:4]]
    if all(s == "filed" for s in recent_statuses):
        compliance_status = "Good"
    elif sum(1 for s in recent_statuses if s == "filed") >= 2:
        compliance_status = "Partial"
    else:
        compliance_status = "Poor"

    return {
        "success": True,
        "gstin": validation["gstin"],
        "filing_status": filings,
        "compliance_status": compliance_status,
        "total_records_returned": len(filings),
    }


# ─── All-in-One Info Endpoint ──────────────────────────────────────────────────
@router.get(
    "/gstin/info/{gstin}",
    summary="Full GSTIN Info — Validation + Business + Risk in One Call",
    tags=["GSTIN"],
)
async def gstin_full_info(gstin: str):
    """
    Returns everything about a GSTIN in a single API call.

    Combines:
    - GSTIN format and checksum validation
    - Business registration details
    - GST return filing status
    - Vendor risk score

    Ideal for vendor onboarding workflows where you need a complete
    picture in one request without chaining multiple API calls.
    """
    validation = validate_gstin_format(gstin)

    business = None
    filings = None
    risk = None

    if validation["is_valid_format"]:
        business = get_business_details(gstin)
        filings = get_filing_status(gstin)
        risk = compute_risk_score(
            gstin=validation["gstin"],
            is_valid_format=validation["is_valid_format"],
            checksum_valid=validation["checksum_valid"],
            business=business,
            filings=filings,
        )

    return {
        "success": True,
        "gstin": validation["gstin"],
        "validation": {
            "is_valid_format": validation["is_valid_format"],
            "checksum_valid": validation["checksum_valid"],
            "gstin_type": validation["gstin_type"],
            "gstin_type_description": validation["gstin_type_description"],
            "state_code": validation["state_code"],
            "state": validation["state"],
            "pan": validation["pan"],
            "errors": validation["errors"],
        },
        "business": business,
        "filings": filings,
        "risk": risk,
    }


# ─── Risk Score ────────────────────────────────────────────────────────────────
@router.get(
    "/risk/{gstin}",
    summary="Get Vendor Risk Score",
    tags=["Risk & Intelligence"],
)
async def get_risk_score(gstin: str):
    """
    Returns a risk score (0-100) and risk level for a GSTIN.

    Risk Levels:
    - Low (0-20): Valid GSTIN, active business, filings present.
    - Medium (21-50): Valid format but incomplete signals.
    - High (51-100): Invalid GSTIN, cancelled/suspended business, or no data.
    """
    validation = validate_gstin_format(gstin)
    business = get_business_details(gstin) if validation["is_valid_format"] else None
    filings = get_filing_status(gstin) if validation["is_valid_format"] else None

    return compute_risk_score(
        gstin=validation["gstin"],
        is_valid_format=validation["is_valid_format"],
        checksum_valid=validation["checksum_valid"],
        business=business,
        filings=filings,
    )