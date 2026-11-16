from __future__ import annotations
import pytest
from participium.services.messaging_service import MessagingService
from participium.models.user import User
from participium.models.enums import Role
from participium.models.enums import ReportStatus

from participium.core import AuthorizationError, ValidationError
from participium.models.report import Report
from participium.models.report import ReportStatusHistory
from participium.models.message import Message

MESSAGING_SERVICE = MessagingService()
dieci_messaggi = [Message(body="Test")] * 10
un_messaggio=[Message(body="Test")]
dieci_reportStatusHistory = [ReportStatusHistory()] * 10
un_reportStatusHistory= [ReportStatusHistory()]
USER_DEFAULT=User()
USER_REPORTER=User(id=1)
OPERATOR=User(role=Role.OPERATOR)
REPORT_STANDARD=Report(reporter_id=1,reporter=USER_REPORTER)
REPORT_WITHTEN_MESSAGES=Report(reporter_id=1,reporter=USER_REPORTER,messages=dieci_messaggi)
REPORT_WITHONE_MESSAGES=Report(reporter_id=1,reporter=USER_REPORTER,messages=un_messaggio)
REPORT_WITHTEN_STATUS=Report(reporter_id=1,reporter=USER_REPORTER,status_history=dieci_reportStatusHistory)
REPORT_WITHONE_STATUS=Report(reporter_id=1,reporter=USER_REPORTER,status_history=un_reportStatusHistory)
MESSAGE=Message(body="a")

@pytest.mark.parametrize( "messagingService,report,sender,body,expectedException,expectedValue",
                          [
                          (MESSAGING_SERVICE,REPORT_STANDARD,USER_DEFAULT,"  ",AuthorizationError,None),
                          (MESSAGING_SERVICE,REPORT_STANDARD,USER_DEFAULT,"a",AuthorizationError,None),
                          (MESSAGING_SERVICE,REPORT_WITHTEN_MESSAGES,USER_DEFAULT,"   ",AuthorizationError,None),
                          (MESSAGING_SERVICE,REPORT_WITHTEN_MESSAGES,USER_DEFAULT,"a",AuthorizationError,None),
                          (MESSAGING_SERVICE,REPORT_STANDARD,OPERATOR,"",ValidationError,None),
                        (MESSAGING_SERVICE,REPORT_STANDARD,OPERATOR,"a",None,MESSAGE),
                        (MESSAGING_SERVICE,REPORT_STANDARD,USER_REPORTER,"  ",ValidationError,None),
                        (MESSAGING_SERVICE,REPORT_WITHTEN_STATUS,OPERATOR,"  ",ValidationError,None),
                        (MESSAGING_SERVICE,REPORT_WITHTEN_STATUS,USER_REPORTER,"a",None,MESSAGE),
                        (MESSAGING_SERVICE,REPORT_WITHTEN_STATUS,OPERATOR,"",ValidationError,None),
                        (MESSAGING_SERVICE,REPORT_STANDARD,USER_REPORTER,"a",ValidationError,None),
                        (MESSAGING_SERVICE,REPORT_WITHONE_STATUS,USER_REPORTER,"a",None,MESSAGE),
                        (MESSAGING_SERVICE,REPORT_WITHONE_MESSAGES,USER_REPORTER,"a",None,MESSAGE),
                          ]
)

@pytest.mark.skip(reason="Disabled.")
def test_send_message(messagingService,report: Report, sender: User,body: str,expectedException , expectedValue: Message) -> None:
    if expectedException:
        with pytest.raises(expectedException):
            messagingService.send_message(report,sender,body)
    else:
        assert messagingService.send_message(report,sender,body).body == expectedValue.body








