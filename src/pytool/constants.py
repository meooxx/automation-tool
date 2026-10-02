import re

# Constants for filtering source data
JOINED_HEADER = ["AN", "joined", re.compile(r"(?i)^joined$")]
# match Lead Source header for filtering
LEADER_HEADER = [
    "DC",
    "Lead Source - Most Recent",
    re.compile(r"(?i)^lead\s+source.*most\s+recent$"),
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
        "aliases": {"career match", "careermatch"},
    },
    {
        "name": "Connect W Recr",
        "key": "connectWRecr",
        "order": 70,
        "aliases": {
            "connect w recr",
            "connect w/ recr",
            "connect with recruiter",
        },
    },
    {
        "name": "Recruitment events",
        "key": "recruitmentEvents",
        "order": 80,
        "aliases": {"recruitment event", "recruitment events"},
    },
    {
        "name": "JOML",
        "key": "joml",
        "order": 90,
        "aliases": {"joml"},
    },
    {
        "name": "Still time to apply",
        "key": "stillTimeToApply",
        "order": 100,
        "aliases": {"still time to apply"},
    },
    {
        "name": "Other",
        "key": "other",
        "order": 110,
        "aliases": set(),
    },
    {
        "name": "FOH",
        "key": "foh",
        "order": 120,
        "aliases": {"foh", "fall open house"},
    },
    {
        "name": "AppDay",
        "key": "appDay",
        "order": 130,
        "aliases": {"appday", "app day", "application day"},
    },
    {
        "name": "Auto Web Form",
        "key": "autoWebForm",
        "order": 140,
        "aliases": {"auto web form", "web form"},
    },
    {
        "name": "SOH",
        "key": "soh",
        "order": 150,
        "aliases": {"soh", "spring open house"},
    },
    {
        "name": "Tell Us More",
        "key": "tellUsMore",
        "order": 160,
        "aliases": {"tell us more"},
    },
    {
        "name": "GC Website",
        "key": "gcWebsite",
        "order": 170,
        "aliases": {"gc website", "georgian college website"},
    },
    {
        "name": "int recruitment",
        "key": "intRecruitment",
        "order": 180,
        "aliases": {
            "int recruitment",
            "intl recruitment",
            "international recruitment",
        },
    },
    {
        "name": "Blank",
        "key": "blank",
        "order": 190,
        "aliases": set(),
    },
]
LEAD_SOURCE_CATEGORIES = CATEGORY_HEADER[6:]

# Direct: these exact normalized values. Everything else is Non-direct.
DIRECT_VALUES = {
    "direct",
    "direct from high school",
    "direct from secondary school",
}

# IC vs OOC from Zip (column T). Provisional FSA list pending client confirmation.
ZIP_HEADER = ["T", "Zip", re.compile(r"(?i)^zip$")]
IC_POSTAL_PREFIXES = frozenset({
    "L0G", "L0K", "L0L", "L0M", "L0N",
    "L3V", "L3Z", "L4M", "L4N", "L4R",
    "L9J", "L9M", "L9R", "L9S", "L9V",
    "L9W", "L9X", "L9Y", "L9Z",
    "N0C", "N0G", "N0H", "N2Z",
    "N4K", "N4L", "N4N",
    "P0A", "P0B", "P0C", "P0E",
    "P1H", "P1L", "P1P",
})

APPLICANT_TYPE_HEADER = [
    "DJ",
    "OH Applicant Type",
    re.compile(r"(?i)\bapplicant\s+type\b"),
]
PROSPECT_ID_HEADER = ["A", "Prospect Id", re.compile(r"(?i)\bprospect\s+id\b")]
GEORGIAN_ID_HEADER = ["CR", "Georgian ID", re.compile(r"(?i)\bgeorgian\s+id\b")]
UNSUBSCRIBE_HEADERS = [
    ["AF", "Opted Out", re.compile(r"(?i)^opted out$")],
    ["AO", "Opted Out of List", re.compile(r"(?i)^opted out of list$")],
    ["AA", "Do Not Email", re.compile(r"(?i)^do not email$")],
]
