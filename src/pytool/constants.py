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
DIRECT_VALUES = (
    "Direct",
    "Direct from High School",
)

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
DEFAULT_IC_POSTAL_PREFIXES = tuple(sorted(IC_POSTAL_PREFIXES))


NON_EMPTY_VALUE = "__NON_EMPTY__"

DEFAULT_MAILABLE_CONDITIONS = [
    {
        "key": "exclude_deceased",
        "label": "Exclude deceased",
        "field": "deceased",
        "mode": "exclude_if_value",
        "enabled": False,
        "values": ["Yes", "Y", "True", "1"],
    },
    {
        "key": "exclude_bounced",
        "label": "Exclude bounced email",
        "field": "email_bounced",
        "mode": "exclude_if_value",
        "enabled": False,
        "values": ["Yes", "Y", "True", "1"],
    },
    {
        "key": "exclude_georgian_id",
        "label": "Exclude Georgian ID",
        "field": "georgian_id",
        "mode": "exclude_if_non_empty",
        "enabled": False,
        "values": [],
    },
    {
        "key": "require_email_opt_in",
        "label": "Require email opt in",
        "field": "email_opt_in",
        "mode": "require_value",
        "enabled": False,
        "values": ["Yes", "Y", "True", "1"],
    },
    {
        "key": "exclude_opted_out",
        "label": "Exclude opted out",
        "field": "email_opted_out",
        "mode": "exclude_if_value",
        "enabled": False,
        "values": ["Yes", "Y", "True", "1"],
    },
    {
        "key": "require_future_students_updates",
        "label": "Require future students updates",
        "field": "future_students_updates",
        "mode": "require_value",
        "enabled": False,
        "values": ["Yes", "Y", "True", "1"],
    },
]

DEFAULT_FIELD_MAPPING = {
    "joined": ["Joined"],
    "lead_source": ["Lead Source - Most Recent", "Lead Source"],
    "prospect_id": ["Prospect Id"],
    "zip": ["Zip"],
    "applicant_type": ["OH Applicant Type"],
    "georgian_id": ["Georgian ID"],
    "deceased": ["Deceased"],
    "email_bounced": ["Email Bounced"],
    "email_opt_in": ["Email Opt In"],
    "email_opted_out": ["Opted Out"],
    "future_students_updates": ["Updates for future students"],
}

DEFAULT_NURTURE_CONFIG = {
    "file_path": "",
    "report_field": "Prospect Id",
    "nurture_header": "Prospect Id",
    "enable": False,
}

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
