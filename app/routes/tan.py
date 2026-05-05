from fastapi import APIRouter, HTTPException
from app.validators import validate_tan_format

router = APIRouter()


@router.get(
    "/tan/validate/{tan}",
    summary="Validate TAN Format",
    tags=["PAN & TAN"],
    response_description="TAN format validation result.",
)
async def validate_tan(tan: str):
    """
    Validates an Indian Tax Deduction and Collection Account Number (TAN).

    Format: 4 uppercase letters + 5 digits + 1 uppercase letter.
    Example: PUNE12345B

    Useful for verifying TAN details during vendor onboarding,
    payroll systems, and TDS-related compliance workflows.
    """
    result = validate_tan_format(tan)

    if not result["is_valid_format"]:
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "tan": result["tan"],
                "is_valid_format": False,
                "error_code": "INVALID_TAN_FORMAT",
                "message": result["message"],
            },
        )

    return {
        "success": True,
        **result,
    }