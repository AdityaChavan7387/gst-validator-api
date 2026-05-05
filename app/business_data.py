"""
Mock business data — Phase 1 MVP.
Covers multiple states, business types, and GST statuses.
Replace get_business_details() and get_filing_status() with
a licensed data provider (Masters India / Govt sandbox) in Phase 2.
"""

from datetime import date
from typing import Optional

MOCK_BUSINESSES = {
    # Maharashtra — Active Private Limited
    "27ABCDE1234F1Z5": {
        "legal_name": "ABC TRADERS PRIVATE LIMITED",
        "trade_name": "ABC TRADERS",
        "status": "Active",
        "taxpayer_type": "Regular",
        "constitution": "Private Limited Company",
        "registration_date": "2019-07-12",
        "principal_address": {
            "building": "Office No. 12",
            "street": "MG Road",
            "city": "Pune",
            "pincode": "411001",
            "state": "Maharashtra",
        },
        "last_updated": str(date.today()),
    },
    # Karnataka — Active LLP
    "29AAGCB2702H1ZY": {
        "legal_name": "BENGALURU TECH SOLUTIONS LLP",
        "trade_name": "BTS LLP",
        "status": "Active",
        "taxpayer_type": "Regular",
        "constitution": "Limited Liability Partnership",
        "registration_date": "2020-03-22",
        "principal_address": {
            "building": "4th Floor, Tower B",
            "street": "Whitefield Main Road",
            "city": "Bengaluru",
            "pincode": "560066",
            "state": "Karnataka",
        },
        "last_updated": str(date.today()),
    },
    # Delhi — Active Proprietorship
    "07AABCU9603R1ZX": {
        "legal_name": "DELHI SUPPLY COMPANY",
        "trade_name": "DSC SUPPLIES",
        "status": "Active",
        "taxpayer_type": "Regular",
        "constitution": "Proprietorship",
        "registration_date": "2018-04-01",
        "principal_address": {
            "building": "Shop No. 5, Lajpat Nagar",
            "street": "Ring Road",
            "city": "New Delhi",
            "pincode": "110024",
            "state": "Delhi",
        },
        "last_updated": str(date.today()),
    },
    # Tamil Nadu — Cancelled
    "33AADCB2230M1ZV": {
        "legal_name": "CHENNAI EXPORTS LIMITED",
        "trade_name": "CHENNAI EXPORTS",
        "status": "Cancelled",
        "taxpayer_type": "Regular",
        "constitution": "Public Limited Company",
        "registration_date": "2017-11-15",
        "cancellation_date": "2023-06-30",
        "principal_address": {
            "building": "Unit 3, Industrial Estate",
            "street": "GST Road",
            "city": "Chennai",
            "pincode": "600032",
            "state": "Tamil Nadu",
        },
        "last_updated": str(date.today()),
    },
    # Gujarat — Active Manufacturer
    "24AAACC1206D1ZN": {
        "legal_name": "GUJARAT MANUFACTURING WORKS PRIVATE LIMITED",
        "trade_name": "GMW PVT LTD",
        "status": "Active",
        "taxpayer_type": "Regular",
        "constitution": "Private Limited Company",
        "registration_date": "2016-08-20",
        "principal_address": {
            "building": "Plot 45, GIDC",
            "street": "Vatva Industrial Area",
            "city": "Ahmedabad",
            "pincode": "382445",
            "state": "Gujarat",
        },
        "last_updated": str(date.today()),
    },
    # Telangana — Active IT Company
    "36AABCT1332L1ZV": {
        "legal_name": "HYDERABAD IT SERVICES PRIVATE LIMITED",
        "trade_name": "HITS PVT LTD",
        "status": "Active",
        "taxpayer_type": "Regular",
        "constitution": "Private Limited Company",
        "registration_date": "2021-01-10",
        "principal_address": {
            "building": "Block A, Cyber Towers",
            "street": "Hitech City",
            "city": "Hyderabad",
            "pincode": "500081",
            "state": "Telangana",
        },
        "last_updated": str(date.today()),
    },
    # West Bengal — Composition Dealer
    "19AABCW1234F1ZK": {
        "legal_name": "KOLKATA RETAIL STORES",
        "trade_name": "KRS RETAIL",
        "status": "Active",
        "taxpayer_type": "Composition",
        "constitution": "Proprietorship",
        "registration_date": "2020-09-05",
        "principal_address": {
            "building": "12B, Park Street",
            "street": "Park Street",
            "city": "Kolkata",
            "pincode": "700016",
            "state": "West Bengal",
        },
        "last_updated": str(date.today()),
    },
    # Kerala — Suspended
    "32AABCK5678G1ZP": {
        "legal_name": "KERALA SPICES TRADERS",
        "trade_name": "KST SPICES",
        "status": "Suspended",
        "taxpayer_type": "Regular",
        "constitution": "Partnership Firm",
        "registration_date": "2018-02-14",
        "principal_address": {
            "building": "Near KSRTC Bus Stand",
            "street": "MG Road",
            "city": "Kochi",
            "pincode": "682016",
            "state": "Kerala",
        },
        "last_updated": str(date.today()),
    },
}

MOCK_FILINGS = {
    "27ABCDE1234F1Z5": [
        {"return_type": "GSTR-1",  "period": "March 2026",    "filing_date": "2026-04-10", "status": "Filed"},
        {"return_type": "GSTR-3B", "period": "March 2026",    "filing_date": "2026-04-20", "status": "Filed"},
        {"return_type": "GSTR-1",  "period": "February 2026", "filing_date": "2026-03-11", "status": "Filed"},
        {"return_type": "GSTR-3B", "period": "February 2026", "filing_date": "2026-03-20", "status": "Filed"},
        {"return_type": "GSTR-1",  "period": "January 2026",  "filing_date": "2026-02-10", "status": "Filed"},
        {"return_type": "GSTR-3B", "period": "January 2026",  "filing_date": "2026-02-20", "status": "Filed"},
    ],
    "29AAGCB2702H1ZY": [
        {"return_type": "GSTR-1",  "period": "March 2026",    "filing_date": "2026-04-11", "status": "Filed"},
        {"return_type": "GSTR-3B", "period": "March 2026",    "filing_date": "2026-04-22", "status": "Filed"},
        {"return_type": "GSTR-1",  "period": "February 2026", "filing_date": "2026-03-12", "status": "Filed"},
        {"return_type": "GSTR-3B", "period": "February 2026", "filing_date": None,         "status": "Not Filed"},
    ],
    "24AAACC1206D1ZN": [
        {"return_type": "GSTR-1",  "period": "March 2026",    "filing_date": "2026-04-09", "status": "Filed"},
        {"return_type": "GSTR-3B", "period": "March 2026",    "filing_date": "2026-04-19", "status": "Filed"},
    ],
    "36AABCT1332L1ZV": [
        {"return_type": "GSTR-1",  "period": "March 2026",    "filing_date": "2026-04-10", "status": "Filed"},
        {"return_type": "GSTR-3B", "period": "March 2026",    "filing_date": None,         "status": "Not Filed"},
    ],
}


def get_business_details(gstin: str) -> Optional[dict]:
    return MOCK_BUSINESSES.get(gstin.upper())


def get_filing_status(gstin: str) -> Optional[list]:
    return MOCK_FILINGS.get(gstin.upper())