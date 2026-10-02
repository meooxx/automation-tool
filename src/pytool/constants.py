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
        "match": re.compile(r"(?i)^(?:career match|careermatch)$"),
    },
    {
        "name": "Connect W Recr",
        "key": "connectWRecr",
        "order": 70,
        "match": re.compile(
            r"(?i)^(?:connect w recr|connect w/ recr|connect with recruiter)$"
        ),
    },
    {
        "name": "Recruitment events",
        "key": "recruitmentEvents",
        "order": 80,
        "match": re.compile(r"(?i)^recruitment events?$"),
    },
    {
        "name": "JOML",
        "key": "joml",
        "order": 90,
        "match": re.compile(r"(?i)^joml$"),
    },
    {
        "name": "Still time to apply",
        "key": "stillTimeToApply",
        "order": 100,
        "match": re.compile(r"(?i)^still time to apply$"),
    },
    {
        "name": "Other",
        "key": "other",
        "order": 110,
        "match": None,
    },
    {
        "name": "FOH",
        "key": "foh",
        "order": 120,
        "match": re.compile(r"(?i)^(?:foh|fall open house)$"),
    },
    {
        "name": "AppDay",
        "key": "appDay",
        "order": 130,
        "match": re.compile(r"(?i)^(?:appday|app day|application day)$"),
    },
    {
        "name": "Auto Web Form",
        "key": "autoWebForm",
        "order": 140,
        "match": re.compile(r"(?i)^(?:auto web form|web form)$"),
    },
    {
        "name": "SOH",
        "key": "soh",
        "order": 150,
        "match": re.compile(r"(?i)^(?:soh|spring open house)$"),
    },
    {
        "name": "Tell Us More",
        "key": "tellUsMore",
        "order": 160,
        "match": re.compile(r"(?i)^tell us more$"),
    },
    {
        "name": "GC Website",
        "key": "gcWebsite",
        "order": 170,
        "match": re.compile(r"(?i)^(?:gc website|georgian college website)$"),
    },
    {
        "name": "int recruitment",
        "key": "intRecruitment",
        "order": 180,
        "match": re.compile(
            r"(?i)^(?:int recruitment|intl recruitment|international recruitment)$"
        ),
    },
    {
        "name": "Blank",
        "key": "blank",
        "order": 190,
        "match": None,
    },
]
LEAD_SOURCE_CATEGORIES = CATEGORY_HEADER[6:]

# Direct: "direct from high school". Everything else on OH Applicant Type is Non-direct.
DIRECT_MATCH = re.compile(
    r"(?i)^direct from (?:high|secondary) school$"
)

# IC vs OOC from Zip (column T). Fill with official catchment FSA prefixes (e.g. "L4N").
ZIP_HEADER = ["T", "Zip", re.compile(r"(?i)^zip$")]
IC_POSTAL_PREFIXES = frozenset()

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
