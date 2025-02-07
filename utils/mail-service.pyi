from typing import Any

def send_mail_service(
        subject: str,
        html_template: str,
        context: dict[str, Any],
        recipient_list: list[str]) -> None: ...
