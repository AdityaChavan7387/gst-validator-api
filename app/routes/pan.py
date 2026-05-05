from fastapi import APIRouter, HTTPException
from app.validators import validate_pan_format

router = APIRouter()


@router.get(
    "/pan/validate/{pan}",
    summary="Validate PAN Format",
    tags=["PAN & TAN"],
    response_description="PAN format validation result.",
)
async def validate_pan(pan: str):
    """
    Validates an Indian Permanent Account Number (PAN).

    Format: 5 uppercase letters + 4 digits + 1 uppercase letter.
    Example: ABCDE1234F

    Also identifies the taxpayer category from the 4th character:
    P = Individual, C = Company, H = HUF, F = Firm, etc.
    """
    result = validate_pan_format(pan)

    if not result["is_valid_format"]:
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "pan": result["pan"],
                "is_valid_format": False,
                "error_code": "INVALID_PAN_FORMAT",
                "message": result["message"],
            },
        )

    return {
        "success": True,
        **result,
    }