"""
Background Bulk Email Sending Engine
=====================================
Runs email campaigns in a dedicated daemon thread.
Supports pause / resume / stop with in-memory signal Events.
All database writes use an isolated per-thread session.
"""
import threading
import time
import random
import smtplib
import logging
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from typing import Optional, Callable
import uuid

from app.db.database import SessionLocal
from app.models.campaign import Campaign, CampaignStatus
from app.models.contact import Contact
from app.models.email_log import EmailLog
from app.models.smtp_profile import SMTPProfile
from app.services.template_renderer import TemplateRenderer
from app.core.security import decrypt_secret

logger = logging.getLogger(__name__)


def _create_notification(db, campaign, notif_type: str, title: str, message: str):
    """Create a notification for the campaign owner"""
    try:
        from app.models.notification import Notification
        if not campaign.user_id:
            return
        notif = Notification(
            user_id=campaign.user_id,
            type=notif_type,
            title=title,
            message=message,
            campaign_id=campaign.id,
            is_read=False
        )
        db.add(notif)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to create notification: {e}") 


# ---------------------------------------------------------------------------
# Per-campaign runtime state container
# ---------------------------------------------------------------------------

class _CampaignState:
    """Holds runtime control objects for one running campaign."""

    def __init__(self, campaign_id: int):
        self.campaign_id = campaign_id
        # pause_event: SET = running, CLEAR = paused
        self.pause_event = threading.Event()
        self.pause_event.set()  # start in running state
        # stop_event: SET = stop requested
        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None
        self.status: str = "starting"  # "running" | "paused" | "stopped" | "completed"

    def is_alive(self) -> bool:
        return self.thread is not None and self.thread.is_alive()


# ---------------------------------------------------------------------------
# SMTP helpers (synchronous — safe inside a worker thread)
# ---------------------------------------------------------------------------

def _get_active_smtp_profile(db) -> Optional[SMTPProfile]:
    return db.query(SMTPProfile).filter(SMTPProfile.is_active == True).first()


def _build_message(profile: SMTPProfile, to_email: str, subject: str,
                   html_body: str, text_body: str, tracking_id: str = None) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{profile.sender_name} <{profile.sender_email}>"
    msg["To"] = to_email
    msg["Reply-To"] = profile.sender_email
    msg["Message-ID"] = f"<{tracking_id or uuid.uuid4()}@carlyshayn.com>"
    msg["Date"] = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    msg["MIME-Version"] = "1.0"
    msg.attach(MIMEText(text_body or "Please enable HTML to view this email.", "plain"))
    msg.attach(MIMEText(html_body, "html"))
    return msg


def _send_via_smtplib(profile: SMTPProfile, msg: MIMEMultipart,
                      to_email: str, max_retries: int = 3) -> bool:
    """Send a single message using synchronous smtplib with retry logic."""
    password = decrypt_secret(profile.password)
    use_ssl = profile.tls_enabled and profile.smtp_port == 465
    use_starttls = profile.tls_enabled and not use_ssl

    for attempt in range(max_retries):
        try:
            if use_ssl:
                ctx = ssl.create_default_context()
                server = smtplib.SMTP_SSL(profile.smtp_host, profile.smtp_port,
                                          context=ctx, timeout=30)
            else:
                server = smtplib.SMTP(profile.smtp_host, profile.smtp_port, timeout=30)
                if use_starttls:
                    server.starttls()

            server.login(profile.username, password)
            server.send_message(msg)
            server.quit()
            return True

        except (smtplib.SMTPException, OSError) as exc:
            logger.warning(
                f"SMTP attempt {attempt + 1}/{max_retries} failed for {to_email}: {exc}"
            )
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # exponential back-off
            else:
                raise
    return False


# ---------------------------------------------------------------------------
# Worker thread function
# ---------------------------------------------------------------------------

def _send_loop(
    campaign_id: int,
    state: "_CampaignState",
    delay_min: float,
    delay_max: float,
):
    """
    The main loop executed inside the worker thread.
    Opens its own DB session — completely independent of FastAPI sessions.
    """
    logger.info(f"[Engine] Campaign {campaign_id} — worker thread started.")
    db = SessionLocal()

    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            logger.error(f"[Engine] Campaign {campaign_id} not found — aborting.")
            return

        # Mark as running
        campaign.status = CampaignStatus.RUNNING
        campaign.started_at = campaign.started_at or datetime.now(timezone.utc)
        db.commit()
        state.status = "running"

        # Notify campaign started
        _create_notification(
            db, campaign,
            notif_type="info",
            title="Campaign Started",
            message=f"'{campaign.campaign_name}' started sending emails."
        )

        smtp_profile = _get_active_smtp_profile(db)
        if not smtp_profile:
            logger.error("[Engine] No active SMTP profile — aborting campaign.")
            campaign.status = CampaignStatus.FAILED
            db.commit()
            state.status = "stopped"
            return

        # Collect contacts that don't have a sent/delivered log yet
        sent_contact_ids = (
            db.query(EmailLog.contact_id)
            .filter(
                EmailLog.campaign_id == campaign_id,
                EmailLog.delivery_status.in_(["sent", "delivered"]),
            )
            .subquery()
        )
        contacts = (
            db.query(Contact)
            .filter(
                Contact.campaign_id == campaign_id,
                ~Contact.id.in_(sent_contact_ids),
            )
            .all()
        )

        logger.info(
            f"[Engine] Campaign {campaign_id} — {len(contacts)} contacts to process."
        )

        for contact in contacts:
            # ── STOP check ──────────────────────────────────────────────────
            if state.stop_event.is_set():
                logger.info(f"[Engine] Campaign {campaign_id} — stop requested.")
                break

            # ── PAUSE check (blocks until resumed or stopped) ────────────────
            if not state.pause_event.is_set():
                logger.info(f"[Engine] Campaign {campaign_id} — paused, waiting…")
                state.status = "paused"
                campaign.status = CampaignStatus.PAUSED
                db.commit()

                # Block here until resume() sets pause_event OR stop is called
                while not state.pause_event.wait(timeout=1.0):
                    if state.stop_event.is_set():
                        break

                if state.stop_event.is_set():
                    logger.info(f"[Engine] Campaign {campaign_id} — stopped while paused.")
                    break

                # Resumed — re-fetch campaign & smtp profile (may have changed)
                db.expire_all()
                campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
                smtp_profile = _get_active_smtp_profile(db)
                campaign.status = CampaignStatus.RUNNING
                db.commit()
                state.status = "running"
                logger.info(f"[Engine] Campaign {campaign_id} — resumed.")

            # ── Build personalized content ───────────────────────────────────
            variables = {
                "first_name": contact.first_name or "",
                "last_name": contact.last_name or "",
                "email": contact.email or "",
                "phone": getattr(contact, "phone", "") or "",
                "company": getattr(contact, "company", "") or "",
            }
            subject = TemplateRenderer.render(campaign.subject, variables)
            # Use campaign.template field
            raw_body = TemplateRenderer.render(campaign.template, variables)
            
            # Convert plain text newlines to HTML line breaks
            html_body = raw_body.replace('\n', '<br>')

            # Tracking pixel
            tracking_id = str(uuid.uuid4())
            
            # Add unsubscribe link
            unsubscribe_link = f"https://carlyshayn.com/unsubscribe/{tracking_id}"
            tracked_html = (
                f"<div style='font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #333;'>"
                f"{html_body}"
                f"</div>"
                f"<br><br>"
                f"<div style='font-size: 12px; color: #666; margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd;'>"
                f"<a href='{unsubscribe_link}' style='color: #666; text-decoration: underline;'>Unsubscribe</a> | "
                f"This email was sent to {contact.email}"
                f"</div>"
                f"<img src='https://track.carlyshayn.com/open/{tracking_id}'"
                f" width='1' height='1' style='display:none;' />"
            )
            text_body = (
                raw_body
                + f"\n\n---\nUnsubscribe: {unsubscribe_link}\nThis email was sent to {contact.email}"
            )

            # ── Upsert EmailLog record ───────────────────────────────────────
            log = (
                db.query(EmailLog)
                .filter(
                    EmailLog.campaign_id == campaign_id,
                    EmailLog.contact_id == contact.id,
                )
                .first()
            )
            if not log:
                log = EmailLog(
                    campaign_id=campaign_id,
                    contact_id=contact.id,
                    recipient_email=contact.email,
                    subject=subject,
                    body=tracked_html,
                    tracking_id=tracking_id,
                    delivery_status="pending",
                )
                db.add(log)
                db.flush()

            # ── Send ─────────────────────────────────────────────────────────
            msg = _build_message(smtp_profile, contact.email, subject,
                                 tracked_html, text_body, tracking_id)
            try:
                _send_via_smtplib(smtp_profile, msg, contact.email)
                log.delivery_status = "delivered"
                log.sent_at = datetime.now(timezone.utc)
                log.delivered_at = datetime.now(timezone.utc)
                campaign.sent_count = (campaign.sent_count or 0) + 1
                campaign.delivered_count = (campaign.delivered_count or 0) + 1
                # Increment user's used email counter
                if campaign.user_id:
                    from app.models.user import User
                    u = db.query(User).filter(User.id == campaign.user_id).first()
                    if u:
                        u.emails_used = (u.emails_used or 0) + 1
                logger.info(
                    f"[Engine] ✓ Sent to {contact.email} "
                    f"(campaign {campaign_id}, "
                    f"sent={campaign.sent_count})"
                )

            except Exception as exc:
                log.delivery_status = "failed"
                log.error_message = str(exc)
                campaign.failed_count = (campaign.failed_count or 0) + 1
                logger.error(
                    f"[Engine] ✗ Failed to send to {contact.email}: {exc}"
                )

            db.commit()

            # ── STOP check again (before sleeping) ──────────────────────────
            if state.stop_event.is_set():
                break

            # ── Random delay between emails ──────────────────────────────────
            delay = random.uniform(delay_min, delay_max)
            logger.info(
                f"[Engine] Waiting {delay:.1f}s before next email…"
            )
            # Sleep in small chunks so stop/pause is responsive
            elapsed = 0.0
            while elapsed < delay:
                if state.stop_event.is_set():
                    break
                if not state.pause_event.is_set():
                    # Hit pause mid-delay — loop back to top to handle pause logic
                    break
                time.sleep(min(1.0, delay - elapsed))
                elapsed += 1.0

        # ── Loop finished — decide final status ──────────────────────────────
        if state.stop_event.is_set():
            campaign.status = CampaignStatus.COMPLETED
            state.status = "stopped"
            logger.info(f"[Engine] Campaign {campaign_id} — stopped by user.")
        else:
            campaign.status = CampaignStatus.COMPLETED
            campaign.completed_at = datetime.now(timezone.utc)
            state.status = "completed"
            logger.info(f"[Engine] Campaign {campaign_id} — all emails processed, completed.")
            # Create completion notification
            _create_notification(
                db, campaign,
                notif_type="success",
                title="Campaign Completed",
                message=f"'{campaign.campaign_name}' — {campaign.sent_count} emails sent, {campaign.delivered_count} delivered."
            )

        db.commit()

    except Exception as exc:
        logger.exception(f"[Engine] Campaign {campaign_id} — unexpected error: {exc}")
        try:
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if campaign:
                campaign.status = CampaignStatus.FAILED
                db.commit()
        except Exception:
            pass
        state.status = "stopped"
    finally:
        db.close()
        logger.info(f"[Engine] Campaign {campaign_id} — worker thread exited.")


# ---------------------------------------------------------------------------
# Campaign Engine Singleton
# ---------------------------------------------------------------------------

class CampaignEngine:
    """
    Singleton that manages background email sending threads.
    One thread per campaign; uses threading.Event for pause/resume/stop.
    """

    def __init__(self, delay_min: float = 20.0, delay_max: float = 60.0):
        self._lock = threading.Lock()
        self._campaigns: dict[int, _CampaignState] = {}
        self.delay_min = delay_min
        self.delay_max = delay_max

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self, campaign_id: int) -> dict:
        """
        Launch a background thread to send the campaign.
        Raises ValueError if already running.
        """
        with self._lock:
            existing = self._campaigns.get(campaign_id)
            if existing and existing.is_alive():
                raise ValueError(
                    f"Campaign {campaign_id} is already running."
                )

            state = _CampaignState(campaign_id)
            thread = threading.Thread(
                target=_send_loop,
                args=(campaign_id, state, self.delay_min, self.delay_max),
                name=f"campaign-{campaign_id}",
                daemon=True,
            )
            state.thread = thread
            self._campaigns[campaign_id] = state
            thread.start()

        logger.info(f"[Engine] Campaign {campaign_id} — thread launched.")
        return {"started": True, "campaign_id": campaign_id}

    def pause(self, campaign_id: int) -> dict:
        """Signal the worker to pause after the current email."""
        state = self._get_state(campaign_id)
        state.pause_event.clear()   # worker will block on wait()
        state.status = "paused"
        logger.info(f"[Engine] Campaign {campaign_id} — pause signal sent.")
        return {"paused": True, "campaign_id": campaign_id}

    def resume(self, campaign_id: int) -> dict:
        """Resume a paused campaign."""
        state = self._get_state(campaign_id)
        state.pause_event.set()     # unblocks the worker
        state.status = "running"
        logger.info(f"[Engine] Campaign {campaign_id} — resume signal sent.")
        return {"resumed": True, "campaign_id": campaign_id}

    def stop(self, campaign_id: int) -> dict:
        """
        Signal the worker to stop after the current email.
        Also unblocks any pause so the thread can exit cleanly.
        """
        state = self._get_state(campaign_id, allow_missing=True)
        if state is None:
            return {"stopped": True, "campaign_id": campaign_id, "note": "was not running"}

        state.stop_event.set()
        state.pause_event.set()   # wake up if currently paused
        state.status = "stopped"
        logger.info(f"[Engine] Campaign {campaign_id} — stop signal sent.")
        return {"stopped": True, "campaign_id": campaign_id}

    def stop_all(self):
        """Stop all running campaigns — call on application shutdown."""
        with self._lock:
            campaign_ids = list(self._campaigns.keys())
        for cid in campaign_ids:
            try:
                self.stop(cid)
            except Exception:
                pass
        logger.info("[Engine] All campaigns signalled to stop.")

    def get_progress(self, campaign_id: int, db) -> dict:
        """
        Return enriched live progress for a campaign.
        Combines in-memory thread state with live DB counts + timing metrics.
        """
        now = datetime.now(timezone.utc)

        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return {"error": "Campaign not found"}

        state = self._campaigns.get(campaign_id)
        is_running = state.is_alive() if state else False
        is_paused = (
            (not state.pause_event.is_set())
            if (state and is_running)
            else False
        )

        total = campaign.total_emails or 0
        sent = campaign.sent_count or 0
        delivered = campaign.delivered_count or 0
        failed = campaign.failed_count or 0

        # Count emails still in 'pending' state in the log
        pending_in_db = (
            db.query(EmailLog)
            .filter(
                EmailLog.campaign_id == campaign_id,
                EmailLog.delivery_status == "pending",
            )
            .count()
        )
        # Contacts with no log at all are also pending
        logged_contact_ids = (
            db.query(EmailLog.contact_id)
            .filter(EmailLog.campaign_id == campaign_id)
            .subquery()
        )
        not_started = (
            db.query(Contact)
            .filter(
                Contact.campaign_id == campaign_id,
                ~Contact.id.in_(logged_contact_ids),
            )
            .count()
        )
        pending = pending_in_db + not_started
        processed = sent + failed
        progress_pct = round((processed / total * 100), 2) if total > 0 else 0.0

        # ── Timing metrics ────────────────────────────────────────────────────
        started_at = campaign.started_at
        elapsed_seconds: Optional[float] = None
        estimated_remaining_seconds: Optional[float] = None
        send_rate_per_hour: Optional[float] = None

        if started_at is not None:
            # Normalise to UTC-aware
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=timezone.utc)
            elapsed_seconds = (now - started_at).total_seconds()

            if elapsed_seconds > 0 and processed > 0:
                rate_per_sec = processed / elapsed_seconds
                send_rate_per_hour = round(rate_per_sec * 3600, 2)
                if pending > 0:
                    estimated_remaining_seconds = round(pending / rate_per_sec, 1)

        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.campaign_name,
            "status": campaign.status.value,
            "is_running": is_running,
            "is_paused": is_paused,
            "total": total,
            "sent": sent,
            "delivered": delivered,
            "failed": failed,
            "pending": pending,
            "progress_pct": progress_pct,
            "started_at": started_at,
            "completed_at": campaign.completed_at,
            "elapsed_seconds": elapsed_seconds,
            "estimated_remaining_seconds": estimated_remaining_seconds,
            "send_rate_per_hour": send_rate_per_hour,
            "snapshot_at": now,
        }

    def get_all_progress(self, db) -> dict:
        """
        Return progress for ALL campaigns that are running or paused.
        Used by the /campaigns/progress/all endpoint.
        """
        from app.models.campaign import CampaignStatus as CS
        now = datetime.now(timezone.utc)

        active_campaigns = (
            db.query(Campaign)
            .filter(Campaign.status.in_([CS.RUNNING, CS.PAUSED]))
            .all()
        )

        results = []
        for campaign in active_campaigns:
            progress = self.get_progress(campaign.id, db)
            if "error" not in progress:
                results.append(progress)

        running = [r for r in results if r["is_running"] and not r["is_paused"]]
        paused = [r for r in results if r["is_paused"]]

        return {
            "active_count": len(running),
            "paused_count": len(paused),
            "campaigns": results,
            "snapshot_at": now,
        }

    # ── Internals ─────────────────────────────────────────────────────────────

    def _get_state(self, campaign_id: int,
                   allow_missing: bool = False) -> Optional[_CampaignState]:
        with self._lock:
            state = self._campaigns.get(campaign_id)
        if state is None and not allow_missing:
            raise ValueError(
                f"Campaign {campaign_id} is not running in the engine."
            )
        return state


# Module-level singleton — import this everywhere
campaign_engine = CampaignEngine(delay_min=1.0, delay_max=2.0)
