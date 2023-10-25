#!/usr/bin/env python3
"""Labelset class."""
import json

class Case:
    """A case is a set of events."""
    def __init__(self, case_id: str):
        self.dp_id = case_id
        self.events = []
        self.state_by_branch = {}

    def __repr__(self):
        return f"Case({self.dp_id}, {self.events})"

    def __str__(self):
        return str({"dp_id": self.dp_id, "events": self.events})


class Event:
    """An event is a tuple of (user, td_id, action)."""
    def __init__(self, user: str, td_id: str, action: str):
        self.user = user
        self.td_id = td_id
        self.action = action

    def __repr__(self):
        return f"Event({self.user}, {self.td_id}, {self.action})"

    def __str__(self):
        return str({"user": self.user, "td_id": self.td_id, "action": self.action})


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

    def annotate_case(self, dp_id:str, user:str, td:str) -> None:
        """Annotate a case."""
        case = self.get_case(dp_id)
        if not case:
            raise ValueError(f"Case with dp_id {dp_id} does not exist")

        state = case.state_by_branch.get(user, None)
        if not state:
            case.state_by_branch[user] = State(td)
        else:
            if state.is_submitted:
                raise ValueError(f"Case with dp_id {dp_id} already submitted")
            case.state_by_branch[user] = State(td)

        case.events.append(Event(user, td, "annotate"))

    def sign_off_on_case(self, dp_id:str, user:str, td:str) -> None:
        """Sign off on a case."""
        case = self.get_case(dp_id)
        if not case:
            raise ValueError(f"Case with dp_id {dp_id} does not exist")

        case.state_by_branch[user].is_submitted = True

        case.events.append(Event(user, td, "sign_off"))


    def review_passed(self, dp_id:str, user:str, td:str) -> None:
        """Case Review passed."""
        case = self.get_case(dp_id)
        if not case:
            raise ValueError(f"Case with dp_id {dp_id} does not exist")

        if case.state_by_branch[user].is_submitted is True:
            case.state_by_branch[user].approved_reviews += 1
        else:
            raise ValueError(f"Case with dp_id {dp_id} not submitted")

        case.events.append(Event(user, td, "review_passed"))

    def review_failed(self, dp_id:str, user:str, td:str) -> None:
        """Case Review failed."""
        case = self.get_case(dp_id)

        if not case:
            raise ValueError(f"Case with dp_id {dp_id} does not exist")

        if case.state_by_branch[user].is_submitted is True:
            case.state_by_branch[user].rejected_reviews += 1
            case.state_by_branch[user].needs_updates = True
        else:
            raise ValueError(f"Case with dp_id {dp_id} not submitted")

        case.events.append(Event(user, td, "review_failed"))

    def merge_branches(self, dp_id:str, users:str, merged_branch:str, td:str)-> None:
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

        case.events.append(Event(merged_branch, td, "merge_branches"))


    def get_cases(self):
        _dict = {}
        for case in self.cases:
            _dict[case] = {}
            _dict[case]["dp_id"] = self.cases[case].dp_id
            _dict[case]["events"] = []
            _dict[case]["state_by_branch"] = {}
            for event in self.cases[case].events:
                _dict[case]["events"].append(event.__dict__)
            for branch in self.cases[case].state_by_branch:
                _dict[case]["state_by_branch"][branch] = self.cases[case].state_by_branch[branch].__dict__
        return json.dumps(_dict, indent=2)

    def __repr__(self):
        return f"Labelset({self.cases})"

    def __str__(self):
        return str({"cases": self.cases})





if __name__ == "__main__":

    dp_id = "test1"
    labelset = Labelset()
    labelset.create_case(dp_id)
    labelset.annotate_case(dp_id, "user1", "td11")
    labelset.annotate_case(dp_id, "user2", "td21")

    labelset.sign_off_on_case(dp_id, "user1", "td11")
    labelset.sign_off_on_case(dp_id, "user2", "td21")

    labelset.review_passed(dp_id, "user1", "td11")
    labelset.review_failed(dp_id, "user2", "td21")

    labelset.merge_branches(dp_id, ["user1", "user2"], "merged_branch", "tdMerged")

    cases = labelset.get_cases()
    print(cases)

    cases_json = json.loads(cases)
    print(cases_json)


