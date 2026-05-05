from fastapi import APIRouter, HTTPException
from app.state_codes import INDIAN_STATE_CODES

router = APIRouter()

# Zone mapping for Indian states
STATE_ZONES = {
    "01": "North", "02": "North", "03": "North", "04": "North",
    "05": "North", "06": "North", "07": "North", "08": "West",
    "09": "North", "10": "East", "11": "East", "12": "East",
    "13": "East", "14": "East", "15": "East", "16": "East",
    "17": "East", "18": "East", "19": "East", "20": "East",
    "21": "East", "22": "Central", "23": "Central", "24": "West",
    "25": "West", "26": "West", "27": "West", "28": "South",
    "29": "South", "30": "West", "31": "South", "32": "South",
    "33": "South", "34": "South", "35": "East", "36": "South",
    "37": "South", "38": "North", "97": "Other", "99": "Centre",
}


@router.get(
    "/state/{state_code}",
    summary="Get Indian State Info by GST State Code",
    tags=["Utilities"],
)
async def get_state_info(state_code: str):
    """
    Returns Indian state or UT information for a given GST state code.

    The first 2 digits of every GSTIN represent the state code.
    Use this endpoint to look up state details independently.

    Example: 27 = Maharashtra, 29 = Karnataka, 07 = Delhi
    """
    state_code = state_code.strip().zfill(2)

    if state_code not in INDIAN_STATE_CODES:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": "INVALID_STATE_CODE",
                "state_code": state_code,
                "message": f"'{state_code}' is not a valid Indian GST state code.",
                "fix_suggestion": "Valid state codes are 01 to 38, plus 97 and 99. Example: 27 for Maharashtra.",
            },
        )

    return {
        "success": True,
        "state_code": state_code,
        "state": INDIAN_STATE_CODES[state_code],
        "zone": STATE_ZONES.get(state_code, "Unknown"),
    }


@router.get(
    "/states",
    summary="List All Indian GST State Codes",
    tags=["Utilities"],
)
async def list_all_states():
    """
    Returns a complete list of all Indian state and UT codes used in GSTIN.
    Useful for building dropdowns, validating state fields, or mapping GSTINs to states.
    """
    states = [
        {
            "state_code": code,
            "state": name,
            "zone": STATE_ZONES.get(code, "Unknown"),
        }
        for code, name in sorted(INDIAN_STATE_CODES.items())
    ]
    return {
        "success": True,
        "total": len(states),
        "states": states,
    }