from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage


logger = logging.getLogger("rippleproof")


def email_configured() -> bool:
    return bool(
        os.getenv("SMTP_HOST")
        and os.getenv("SMTP_FROM")
    )


def send_email(
    to_email: str,
    subject: str,
    text: str,
) -> bool:

    if not email_configured():
        logger.warning(
            "SMTP is not configured."
        )
        return False


    host = os.environ["SMTP_HOST"]

    port = int(
        os.getenv(
            "SMTP_PORT",
            "587"
        )
    )


    username = os.getenv(
        "SMTP_USERNAME"
    )

    password = os.getenv(
        "SMTP_PASSWORD"
    )


    sender = os.environ["SMTP_FROM"]


    message = EmailMessage()

    message["From"] = sender
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(text)


    try:

        with smtplib.SMTP(
            host,
            port,
            timeout=12,
        ) as smtp:


            smtp.ehlo()


            if os.getenv(
                "SMTP_STARTTLS",
                "true",
            ).lower() == "true":

                smtp.starttls()
                smtp.ehlo()


            if username and password:

                smtp.login(
                    username,
                    password,
                )


            smtp.send_message(
                message
            )


        logger.info(
            "Email sent successfully to %s",
            to_email,
        )

        return True


    except Exception as e:

        logger.exception(
            "Unable to send email: %s",
            e,
        )

        return False




def send_critical_drift_alert(
    *,
    to_email: str,
    policy_name: str,
    critical_count: int,
    run_id: str,
) -> bool:


    return send_email(

        to_email=to_email,

        subject=(
            f"RippleProof critical policy drift - {policy_name}"
        ),

        text=(

            f"RippleProof detected {critical_count} "
            "critical inconsistency.\n\n"

            f"Policy: {policy_name}\n"
            f"Run ID: {run_id}\n\n"

            "Review before rollout."

        ),
    )





def send_verified_alert(
    *,
    to_email: str,
    policy_name: str,
    run_id: str,
    receipt_hash: str,
) -> bool:


    return send_email(

        to_email=to_email,

        subject=(
            f"RippleProof verification complete - {policy_name}"
        ),

        text=(

            "RippleProof verification completed.\n\n"

            f"Policy: {policy_name}\n"

            f"Run ID: {run_id}\n"

            f"Evidence SHA256: {receipt_hash}\n\n"

            "Approved policy behaviour passed verification."

        ),
    )