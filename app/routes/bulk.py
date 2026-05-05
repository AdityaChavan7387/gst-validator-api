from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Annotated
from app.validators import validate_gstin_format

router = APIRouter()

MAX_BULK_LIMIT = 50  # Free plan safety limit; increase for paid plans


class BulkValidateRequest(BaseModel):
    gstins: Annotated[List[str], Field(
        min_length=1,
        max_length=MAX_BULK_LIMIT,
        description="List of GSTINs to validate. Maximum 50 per request.",
        examples=[["27ABCDE1234F1Z5", "29AAAAA0000A1Z5", "07ABCDE9999F1Z2"]],
    )]


@router.post(
    "/bulk-validate",
    summary="Bulk GSTIN Validation",
    tags=["Bulk Operations"],
    response_description="Validation results for all submitted GSTINs.",
)
async def bulk_validate(payload: BulkValidateRequest):
    """
    Validates multiple GSTINs in a single API call.

    Accepts up to **50 GSTINs** per request. Returns format validity,
    checksum status, state, and PAN for each GSTIN.

    Ideal for:
    - Vendor master database cleanup
    - Bulk invoice pre-validation
    - Seller onboarding batch processing
    - Enterprise compliance audits

    **Note:** Upgrade to Pro or Business plan for higher per-request limits.
    """
    if len(payload.gstins) > MAX_BULK_LIMIT:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error_code": "BULK_LIMIT_EXCEEDED",
                "message": f"Maximum {MAX_BULK_LIMIT} GSTINs allowed per request. You submitted {len(payload.gstins)}.",
            },
        )

    results = []
    valid_count = 0
    invalid_count = 0

    for gstin in payload.gstins:
        r = validate_gstin_format(gstin)
        entry = {
            "gstin": r["gstin"],
            "is_valid": r["is_valid_format"] and r["checksum_valid"],
            "is_valid_format": r["is_valid_format"],
            "checksum_valid": r["checksum_valid"],
            "state_code": r["state_code"],
            "state": r["state"],
            "pan": r["pan"],
            "entity_number": r["entity_number"],
        }

        if r["errors"]:
            entry["error"] = r["errors"][0]

        if entry["is_valid"]:
            valid_count += 1
        else:
            invalid_count += 1

        results.append(entry)

    return {
        "success": True,
        "total": len(payload.gstins),
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "results": results,
    }