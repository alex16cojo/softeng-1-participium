## 1 `participium.services.auth_service.AuthService.authenticate`

Suggested test file: `test_authenticate.py`

Prototype: `authenticate(identifier: str, password: str) -> User`

| TC-ID | identifier        | password  | Expected            | Fixture                                                                          |
|:------|:------------------|:----------|:--------------------|:---------------------------------------------------------------------------------|
| TC-1  | mario.rossi       | MarioR$   | User                | Esiste l'utente 'mario.rossi', è attivo e la email è verificata.                 |
| TC-2  | m.rossi@email.com | MarioR$   | User                | Esiste l'utente con email 'm.rossi@email.com', è attivo e la email è verificata. |
| TC-3  | mario.ro          | MarioR$   | AuthenticationError |                                                                                  |
| TC-4  | ""                | MarioR$   | AuthenticationError |                                                                                  |
| TC-5  | mario.rossi       | sbagliata | AuthenticationError | Esiste l'utente 'mario.rossi', è attivo e la email è verificata.                 |
| TC-6  | mario.rossi       | ""        | AuthenticationError | Esiste l'utente 'mario.rossi', è attivo e la email è verificata.                 |
| TC-7  | paolo.bianchi     | PaoloB$   | AuthenticationError | Esiste l'utente 'paolo.bianchi', la email è verificata ma non è attivo.          |
| TC-8  | luca.verdi        | LucaV$    | AuthenticationError | Esiste l'utente 'luca.verdi', è attivo ma la email non è verificata.             |


## 2 `participium.core.utils.parse_date`

Suggested test file: `test_parse_date.py`

Prototype: `parse_date(value: str | None) -> datetime | None`

| TC-ID | value        | Expected   | Fixture |
|:------|:-------------|:-----------|:--------|
| TC-1  | "2026-04-21" | datetime   |         |
| TC-2  | "21-04-2026" | ValueError |         |
| TC-3  | "data"       | ValueError |         |
| TC-4  | None         | None       |         |
| TC-5  | ""           | None       |         |


## 3 `participium.core.status_flow.ensure_transition_allowed`

Suggested test file: `test_status_flow.py`

Prototype: `ensure_transition_allowed(current_status: ReportStatus, next_status: ReportStatus) -> bool`

Allowed transitions:
`Pending Approval -> Pending Approval | Assigned | Rejected`;
`Assigned -> Assigned | In Progress | Suspended | Resolved`;
`In Progress -> In Progress | Suspended | Resolved`;
`Suspended -> Suspended | In Progress | Resolved`;
`Rejected -> Rejected`;
`Resolved -> Resolved`.

| TC-ID | current_status   | next_status       | Expected         | Fixture |
|:------|:-----------------|:------------------|:-----------------|:--------|
| TC-1  | Pending Approval | Pending Approval  | True             |         |
| TC-2  | Pending Approval | Assigned          | True             |         |
| TC-3  | Pending Approval | In Progress       | ValidationError  |         |
| TC-4  | Pending Approval | Suspended         | ValidationError  |         |
| TC-5  | Pending Approval | Rejected          | True             |         |
| TC-6  | Pending Approval | Resolved          | ValidationError  |         |
| TC-7  | Assigned         | Pending Approval  | ValidationError  |         |
| TC-8  | Assigned         | Assigned          | True             |         |
| TC-9  | Assigned         | In Progress       | True             |         |
| TC-10 | Assigned         | Suspended         | True             |         |
| TC-11 | Assigned         | Rejected          | ValidationError  |         |
| TC-12 | Assigned         | Resolved          | True             |         |
| TC-13 | In Progress      | Pending Approval  | ValidationError  |         |
| TC-14 | In Progress      | Assigned          | ValidationError  |         |
| TC-15 | In Progress      | In Progress       | True             |         |
| TC-16 | In Progress      | Suspended         | True             |         |
| TC-17 | In Progress      | Rejected          | ValidationError  |         |
| TC-18 | In Progress      | Resolved          | True             |         |
| TC-19 | Suspended        | Pending Approval  | ValidationError  |         |
| TC-20 | Suspended        | Assigned          | ValidationError  |         |
| TC-21 | Suspended        | In Progress       | True             |         |
| TC-22 | Suspended        | Suspended         | True             |         |
| TC-23 | Suspended        | Rejected          | ValidationError  |         |
| TC-24 | Suspended        | Resolved          | True             |         |
| TC-25 | Rejected         | Pending Approval  | ValidationError  |         |
| TC-26 | Rejected         | Assigned          | ValidationError  |         |
| TC-27 | Rejected         | In Progress       | ValidationError  |         |
| TC-28 | Rejected         | Suspended         | ValidationError  |         |
| TC-29 | Rejected         | Rejected          | True             |         |
| TC-30 | Rejected         | Resolved          | ValidationError  |         |
| TC-31 | Resolved         | Pending Approval  | ValidationError  |         |
| TC-32 | Resolved         | Assigned          | ValidationError  |         |
| TC-33 | Resolved         | In Progress       | ValidationError  |         |
| TC-34 | Resolved         | Suspended         | ValidationError  |         |
| TC-35 | Resolved         | Rejected          | ValidationError  |         |
| TC-36 | Resolved         | Resolved          | True             |         |

## 4 `participium.services.report_service.ReportService.create_report`

Suggested test file: `test_create_report.py`

Prototype: `create_report(reporter: User, category_id: int | str | None, title: str | None, description: str | None, latitude: float | str | None, longitude: float | str | None, photos: list[FileStorage], is_anonymous: bool = False) -> Report`

| TC-ID | reporter | category_id  | title         | description | latitude | longitude | photos                             | is_anonymous | Expected        | Fixture                                                                                 |
|:------|:---------|:-------------|:--------------|:------------|:---------|:----------|:-----------------------------------|:-------------|:----------------|:----------------------------------------------------------------------------------------|
| TC-1  | User     | 1            | "Fuga di gas" | "abc"       | 47.1     | 7.5       | [f1, f2, f3]                       | False        | Report          | Reporter esistente, attivo e con email verificata, categoria 1 esistente e attiva.      |
| TC-2  | User     | "1"          | "Fuga di gas" | "abc"       | "47.1"   | "7.5"     | [f1]                               | True         | Report          | Reporter esistente, attivo e con email verificata, categoria 1 esistente e attiva.      |
| TC-3  | User     | ""           | "Fuga di gas" | "abc"       | 47.1     | 7.5       | [f1, f2, f3]                       | False        | ValidationError | Reporter esistente, attivo e con email verificata.                                      |
| TC-4  | User     | "categoria1" | "Fuga di gas" | "abc"       | 47.1     | 7.5       | [f1, f2, f3]                       | False        | ValidationError | Reporter esistente, attivo e con email verificata.                                      |
| TC-5  | User     | None         | "Fuga di gas" | "abc"       | 47.1     | 7.5       | [f1, f2, f3]                       | False        | ValidationError | Reporter esistente, attivo e con email verificata.                                      |
| TC-6  | User     | 2            | "Fuga di gas" | "abc"       | 47.1     | 7.5       | [f1, f2, f3]                       | False        | ValidationError | Reporter esistente, attivo e con email verificata, categoria 2 inesistente.             |
| TC-7  | User     | 3            | "Fuga di gas" | "abc"       | 47.1     | 7.5       | [f1, f2, f3]                       | False        | ValidationError | Reporter esistente, attivo e con email verificata, categoria 3 esistente ma non attiva. |
| TC-8  | User     | 1            | ""            | "abc"       | 47.1     | 7.5       | [f1, f2, f3]                       | False        | ValidationError | Reporter esistente, attivo e con email verificata, categoria 1 esistente e attiva.      |
| TC-9  | User     | 1            | None          | "abc"       | 47.1     | 7.5       | [f1, f2, f3]                       | False        | ValidationError | Reporter esistente, attivo e con email verificata, categoria 1 esistente e attiva.      |
| TC-10 | User     | 1            | "Fuga di gas" | ""          | 47.1     | 7.5       | [f1, f2, f3]                       | False        | ValidationError | Reporter esistente, attivo e con email verificata, categoria 1 esistente e attiva.      |
| TC-11 | User     | 1            | "Fuga di gas" | None        | 47.1     | 7.5       | [f1, f2, f3]                       | False        | ValidationError | Reporter esistente, attivo e con email verificata, categoria 1 esistente e attiva.      |
| TC-12 | User     | 1            | "Fuga di gas" | "abc"       | ""       | 7.5       | [f1, f2, f3]                       | False        | ValidationError | Reporter esistente, attivo e con email verificata, categoria 1 esistente e attiva.      |
| TC-13 | User     | 1            | "Fuga di gas" | "abc"       | None     | 7.5       | [f1, f2, f3]                       | False        | ValidationError | Reporter esistente, attivo e con email verificata, categoria 1 esistente e attiva.      |
| TC-14 | User     | 1            | "Fuga di gas" | "abc"       | "lat"    | 7.5       | [f1, f2, f3]                       | False        | ValidationError | Reporter esistente, attivo e con email verificata, categoria 1 esistente e attiva.      |
| TC-15 | User     | 1            | "Fuga di gas" | "abc"       | 47.1     | ""        | [f1, f2, f3]                       | False        | ValidationError | Reporter esistente, attivo e con email verificata, categoria 1 esistente e attiva.      |
| TC-16 | User     | 1            | "Fuga di gas" | "abc"       | 47.1     | None      | [f1, f2, f3]                       | False        | ValidationError | Reporter esistente, attivo e con email verificata, categoria 1 esistente e attiva.      |
| TC-17 | User     | 1            | "Fuga di gas" | "abc"       | 47.1     | "long"    | [f1, f2, f3]                       | False        | ValidationError | Reporter esistente, attivo e con email verificata, categoria 1 esistente e attiva.      |
| TC-18 | User     | 1            | "Fuga di gas" | "abc"       | 47.1     | 7.5       | []                                 | False        | ValidationError | Reporter esistente, attivo e con email verificata, categoria 1 esistente e attiva.      |
| TC-19 | User     | 1            | "Fuga di gas" | "abc"       | 47.1     | 7.5       | [file_senza_nome, file_senza_nome] | False        | ValidationError | Reporter esistente, attivo e con email verificata, categoria 1 esistente e attiva.      |
| TC-20 | User     | 1            | "Fuga di gas" | "abc"       | 47.1     | 7.5       | [f1, f2, f3, f4]                   | False        | ValidationError | Reporter esistente, attivo e con email verificata, categoria 1 esistente e attiva.      |

## 5 `participium.services.report_service.ReportService.update_status`

Suggested test file: `test_update_status.py`

Prototype: `update_status(report_id: int, operator: User, next_status_value: str, note: str | None = None) -> Report`

| TC-ID | report_id | operator | next_status_value  | note              | Expected           | Fixture                                |
| :---- | :-------- | :------- | :----------------- | :---------------- | :----------------- | :------------------------------------- |
| TC-1  | 1         | ADMIN    | "Assigned"         | None              | Success            | Report (id=1, status=PENDING_APPROVAL) |
| TC-2  | 1         | CITIZEN  | "Assigned"         | None              | AuthorizationError | Operator con role.CITIZEN              |
| TC-3  | 999       | ADMIN    | "Assigned"         | None              | NotFoundError      | Database senza report_id=999           |
| TC-4  | 1         | OPERATOR | "In Progress"      | None              | AuthorizationError | report_id non relativo all'operatore   |
| TC-5  | 1         | ADMIN    | "InvalidStatus"    | None              | ValidationError    | Valore non presente in ReportStatus    |
| TC-6  | 1         | ADMIN    | "Rejected"         | None              | ValidationError    | Nota mancante per rejection            |
| TC-7  | 1         | ADMIN    | "Rejected"         | "Foto non chiara" | Success            | Nota presente per rejection            |
| TC-8  | 1         | ADMIN    | "Pending Approval" | None              | ValidationError    | Transizione non logica                 |

## 6 `participium.services.report_service.ReportService.list_public_reports`

Suggested test file: `test_public_reports.py`

Prototype: `list_public_reports(category_id: int | None = None, status: ReportStatus | None = None, date_from: datetime | None = None, date_to: datetime | None = None, sort: str = "desc") -> list[Report]`

| TC-ID | category_id | status | date_from | date_to | sort | Expected | Fixture |
| :---- | :---------- | :----- | :-------- | :------ | :--- | :------- | :------ |
| TC-1 | -1 | PENDING_APPROVAL | Date("2025-03-21")  | Date("2026-02-15") | "asc"  | [] | elenco di report ALL_ASC = [REPORT_DATE_FROM_2017, REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED, REPORT_DATE_TO_2027] dove REPORT_BASE ha id = 1, status = PENDING_APPROVAL e data = Date("2025-03-21"), gli altri report sono differenti da quello base solo per l'attributo specificato nel nome|
| TC-2 | None | None | None | None | "asc"  | ALL_ASC  | elenco di report ALL_ASC = [REPORT_DATE_FROM_2017, REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED, REPORT_DATE_TO_2027] dove REPORT_BASE ha id = 1, status = PENDING_APPROVAL e data = Date("2025-03-21"), gli altri report sono differenti da quello base solo per l'attributo specificato nel nome |
| TC-3 | 2    | None | None | None | "asc"  | [REPORT_ID_2] | elenco di report ALL_ASC = [REPORT_DATE_FROM_2017, REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED, REPORT_DATE_TO_2027] dove REPORT_BASE ha id = 1, status = PENDING_APPROVAL e data = Date("2025-03-21"), gli altri report sono differenti da quello base solo per l'attributo specificato nel nome |
| TC-4 | 1    | ASSIGNED | None | None | "asc"  | [REPORT_STATUS_ASSIGNED] | elenco di report ALL_ASC = [REPORT_DATE_FROM_2017, REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED, REPORT_DATE_TO_2027] dove REPORT_BASE ha id = 1, status = PENDING_APPROVAL e data = Date("2025-03-21"), gli altri report sono differenti da quello base solo per l'attributo specificato nel nome |
| TC-5 | None | None | None | None | "desc"  | list(reversed(ALL_ASC)) | elenco di report ALL_ASC = [REPORT_DATE_FROM_2017, REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED, REPORT_DATE_TO_2027] dove REPORT_BASE ha id = 1, status = PENDING_APPROVAL e data = Date("2025-03-21"), gli altri report sono differenti da quello base solo per l'attributo specificato nel nome |
| TC-6 | None | None | None | None | ""  | list(reversed(ALL_ASC)) | elenco di report ALL_ASC = [REPORT_DATE_FROM_2017, REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED, REPORT_DATE_TO_2027] dove REPORT_BASE ha id = 1, status = PENDING_APPROVAL e data = Date("2025-03-21"), gli altri report sono differenti da quello base solo per l'attributo specificato nel nome |
| TC-7 | None | PENDING_APPROVAL | Date("2025-03-21") | Date("2026-02-15") | "asc"  |[REPORT_BASE, REPORT_ID_2]| elenco di report ALL_ASC = [REPORT_DATE_FROM_2017, REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED, REPORT_DATE_TO_2027] dove REPORT_BASE ha id = 1, status = PENDING_APPROVAL e data = Date("2025-03-21"), gli altri report sono differenti da quello base solo per l'attributo specificato nel nome |
| TC-8 | 1 | PENDING_APPROVAL | None | Date("2026-02-15") | "asc"  | [REPORT_DATE_FROM_2017, REPORT_BASE] |elenco di report ALL_ASC = [REPORT_DATE_FROM_2017, REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED, REPORT_DATE_TO_2027] dove REPORT_BASE ha id = 1, status = PENDING_APPROVAL e data = Date("2025-03-21"), gli altri report sono differenti da quello base solo per l'attributo specificato nel nome  |
| TC-9 | 1 | PENDING_APPROVAL | Date("2025-03-21") | None | "asc"  | [REPORT_BASE, REPORT_DATE_TO_2027] | elenco di report ALL_ASC = [REPORT_DATE_FROM_2017, REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED, REPORT_DATE_TO_2027] dove REPORT_BASE ha id = 1, status = PENDING_APPROVAL e data = Date("2025-03-21"), gli altri report sono differenti da quello base solo per l'attributo specificato nel nome |
| TC-10 | 1 | PENDING_APPROVAL | Date("2025-03-21") | Date("2020-02-15") | "asc"  | [] | elenco di report ALL_ASC = [REPORT_DATE_FROM_2017, REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED, REPORT_DATE_TO_2027] dove REPORT_BASE ha id = 1, status = PENDING_APPROVAL e data = Date("2025-03-21"), gli altri report sono differenti da quello base solo per l'attributo specificato nel nome |
| TC-11| 1 | PENDING_APPROVAL | Date("2015-03-21") | Date("2016-05-15") | "asc"  | [] | elenco di report ALL_ASC = [REPORT_DATE_FROM_2017, REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED, REPORT_DATE_TO_2027] dove REPORT_BASE ha id = 1, status = PENDING_APPROVAL e data = Date("2025-03-21"), gli altri report sono differenti da quello base solo per l'attributo specificato nel nome |  
| TC-12 | 1 | PENDING_APPROVAL | Date("2025-03-21") | Date("2025-03-21")| "asc"  | [REPORT_BASE] | elenco di report ALL_ASC = [REPORT_DATE_FROM_2017, REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED, REPORT_DATE_TO_2027] dove REPORT_BASE ha id = 1, status = PENDING_APPROVAL e data = Date("2025-03-21"), gli altri report sono differenti da quello base solo per l'attributo specificato nel nome |
| TC-13 | None | None | Date("2025-03-21") | Date("2026-02-15") | "asc"  | [REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED] | elenco di report ALL_ASC = [REPORT_DATE_FROM_2017, REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED, REPORT_DATE_TO_2027] dove REPORT_BASE ha id = 1, status = PENDING_APPROVAL e data = Date("2025-03-21"), gli altri report sono differenti da quello base solo per l'attributo specificato nel nome |
| TC-14 | None | None | Date("2025-03-21") | Date("2026-02-15") | "desc"  | [REPORT_STATUS_ASSIGNED, REPORT_ID_2, REPORT_BASE] | elenco di report ALL_ASC = [REPORT_DATE_FROM_2017, REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED, REPORT_DATE_TO_2027] dove REPORT_BASE ha id = 1, status = PENDING_APPROVAL e data = Date("2025-03-21"), gli altri report sono differenti da quello base solo per l'attributo specificato nel nome |

## 7 `participium.services.messaging_service.MessagingService.send_message`

Suggested test file: `test_send_message.py`

Prototype: `send_message(report: Report, sender: User, body: str) -> Message`

Nota: Si presuppone che il primo messaggio (report con lista di ReportStatusHistory vuota e lista di messaggi vuota) puo inviarlo solo l'operatore/admin

| TC-ID | report                                                                           | sender                                                             | body        | Expected           | Fixture                                                                                                                                                                                                                           |
|:------|:---------------------------------------------------------------------------------|:-------------------------------------------------------------------|:------------|:-------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| TC-1  | Report con lista di messaggi vuota, lista di ReportStatusHistory vuota           | User che non è admin o operatore e non è il segnalatore del report | "`  `  "    | AuthorizationError | Un istanza di report con status_history e messages vuoti e un istanza di user che non è il reporter del report ma semplicemente un istanza di default di user (CITIZEN), un istanza di messaging service                          |
| TC-2  | Report con lista di messaggi vuota, lista di ReportStatusHistory vuota           | User che non è admin o operatore e non è il segnalatore del report | "a"         | AuthorizationError | Un istanza di report con status_history e messages vuoti e un istanza di user che non è il reporter del report ma semplicemente un istanza di default di user (CITIZEN),  un istanza di messaging service                         |
| TC-3  | Report con lista di messaggi piena                                               | User che non è admin o operatore e non è il segnalatore del report | " `   `   " | AuthorizationError | Un istanza di report con status_history vuota e lista di messaggi di lunghezza 10 e un istanza di user che non è il reporter del report ma semplicemente un istanza di default di user (CITIZEN), un istanza di messaging service |
| TC-4  | Report con lista di messaggi piena                                               | User che non è admin o operatore e non è il segnalatore del report | "a"         | AuthorizationError | Un istanza di report con status_history vuota e lista di messaggi di lunghezza 10 e un istanza di user che non è il reporter del report ma semplicemente un istanza di default di user (CITIZEN), un istanza di messaging service |
| TC-5  | Report con lista di messaggi vuota, lista di ReportStatusHistory vuota           | User che è operatore                                               | "`  `  "    | ValidationError    | Un istanza di report con status_history e messages vuoti e un istanza di user che ha ruolo di operatore , un istanza di messaging service                                                                                         |
| TC-6  | Report con lista di messaggi vuota, lista di ReportStatusHistory vuota           | User che è operatore                                               | " a"        | Message            | Un istanza di report con status_history e messages vuoti e un istanza di user che ha ruolo di operatore , un istanza di messaging service                                                                                         |                                                                                                                                                                                                                         |
| TC-7  | Report con lista di messaggi vuota, lista di ReportStatusHistory vuota           | User che non è admin o operatore, è il segnalatore del report      | " `  `  "   | ValidationError    | Un istanza di report con status_history e messages vuoti e un istanza di default di user che è segnalatore del report , un istanza di messaging service                                                                           |                                                                                                                                                                                                                         |
| TC-8  | Report con lista di ReportStatusHistory piena                                    | User che è operatore                                               | " `  `  "    | ValidationError    | Un istanza di report con status_history piena (lunghezza 10) e messages vuoti , un istanza di user che ha il ruolo di operatore  , un istanza di messaging service                                                                |                                                                                                                                                                                                                         |
| TC-9  | Report con lista di ReportStatusHistory piena                                    | User che è il segnalatore del report                               | "a"         | Message            | Un istanza di report con status_history piena (lunghezza 10) e messages vuoti, un istanza di user che è il segnalatore del report , un istanza di messaging service                                                               |
| TC-10 | Report con lista di ReportStatusHistory piena                                    | User che è operatore                                               | ""          | ValidationError    | Un istanza di report con status_history piena (lunghezza 10) e messages vuoti, un istanza di user che ha il ruolo di operatore  , un istanza di messaging service                                                                 |
| TC-11 | Report con lista di ReportStatusHistory vuota e lista di messaggi vuota          | User che è il reporter del report                                  | "a"         | ValidationError    | Un istanza di report con status_history e messages vuoti , un istanza di user che ha il ruolo di reporter del report , un istanza di messaging service                                                                            |
| TC-12 | Report con lista di ReportStatusHistory piena (len==1) e lista di messaggi vuota | User che è il reporter del report                                  | "a"         | Message            | Un istanza di report con status_history piena (lunghezza 1) e messages vuoti , un istanza di user che ha il ruolo di reporter del report , un istanza di messaging service                                                        |
| TC-13 | Report con lista di ReportStatusHistory vuota e lista di messaggi piena (len==1) | User che è il reporter del report                                  | "a"         | Message            | Un istanza di report con status_history vuota e lista di messaggi piena (lunghezza 1), un istanza di user che è il reporter del report , un istanza di messaging service                                                                                         |


## 8 `participium.core.security.verify_password`

Suggested test file: `test_verify_password.py`

Prototype: `verify_password(password: str, password_hash: str) -> bool`

| TC-ID | password    | password_hash           | Expected | Fixture                           |
| :---- | :---------- | :---------------------- | :------- | :-------------------------------- |
| TC-1  | "Ciao1234?" | [Hash corretto]         | True     | Hash valido                       |
| TC-2  | "Ciao1234"  | [Hash di "Ciao1234?"]   | False    | Password quasi corretta           |
| TC-3  | "CIAO1234?" | [Hash di "Ciao1234?"]   | False    | Case sensitivity attiva           |
| TC-4  | ""          | [Hash corretto]         | False    | Password vuota                    |
| TC-5  | "Ciao1234?" | ""                      | False    | Hash vuoto                        |
| TC-6  | "Ciao1234?" | [hash formato invalido] | False    | Hash con formato non riconosciuto |
| TC-7  | " "         | [hash dello spazio " "] | True     | Password composta solo da spazi   |

## 9 `participium.services.notification_service.NotificationService.create_notification`

Suggested test file: `test_create_notification.py`

Prototype: `create_notification(user: User | None, notification_type: NotificationType, title: str, body: str, report: Report | None = None) -> Notification | None`

| TC-ID | user       | notification_type | title    | body                 | report       | Expected     | Fixture                     |
| :---- | :--------- | :---------------- | :------- | :------------------- | :----------- | :----------- | :-------------------------- |
| TC-1  | Valid User | STATUS_CHANGE     | "Update" | "Status changed"     | Valid report | Notification | Utente e report esistenti   |
| TC-2  | None       | STATUS_CHANGE     | "Update" | "Status changed"     | Valid report | None         | Report esistente            |
| TC-3  | Valid User | SYSTEM            | "Alert"  | "System maintenance" | None         | Notification | Utente esistente, no report |
| TC-4  | Valid User | MESSAGE           | ""       | "Content"            | None         | Notification | Titolo vuoto                |
| TC-5  | Valid User | STATUS_CHANGE     | "Title"  | ""                   | None         | Notification | Body vuoto                  |

## 10 `participium.services.user_service.UserService.update_profile`

Suggested test file: `test_update_profile.py`

Prototype: `update_profile(user: User, username: str | None = None, first_name: str | None = None, last_name: str | None = None, email_notifications_enabled: bool | None = None, profile_picture: FileStorage | None = None) -> User`

| TC-ID | user  | username  | first_name | last_name | email_notifications_enabled | profile_picture | Expected        | Fixture                               |
| :---- | :---- | :-------- | :--------- | :-------- | :-------------------------- | :-------------- | :-------------- | :------------------------------------ |
| TC-1  | User1 | "BigBoss" | "Mario"    | "Rossi"   | True                        | [File]          | Success         | User1 esistente, file valido          |
| TC-2  | User2 | "BigBoss" | None       | None      | None                        | None            | ValidationError | User1 ha già l'username desiderato    |
| TC-3  | User1 | None      | "Luigi"    | None      | None                        | None            | Success         | User1 esistente, nome aggiornato      |
| TC-4  | User1 | None      | None       | None      | False                       | None            | Success         | User1 esistente, notifiche aggiornate |
| TC-5  | User1 | None      | None       | None      | None                        | None            | Success         | User1 esistente, no aggiornamenti     |
