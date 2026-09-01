# --------------------------------------------------
# Intelligent Ticket Assignment Engine
# --------------------------------------------------

# Simulated team data.
# Later this will come from the database/backend.

TEAM_DATA = {
    "Technical Support": {
        "skills": ["Technical"],
        "available_agents": 2,
        "workload": 4,
    },
    "Billing Support": {
        "skills": ["Billing"],
        "available_agents": 3,
        "workload": 2,
    },
    "Service Support": {
        "skills": ["Service"],
        "available_agents": 2,
        "workload": 3,
    },
    "Account Support": {
        "skills": ["Account"],
        "available_agents": 2,
        "workload": 1,
    },
    "Delivery Support": {
        "skills": ["Delivery"],
        "available_agents": 3,
        "workload": 2,
    },
    "General Support": {
        "skills": ["Other"],
        "available_agents": 2,
        "workload": 1,
    },
}


# --------------------------------------------------
# Assignment Rules
# --------------------------------------------------

PRIORITY_WEIGHT = {
    "Urgent": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
}

COMPLEXITY_WEIGHT = {
    "High": 3,
    "Medium": 2,
    "Low": 1,
}


def calculate_assignment_score(
    category,
    priority,
    complexity,
    team
):
    """
    Calculate suitability score for a team.
    """

    team_info = TEAM_DATA[team]

    score = 0

    # Skill/category match
    if category in team_info["skills"]:
        score += 50

    # Priority contribution
    score += PRIORITY_WEIGHT.get(
        priority,
        1
    ) * 5

    # Complexity contribution
    score += COMPLEXITY_WEIGHT.get(
        complexity,
        1
    ) * 5

    # Availability contribution
    if team_info["available_agents"] > 0:
        score += 20

    # Lower workload is preferred
    workload = team_info["workload"]

    if workload <= 2:
        score += 15
    elif workload <= 4:
        score += 10
    else:
        score += 5

    return score


def assign_ticket(
    category,
    priority,
    complexity
):
    """
    Assign a ticket to the most suitable team.
    """

    best_team = None
    best_score = -1

    for team in TEAM_DATA:

        score = calculate_assignment_score(
            category,
            priority,
            complexity,
            team
        )

        if score > best_score:
            best_score = score
            best_team = team

    team_info = TEAM_DATA[best_team]

    if priority == "Urgent":
        reason = (
            "Urgent ticket assigned to the "
            "matching specialist team."
        )

    elif complexity == "High":
        reason = (
            "High-complexity ticket assigned "
            "to the matching specialist team."
        )

    else:
        reason = (
            "Assigned based on category match, "
            "availability and workload."
        )

    return {
        "recommended_team": best_team,
        "assignment_score": best_score,
        "available_agents": team_info[
            "available_agents"
        ],
        "current_workload": team_info[
            "workload"
        ],
        "reason": reason,
    }


# --------------------------------------------------
# Test Cases
# --------------------------------------------------

if __name__ == "__main__":

    test_tickets = [
        {
            "category": "Technical",
            "priority": "Urgent",
            "complexity": "High",
        },
        {
            "category": "Billing",
            "priority": "Medium",
            "complexity": "Low",
        },
        {
            "category": "Account",
            "priority": "High",
            "complexity": "Medium",
        },
        {
            "category": "Delivery",
            "priority": "Low",
            "complexity": "Low",
        },
        {
            "category": "Service",
            "priority": "High",
            "complexity": "High",
        },
    ]

    print("=" * 70)
    print("INTELLIGENT TICKET ASSIGNMENT ENGINE")
    print("=" * 70)

    for ticket in test_tickets:

        result = assign_ticket(
            ticket["category"],
            ticket["priority"],
            ticket["complexity"]
        )

        print("\nTicket:")
        print("Category   :", ticket["category"])
        print("Priority   :", ticket["priority"])
        print("Complexity :", ticket["complexity"])

        print("\nAssignment:")
        print(
            "Recommended Team :",
            result["recommended_team"]
        )

        print(
            "Assignment Score :",
            result["assignment_score"]
        )

        print(
            "Available Agents :",
            result["available_agents"]
        )

        print(
            "Current Workload :",
            result["current_workload"]
        )

        print(
            "Reason           :",
            result["reason"]
        )