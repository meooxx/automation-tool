import re

# Constants for filtering source data
JOINED_HEADER = ["AN", "joined", re.compile(r"(?i)joined")]
# match Lead Source header for filtering
LEADER_HEADER = [
    "DC",
    "Lead Source - Most Recent",
    re.compile(r"(?i)lead source.*most recent"),
]
# match Lead Source categories for filtering
CATEGORY_HEADER = [
    {
        "name": "Total mailable pros",
        "key": "totalMailablePros",
        "order": 1
    },
    {
        "name": "New this month pros",
        "key": "newThisMonthPros",
        "order": 10
    },
    {
        "name": "Direct IC pros",
        "key": "directICPros",
        "order": 20
    },
    {
        "name": "Direct OOC pros",
        "key": "directOOCPros",
        "order": 30
    },
    {
        "name": "Non-direct IC pros",
        "key": "nonDirectICPros",
        "order": 40
    },
    {
        "name": "Non-direct OOC pros",
        "key": "nonDirectOOCPros",
        "order": 50
    },
    {
        "name": "Career Match",
        "key": "careerMatch",
        "order": 60,
        "match": re.compile(r"(?i)career match|careermatch"),
    },
    {
        "name": "Connect W Recr",
        "key": "connectWRecr",
        "order": 70,
        "match": re.compile(r"(?i)connect w recr|connect w/ recr|connect with recruiter"),
    },
    {
        "name": "Recruitment events",
        "key": "recruitmentEvents",
        "order": 80,
        "match": re.compile(r"(?i)recruitment events|recruitment event"),
    },
    {
        "name": "JOML",
        "key": "joml",
        "order": 90,
        "match": re.compile(r"(?i)joml"),
    },
    {
        "name": "Still time to apply",
        "key": "stillTimeToApply",
        "order": 100,
        "match": re.compile(r"(?i)still time to apply"),
    },
    {
        "name": "Other",
        "key": "other",
        "order": 110,
        "match": re.compile(r"(?i)^other$"),
    },
    {
        "name": "FOH",
        "key": "foh",
        "order": 120,
        "match": re.compile(r"(?i)foh|fall open house"),
    },
    {
        "name": "AppDay",
        "key": "appDay",
        "order": 130,
        "match": re.compile(r"(?i)appday|app day|application day"),
    },
    {
        "name": "Auto Web Form",
        "key": "autoWebForm",
        "order": 140,
        "match": re.compile(r"(?i)auto web form|web form"),
    },
    {
        "name": "SOH",
        "key": "soh",
        "order": 150,
        "match": re.compile(r"(?i)soh|spring open house"),
    },
    {
        "name": "Tell Us More",
        "key": "tellUsMore",
        "order": 160,
        "match": re.compile(r"(?i)tell us more"),
    },
    {
        "name": "GC Website",
        "key": "gcWebsite",
        "order": 170,
        "match": re.compile(r"(?i)gc website|georgian college website"),
    },
    {
        "name": "int recruitment",
        "key": "intRecruitment",
        "order": 180,
        "match": re.compile(r"(?i)int recruitment|intl recruitment|international recruitment"),
    },
    {
        "name": "Blank",
        "key": "blank",
        "order": 190,
        "match": None,
    },
]
LEAD_SOURCE_CATEGORIES = CATEGORY_HEADER[6:]

# Match IC, OOC, Direct, Non-direct, and RESD headers for filtering
IC_MATCH = re.compile(r"(?i)^ic$|^icc$|in-catchment|in catchment")
OOC_MATCH = re.compile(r"(?i)^ooc$|^occ$|out-of-catchment|out of catchment")
DIRECT_MATCH = re.compile(
    r"(?i)direct from secondary school|direct from high school|^direct$"
)
NON_DIRECT_MATCH = re.compile(
    r"(?i)non-direct|non direct|nondirect|mature student|college transfer|university transfer"
)

# match RESD header for filtering
RESD_HEADER = [
    "DZ",
    "Resd Code IRx",
    re.compile(r"(?i)resd code"),
]
# match Applicant Type header for filtering
APPLICANT_TYPE_HEADER = [
    "DJ",
    "OH Applicant Type",
    re.compile(r"(?i)applicant type"),
]
