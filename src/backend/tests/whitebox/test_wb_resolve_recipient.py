from __future__ import annotations


from unittest.mock import Mock

import pytest
from participium.services.messaging_service import MessagingService
from participium.models.user import User
from participium.models.report import Report
from participium.models.report import ReportStatusHistory
from participium.database   import Session
from participium.models.message import Message
from participium.models.enums import Role





pytestmark = pytest.mark.whitebox


def _user(role)->User:
    return User(role=role)

def _report(reporter,status_history)->Report:
    return Report(reporter=reporter,status_history=status_history)

@pytest.fixture
def _r1()->Report:
    status=ReportStatusHistory()
    reporter = User()
    return _report(reporter,[status])

@pytest.fixture
def _r2() -> Report:
    status1=ReportStatusHistory(changed_by=_user(Role.CITIZEN))
    status2=ReportStatusHistory(changed_by=_user(Role.OPERATOR))
    reporter = User()
    return _report(reporter,[status1,status2])



@pytest.fixture
def messaging_service_bundle() -> dict[str,object]:

    message_repository=Mock()

    service=MessagingService(message_repository=message_repository)
    return {
        "service" : service,
        "message_repository" : message_repository,
    }


@pytest.fixture
def ms1_case(messaging_service_bundle) -> dict[str,object]:
    messages=[Message()]
    messaging_service_bundle["message_repository"].list_for_report.return_value=messages
    return messaging_service_bundle

@pytest.fixture
def ms2_case(messaging_service_bundle) -> dict[str,object]:
    u1=_user(Role.CITIZEN)
    u2=_user(Role.OPERATOR)
    messages=[Message(sender=u1),Message(sender=u2)]
    messaging_service_bundle["message_repository"].list_for_report.return_value = messages
    return messaging_service_bundle








# Structural tests for MessagingService._resolve_recipient belong here.
# The current runnable smoke check is kept in test_wb_task06_smoke.py.


def test_resolve_recipient_reporter_case(ms1_case: dict[str,object],_r1:Report)->None:
    u1=_user(Role.OPERATOR)
    ms1=ms1_case["service"]

    assert ms1._resolve_recipient(_r1,u1) == _r1.reporter

def test_resolve_recipient_none_case(ms1_case: dict[str,object],_r1:Report)->None:
    u2=_user(Role.CITIZEN)
    ms1 = ms1_case["service"]

    assert ms1._resolve_recipient(_r1, u2) == None

def test_resolve_recipient_sender_case(ms2_case: dict[str,object],_r1:Report)->None:
    u2 = _user(Role.CITIZEN)
    ms2 = ms2_case["service"]
    for message in reversed(ms2_case["message_repository"].list_for_report.return_value):
        if message.sender.role==Role.OPERATOR:
            user_atteso=message.sender
            break
    assert ms2._resolve_recipient(_r1, u2) == user_atteso

def test_resolve_recipient_changed_by_case(ms1_case: dict[str,object],_r2:Report)->None:
    u2 = _user(Role.CITIZEN)
    ms1 = ms1_case["service"]
    for status in reversed(_r2.status_history):
        if status.changed_by.role==Role.OPERATOR:
            user_atteso=status.changed_by
            break
    assert ms1._resolve_recipient(_r2, u2) == user_atteso

