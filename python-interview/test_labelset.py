from labelset import Labelset
import pytest
from typing import Optional


def test_create_case() -> None:
    """Can create a case."""
    labelset = Labelset()
    dp_id = "test"
    labelset.create_case(dp_id)
    case = labelset.get_case(dp_id)

    assert case
    assert case.dp_id == dp_id
    assert len(case.events) == 0


def test_annotate_case() -> None:
    """Can annotate a case."""
    labelset = Labelset()
    dp_id = "test"
    labelset.create_case(dp_id)

    labelset.annotate_case(dp_id, "user1", "td1")

    case = labelset.get_case(dp_id)

    assert case
    assert case.dp_id == dp_id
    assert len(case.events) == 1


def test_upload_prelabels() -> None:
    """Can upload prelabels."""
    labelset = Labelset()
    dp_id = "test"
    labelset.create_case(dp_id)

    labelset.annotate_case(dp_id, "prelabels", "td1")

    case = labelset.get_case(dp_id)

    assert case
    assert case.dp_id == dp_id
    assert len(case.events) == 1

def test_upload_prelabels_then_annotate() -> None:
    """Can upload prelabels then annotate."""
    labelset = Labelset()
    dp_id = "test"
    labelset.create_case(dp_id)

    labelset.annotate_case(dp_id, "prelabels", "td1")
    labelset.annotate_case(dp_id, "user1", "td2")

    case = labelset.get_case(dp_id)

    assert case
    assert case.dp_id == dp_id
    assert len(case.events) == 2

def test_annotate_then_review_pass() -> None:
    """Can annotate then review pass."""
    labelset = Labelset()
    dp_id = "test"
    labelset.create_case(dp_id)

    labelset.annotate_case(dp_id, "user1", "td1")
    labelset.sign_off_on_case(dp_id, "user1", "td2")
    labelset.review_passed(dp_id, "user1", "td2")

    case = labelset.get_case(dp_id)

    assert case
    assert case.dp_id == dp_id
    assert len(case.events) == 3


def test_no_actions() -> None:
    """The case state should be empty when there are no events."""

    labelset = Labelset()
    dp_id = "test"
    labelset.create_case(dp_id)

    case = labelset.get_case(dp_id)

    assert not case.state_by_branch


def test_annotate_creates_a_branch_with_simple_state() -> None:
    """The case state should have one branch after annotation."""
    labelset = Labelset()
    dp_id = "test"
    labelset.create_case(dp_id)

    case = labelset.get_case(dp_id)
    labelset.annotate_case(dp_id, "user1", "td1")

    assert len(case.state_by_branch.keys()) == 1


def test_annotated_branch_is_not_marked_submitted() -> None:
    """The case state should not be marked submitted if it has only been annotated."""
    labelset = Labelset()
    dp_id = "test"
    labelset.create_case(dp_id)

    case = labelset.get_case(dp_id)
    labelset.annotate_case(dp_id, "user1", "td1")

    state_ = case.state_by_branch["user1"]
    assert state_.is_submitted == False


def test_annotate_then_sign_off_on_task() -> None:
    """The case state should be marked submitted if it has been annotated and signed off."""
    labelset = Labelset()
    dp_id = "test"
    labelset.create_case(dp_id)

    labelset.annotate_case(dp_id, "user1", "td1")
    labelset.sign_off_on_case(dp_id, "user1", "td1")

    case = labelset.get_case(dp_id)
    state_ = case.state_by_branch["user1"]
    assert state_.is_submitted == True


def test_annotate_then_review_failed() -> None:
    """The case state should be marked submitted if it has been annotated and signed off."""
    labelset = Labelset()
    dp_id = "test"
    labelset.create_case(dp_id)

    labelset.annotate_case(dp_id, "user1", "td1")
    labelset.sign_off_on_case(dp_id, "user1", "td1")
    labelset.review_failed(dp_id, "user1", "td1")

    case = labelset.get_case(dp_id)
    state_ = case.state_by_branch["user1"]
    assert state_.is_submitted == True
    assert state_.needs_updates == True


def test_annotate_many_times_then_review_then_annotate() -> None:
    """Annotate 4 times (autosave) then review, latest td_id is correct."""
    labelset = Labelset()
    dp_id = "test"
    labelset.create_case(dp_id)

    for ii in range(5):
        labelset.annotate_case(dp_id, "user1", "td" + str(ii))

    case = labelset.get_case(dp_id)
    state_ = case.state_by_branch["user1"]

    assert state_.latest_td_id == "td4"

    labelset.sign_off_on_case(dp_id, "user1", state_.latest_td_id)

    labelset.review_failed(dp_id, "user1", state_.latest_td_id)

    case = labelset.get_case(dp_id)
    state_ = case.state_by_branch["user1"]

    assert state_.latest_td_id == "td4"


def test_cannot_annotate_after_signing_off() -> None:
    """Normal annotate is blocked after signing off on a task."""
    labelset = Labelset()

    dp_id = "test"
    labelset.create_case(dp_id)

    labelset.annotate_case(dp_id, "user1", "td1")

    labelset.sign_off_on_case(dp_id, "user1", "td1")

    with pytest.raises(ValueError):
        labelset.annotate_case(dp_id, "user1", "td2")

    case = labelset.get_case(dp_id)
    state_ = case.state_by_branch["user1"]

    assert state_.latest_td_id == "td1"


def test_reviewer_reviews_before_signing_off() -> None:
    """Review is attempted before annotator has signed off."""
    labelset = Labelset()

    dp_id = "test"

    labelset.create_case(dp_id)

    labelset.annotate_case(dp_id, "user1", "td1")

    with pytest.raises(ValueError):
        labelset.review_failed(dp_id, "user1", "td1")

    case = labelset.get_case(dp_id)
    state_ = case.state_by_branch["user1"]

    assert state_.latest_td_id == "td1"


def test_create_2_different_branches() -> None:
    """2 different branches have their own state."""
    labelset = Labelset()

    dp_id = "test"

    labelset.create_case(dp_id)

    labelset.annotate_case(dp_id, "user1", "td11")
    labelset.annotate_case(dp_id, "user2", "td21")

    case = labelset.get_case(dp_id)
    all_state = case.state_by_branch
    assert all_state["user1"] and all_state["user2"]


def test_create_and_review_2_different_branches() -> None:
    """2 different branches have their own state."""
    labelset = Labelset()

    dp_id = "test"

    labelset.create_case(dp_id)

    labelset.annotate_case(dp_id, "user1", "td11")
    labelset.annotate_case(dp_id, "user2", "td21")

    labelset.sign_off_on_case(dp_id, "user1", "td11")
    labelset.sign_off_on_case(dp_id, "user2", "td21")

    labelset.review_passed(dp_id, "user1", "td11")
    labelset.review_passed(dp_id, "user2", "td21")

    case = labelset.get_case(dp_id)
    all_state = case.state_by_branch
    user_1_branch = all_state["user1"]
    user_2_branch = all_state["user2"]
    assert user_1_branch.is_submitted == True
    assert user_2_branch.is_submitted == True
    assert user_1_branch.needs_updates == False
    assert user_2_branch.needs_updates == False


def test_2_branches_then_merge() -> None:
    """2 different branches that are annotated then merged."""
    labelset = Labelset()

    dp_id = "test"

    labelset.create_case(dp_id)

    labelset.annotate_case(dp_id, "user1", "td11")
    labelset.annotate_case(dp_id, "user2", "td21")

    labelset.sign_off_on_case(dp_id, "user1", "td11")
    labelset.sign_off_on_case(dp_id, "user2", "td21")

    labelset.review_passed(dp_id, "user1", "td11")
    labelset.review_passed(dp_id, "user2", "td21")

    labelset.merge_branches(dp_id, ["user1", "user2"], "merged_branch", "tdMerged")

    case = labelset.get_case(dp_id)
    all_state = case.state_by_branch
    user_1_branch = all_state["user1"]
    user_2_branch = all_state["user2"]
    merged_branch = all_state["merged_branch"]

    assert user_1_branch.is_submitted == True
    assert user_2_branch.is_submitted == True
    assert user_1_branch.needs_updates == False
    assert user_2_branch.needs_updates == False
    assert user_1_branch.is_active == False
    assert user_2_branch.is_active == False

    assert merged_branch.is_submitted == True
    assert merged_branch.latest_td_id == "tdMerged"
    assert merged_branch.is_active == True


def test_review_multiple_times() -> None:
    labelset = Labelset()
    dp_id = "test"
    labelset.create_case(dp_id)

    labelset.annotate_case(dp_id, "user1", "td1")
    labelset.sign_off_on_case(dp_id, "user1", "td1")
    labelset.review_passed(dp_id, "user1", "td1")
    labelset.review_passed(dp_id, "user1", "td1")
    labelset.review_failed(dp_id, "user1", "td1")

    case = labelset.get_case(dp_id)
    state_ = case.state_by_branch["user1"]

    assert state_.is_submitted == True
    assert state_.approved_reviews == 2
    assert state_.rejected_reviews == 1
