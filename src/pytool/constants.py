import re

# Constants for filtering source data
JOINED_HEADER = ["AN", "joined", re.compile(r"(?i)^joined$")]
# match Lead Source header for filtering
LEADER_HEADER = [
    "DC",
    "Lead Source - Most Recent",
    re.compile(r"(?i)^lead\s+source.*$"),
]
DEFAULT_CATEGORY_HEADER = [
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
]


# Direct: these exact normalized values. Everything else is Non-direct.
DIRECT_VALUES = {
    "direct",
    "direct from high school",
    "direct from secondary school",
}

# IC vs OOC from Zip (column T). Official "Zip begins with" prefixes from client.
ZIP_HEADER = ["T", "Zip", re.compile(r"(?i)^zip$")]
IC_POSTAL_PREFIXES = frozenset({
    "L0E", "L0K", "L0L", "L0M", "L0N",
    "L3V", "L3Z", "L4M", "L4N",
    "L9J", "L9M", "L9R", "L9S", "L9V",
    "L9X", "L9Y", "L9Z",
    "N0C", "N2Z", "N4K", "N4L",
    "P0A", "P0B", "P0C",
    "P1H", "P1L", "P1P",
})

APPLICANT_TYPE_HEADER = [
    "DJ",
    "OH Applicant Type",
    re.compile(r"(?i)\bapplicant\s+type\b"),
]
PROSPECT_ID_HEADER = ["A", "Prospect Id", re.compile(r"(?i)\bprospect\s+id\b")]
GEORGIAN_ID_HEADER = ["CR", "Georgian ID",
                      re.compile(r"(?i)\bgeorgian\s+id\b")]
DECEASED_HEADER = ["CG", "Deceased", re.compile(r"(?i)^deceased$")]
EMAIL_BOUNCED_HEADER = ["CK", "Email Bounced",
                        re.compile(r"(?i)^email\s+bounced$")]
EMAIL_OPT_IN_HEADER = ["CL", "Email Opt In",
                       re.compile(r"(?i)^email\s+opt\s+in$")]
EMAIL_OPT_OUT_HEADER = [
    "AF",
    "Opted Out",
    re.compile(r"(?i)^(email\s+opt\s+out|opted out)$"),
]
FUTURE_STUDENTS_HEADER = [
    "EN",
    "Updates for future students",
    re.compile(r"(?i)^updates\s+for\s+future\s+students$"),
]
UNSUBSCRIBE_HEADERS = [
    ["AF", "Opted Out", re.compile(r"(?i)^opted out$")],
    ["AO", "Opted Out of List", re.compile(r"(?i)^opted out of list$")],
    ["AA", "Do Not Email", re.compile(r"(?i)^do not email$")],
]
