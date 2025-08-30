"""
CTMDP configuration: dependencies, enabling predicates, and outcome categorization.

This module encodes how rules depend on each other and how outcomes affect state.
It does NOT modify any JSON; it's a glue layer between GROOVE matches and simulation.
"""
from __future__ import annotations
from typing import Dict, Callable, Set, Any, List


# Outcome categories we recognize in transformer logic.
# Each rule's outcomes will be classified into one of: 'success', 'detected', 'fail', 'neutral'.
# If probabilities are missing in JSON, the simulator will distribute them uniformly.


class CTMDPState:
    """Minimal state summary for simulation.

    We keep sets of entity IDs (as parsed from GROOVE LTS labels, e.g., n13) that carry flags.
    This lets follow-up rules enable on the same entities without re-running GROOVE per step.
    """

    # Entity id space is whatever comes from GROOVE, e.g., 'n13', 'n15'.
    def __init__(self):
        # Flags that enable follow-up actions
        self.compromised_emails: Set[str] = set()      # enabled by RISK001 success
        self.elevated_users: Set[str] = set()          # enabled by RISK002 success
        self.compromised_hosts: Set[str] = set()       # enabled by RISK005 or RISK004 success
        self.stolen_hashes: Set[str] = set()           # enabled by RISK003 success
        self.alerts: int = 0                           # generic alert counter

        # Book-keeping
        self.time: float = 0.0
        self.cumulative_cost: float = 0.0
        self.events: List[Dict[str, Any]] = []         # sequence of events with timestamps


# Enabling predicates per rule. They receive (state, match_id) and return True/False.

def enable_RISK001(state: CTMDPState, match_id: str) -> bool:
    # Phishing on active email account: enabled from initial GROOVE matches.
    return True


def enable_RISK002(state: CTMDPState, match_id: str) -> bool:
    # Privilege escalation requires prior compromise of the same principal.
    return match_id in state.compromised_emails or match_id in state.elevated_users


def enable_RISK003(state: CTMDPState, match_id: str) -> bool:
    # Credential dumping requires compromised host.
    return match_id in state.compromised_hosts


def enable_RISK004(state: CTMDPState, match_id: str) -> bool:
    # Remote service exploitation: enabled from initial exposure.
    return True


def enable_RISK005(state: CTMDPState, match_id: str) -> bool:
    # Lateral movement via Pass-the-Hash requires at least one stolen hash (not necessarily same id).
    return len(state.stolen_hashes) > 0


def enable_RISK006(state: CTMDPState, match_id: str) -> bool:
    # Unauthorized script execution: assume needs some compromise foothold.
    return len(state.compromised_hosts) > 0 or len(state.elevated_users) > 0


def enable_RISK007(state: CTMDPState, match_id: str) -> bool:
    # Malicious USB: independent opportunity.
    return True


def enable_RISK008(state: CTMDPState, match_id: str) -> bool:
    # Ransomware deployment: requires compromised host.
    return len(state.compromised_hosts) > 0


def enable_RISK009(state: CTMDPState, match_id: str) -> bool:
    # DoS: independent on exposed service.
    return True


def enable_RISK010(state: CTMDPState, match_id: str) -> bool:
    # Use of trusted relationship: assume needs elevated user or credentials.
    return len(state.elevated_users) > 0 or len(state.stolen_hashes) > 0


ENABLING_PREDICATES: Dict[str, Callable[[CTMDPState, str], bool]] = {
    "RISK001": enable_RISK001,
    "RISK002": enable_RISK002,
    "RISK003": enable_RISK003,
    "RISK004": enable_RISK004,
    "RISK005": enable_RISK005,
    "RISK006": enable_RISK006,
    "RISK007": enable_RISK007,
    "RISK008": enable_RISK008,
    "RISK009": enable_RISK009,
    "RISK010": enable_RISK010,
}


# Outcome categorization using simple heuristics on GROOVE outcome labels.
# These patterns are advisory; if labels are missing we fall back to index-based guesses.

OUTCOME_SUCCESS_HINTS = [
    "entered_credentials",
    "gained_control",
    "successfully_modifies_file",
    "logged_in",
]

OUTCOME_DETECTED_HINTS = [
    "alert",
    "detected",
    "security_alert",
]

OUTCOME_FAIL_HINTS = [
    "ignored",
    "failed",
    "report",
    "closed_port",
]


def categorize_outcome_label(label: str) -> str:
    L = label.lower()
    if any(k in L for k in OUTCOME_SUCCESS_HINTS):
        return "success"
    if any(k in L for k in OUTCOME_DETECTED_HINTS):
        return "detected"
    if any(k in L for k in OUTCOME_FAIL_HINTS):
        return "fail"
    return "neutral"


def transform_state(rule_id: str, outcome_category: str, state: CTMDPState, match_id: str) -> None:
    """Apply minimal state updates to enable follow-up rules.

    This is intentionally simple and conservative; it can be extended safely without touching JSON.
    """
    if rule_id == "RISK001":
        if outcome_category == "success":
            state.compromised_emails.add(match_id)
        elif outcome_category == "detected":
            state.alerts += 1
    elif rule_id == "RISK002":
        if outcome_category == "success":
            state.elevated_users.add(match_id)
        elif outcome_category == "detected":
            state.alerts += 1
    elif rule_id in ("RISK004", "RISK005"):
        if outcome_category == "success":
            state.compromised_hosts.add(match_id)
        elif outcome_category == "detected":
            state.alerts += 1
    elif rule_id == "RISK003":
        if outcome_category == "success":
            state.stolen_hashes.add(match_id)
        elif outcome_category == "detected":
            state.alerts += 1
    elif rule_id == "RISK006":
        if outcome_category == "detected":
            state.alerts += 1
    elif rule_id in ("RISK007", "RISK008", "RISK009", "RISK010"):
        if outcome_category == "detected":
            state.alerts += 1

