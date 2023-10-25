#!/usr/bin/env python3
"""Labelset class."""

class Case:
    """A case is a set of events."""
    def __init__(self, case_id: str):
        self.dp_id = case_id
        self.events = []
        self.state_by_branch = State

    def __repr__(self):
        return f"Case({self.dp_id}, {self.events})"

    def __str__(self):
        return str({"dp_id": self.dp_id, "events": self.events})


class State:
    """A state is a set of actions."""
    def __init__(self, td_id: str) -> None:
        self.latest_td_id = td_id
        self.is_submitted = False
        self.approved_reviews = 0
        self.rejected_reviews = 0
        self.needs_updates = False
        self.is_active = True

    def __repr__(self):
        return f"State({self.latest_td_id}, {self.is_submitted}, {self.approved_reviews}, {self.rejected_reviews}, {self.needs_updates}, {self.is_active})"

    def __str__(self):
        return str({"latest_td_id": self.latest_td_id, "is_submitted": self.is_submitted, "approved_reviews": self.approved_reviews, "rejected_reviews": self.rejected_reviews, "needs_updates": self.needs_updates, "is_active": self.is_active})


class Labelset:
    """A labelset is a set of cases."""
    def __init__(self):
        self.cases = {}

    def create_case(self, dp_id:str)-> None:
        """Create a case."""
        if dp_id in self.cases:
            raise ValueError(f"Case with case_id {dp_id} already exists")
        self.cases[dp_id] = Case(dp_id)

    def get_case(self, dp_id:str) -> Case:
        """Get a case."""
        return self.cases.get(dp_id, None)

    def annotate_case(self, dp_id:str, user:str, td:str):
        """Annotate a case."""
        case = self.get_case(dp_id)
        state = case.state_by_branch.get(user, None)

        if not state:
            case.state_by_branch[user] = State(td)
        else:
            if state.is_submitted:
                raise ValueError(f"Case with dp_id {dp_id} already submitted")
            case.state_by_branch[user] = State(td)

        if not case:
            raise ValueError(f"Case with dp_id {dp_id} does not exist")
        case.events.append((user, td))

    def sign_off_on_case(self, dp_id:str, user:str, td:str):
        """Sign off on a case."""
        case = self.get_case(dp_id)
        case.state_by_branch[user].is_submitted = True
        if not case:
            raise ValueError(f"Case with dp_id {dp_id} does not exist")
        case.events.append((user, td))


    def review_passed(self, dp_id:str, user:str, td:str):
        """Case Review passed."""
        case = self.get_case(dp_id)

        if not case:
            raise ValueError(f"Case with dp_id {dp_id} does not exist")

        if case.state_by_branch[user].is_submitted is True:
            case.state_by_branch[user].approved_reviews += 1
        else:
            raise ValueError(f"Case with dp_id {dp_id} not submitted")

        case.events.append((user, td))

    def review_failed(self, dp_id:str, user:str, td:str):
        """Case Review failed."""
        case = self.get_case(dp_id)

        if not case:
            raise ValueError(f"Case with dp_id {dp_id} does not exist")

        if case.state_by_branch[user].is_submitted is True:
            case.state_by_branch[user].rejected_reviews += 1
            case.state_by_branch[user].needs_updates = True
        else:
            raise ValueError(f"Case with dp_id {dp_id} not submitted")

        case.events.append((user, td))

    def merge_branches(self, dp_id:str, users:str, merged_branch:str, td:str):
        """Merge branches."""
        case = self.get_case(dp_id)
        if not case:
            raise ValueError(f"Case with dp_id {dp_id} does not exist")

        case.state_by_branch[merged_branch] = State(td)
        case.state_by_branch[merged_branch].is_submitted = True

        for user in users:
            case.state_by_branch[user].is_active = False
            if case.state_by_branch[user].is_submitted is False:
                case.state_by_branch[merged_branch].is_submitted = False

        case.events.append((merged_branch, td))





if __name__ == "__main__":
    case = Case("dp_1")
    print(case)

    state = State("td_1")
    print(state)


    labelset = Labelset()
    labelset.create_case("dp_1")
    labelset.annotate_case("dp_1", "user_1", "td_1")
    # labelset.annotate_case("dp_1", "user_2", "td_2")
    case = labelset.get_case("dp_1")
    print(case)

