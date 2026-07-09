#!/usr/bin/env python3
"""
Gmail Inbox Cleanup Tool — agent-friendly, no stdin required.

Modes:
  analyze          — scan inbox, write results to gmail_analysis.json
  report           — print summary from gmail_analysis.json
  execute          — trash + unsubscribe approved senders (pass --approve or --approve-all)

Usage:
  python3 gmail_cleanup.py analyze
  python3 gmail_cleanup.py report
  python3 gmail_cleanup.py execute --approve-all-junk
  python3 gmail_cleanup.py execute --approve "domain1.com,domain2.com"
  python3 gmail_cleanup.py execute --approve-uncertain "domain1.com" --skip-uncertain "domain2.com"
"""

import json
import os
import re
import sys
import urllib.request
import warnings
from collections import defaultdict
from pathlib import Path

warnings.filterwarnings("ignore")

CREDENTIALS_FILE = Path.home() / ".agents" / "credentials.json"
TOKEN_FILE = Path("/var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/gmail_token.json")
ANALYSIS_FILE = Path("/var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/gmail_analysis.json")
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.readonly",
]

# ── Auth ──────────────────────────────────────────────────────────────────────

def load_gmail_creds():
    with open(CREDENTIALS_FILE) as f:
        data = json.load(f)
    c = data["gmail"]
    return c["client_id"], c["client_secret"]

def authenticate():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    client_id, client_secret = load_gmail_creds()
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        }
    }

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return creds

def build_service(creds):
    from googleapiclient.discovery import build
    return build("gmail", "v1", credentials=creds)

# ── Gmail helpers ─────────────────────────────────────────────────────────────

def list_messages(service, query="", max_results=1000):
    messages = []
    page_token = None
    while len(messages) < max_results:
        kwargs = {"userId": "me", "maxResults": min(500, max_results - len(messages)), "q": query}
        if page_token:
            kwargs["pageToken"] = page_token
        result = service.users().messages().list(**kwargs).execute()
        messages.extend(result.get("messages", []))
        page_token = result.get("nextPageToken")
        if not page_token:
            break
    return messages

def get_message(service, msg_id):
    return service.users().messages().get(userId="me", id=msg_id, format="full").execute()

def extract_headers(msg):
    headers = {}
    for h in msg.get("payload", {}).get("headers", []):
        headers[h["name"].lower()] = h["value"]
    return headers

def get_list_unsubscribe(headers):
    raw = headers.get("list-unsubscribe", "")
    if not raw:
        return None, None
    urls = re.findall(r'<(https?://[^>]+)>', raw)
    mailtos = re.findall(r'<mailto:([^>]+)>', raw)
    return (urls[0] if urls else None), (mailtos[0] if mailtos else None)

# ── Classification ────────────────────────────────────────────────────────────

# Senders confirmed as junk by user across all sessions
CONFIRMED_JUNK_DOMAINS = {
    "linkedin.com", "e.harborfreight.com", "harborfreight.com",
    "parentsquare.com",  # digests only — direct teacher msgs kept separately
    "is.email.nextdoor.com", "rs.email.nextdoor.com",
    "e1.theathletic.com", "snapworx.com", "google.com", "accounts.google.com",
    "4honline.com", "vesta.threadloom.news", "phreesia-mail.com", "phreesia.com",
    "welcome.wondrhealth.com", "seatgeek.com", "home.upstart.com",
    "mail.instagram.com", "priority.instagram.com", "your.omadahealth.com",
    "receipt.lowes.com", "e.lowes.com", "notifications.lowes.com",
    "confirmation.lowes.com", "lowes.com",
    "e.toyota.com", "postable.com", "marketing.onxmaps.com", "camas.wednet.edu",
    "emails.synchrony.com", "servicing.synchrony.com", "email.close.com",
    "guest.valvoline.com", "email.openai.com", "email.claude.com",
    "clarkpud.com", "linuxfoundation.org", "cncf.io",
    "messages.offerup.com", "email.offerup.com", "updates.offerup.com",
    "peacehealth.org", "info6.citi.com", "info3.citi.com", "info15.citi.com",
    "clientexperience.citi.com",
    "spotify.com", "legal.spotify.com", "joinmochi.com",
    "yourmortgageonline.com", "email.skyzone.com", "peachjar.com",
    "mail.fidelity.com", "cascadeforest.org", "updates.otter.ai",
    "marketing.otter.ai", "otter.ai",
    "costcosameday.instacartemail.com", "mail.house.gov",
    "marketing.zoomcare.com", "care.lifestance.com",
    "mail.express-scripts.com", "benefits.express-scripts.com",
    "marketing.sg.weavecoms.com", "vantage.sh", "columbiacumail.org",
    "mail.clickup.com", "digital-delivery.com", "kubotausa.com",
    "notify.cloudflare.com", "em1.cloudflare.com", "fairentry.com",
    "express.medallia.com", "mail.costcoauto.com", "birdeye.com",
    "eonline.e-vanguard.com", "safeopt.com", "mail.route.com",
    "covered.amerisaveinsurance.com", "pmrloans.com", "mail.greatclips.com",
    "wcicustomer.com", "open.feeld.co", "myasdfsupport.org",
    "amazon.com", "walmart.com", "columbiacu.org", "s.usa.experian.com",
    "bricksandminifigs.com", "redfin.com", "gmail.com",  # newsletter sender
    "anoma.ly", "finalforms.com", "mail.anthropic.com", "email.anthropic.com",
    "mail.fidelity.com", "team.public.com", "information.optum.com",
    "em.optum.com", "email.optumfinancial.com", "googlemail.com",
    "ascensus.com", "e.ea.com", "1password.com", "chase.com", "e.geico.com",
    "businessolver.com", "t.databricks.com", "proxyvote.com", "typst.app",
    "3dproductconfigurator.com", "docusign.net", "inmomentfeedback.com",
    "info.providence.org", "campaigns.nexhealth.com", "healthadvocate.com",
    "kubota-kna.com", "getchipdrop.com", "mt.lids.com", "breathe.calm.com",
    "pypi.org", "po.atlassian.net", "starlink.com", "rosequarter.com",
    "advancedmd.com", "email.netgear.com", "fathom.video", "pydantic.dev",
    "mail.beehiiv.com", "regus.com", "substack.com", "scratch.org",
    "letu.edu", "pearly.co", "email.nfl.com", "accountprotection.microsoft.com",
    "microsoft.com", "redditmail.com", "e.amerisave.com", "touchnote.com",
    "otter.ai", "binance.us", "mailgun.patreon.com", "labcorpmessage.com",
    "em.autozone.com", "sentry.io", "husted.senate.gov", "email.roku.com",
    "deviantart.com", "innovations.samsungusa.com", "service.paypal.com",
    "notifications.t-mobile.com", "patients.pgsurveying.com", "link.com",
    "id.atlassian.com", "pcgus.com", "chess.com", "fishercareers.com",
    "mg.homedepot.com", "lwcrm.com", "notifications.dol.wa.gov",
    "plenom.com", "notifications.kubotacreditusa.com", "wcicustomer.com",
    "taxes1-notifications.cash.app", "taxes-notifications.cash.app",
    "taxes-marketing.cash.app", "t.assurant.com", "hrblock.com",
    "email.referral-mail.com", "mail.grammarly.com", "imdb.com",
    "sketchup.com", "audible.com", "ereceipt.usps.gov", "account.netflix.com",
    "e.fitbit.com", "paypal.com", "mail6.lendingclub.com", "email.venmo.com",
    "stripe.com", "alerts.tryfi.com", "square.com", "inmomentfeedback.com",
    "columbiacu.org", "venmo.com", "t-mobile.com", "trx.mail2.disneyplus.com",
    "paddle.com", "kubotacreditusa.com", "infomails.microsoft.com", "et.geico.com",
    "payhipupdates.com", "mhe-tuckerbeck.atlassian.net", "hulumail.com",
    "airbnb.com", "tax-docs.com", "infoemails.microsoft.com",
    "service.playdeltaforce.com", "account.tiktok.com", "service.hbomax.com",
    "mail.public.com", "portlandleather.org", "mheducation.com",
    "coplogic.com", "mybrightwheel.com", "upstash.com", "huggingface.co",
    "questdiagnostics.com", "investordelivery.com", "anvil.works", "tvc.org",
    "permitium.com", "kinkfest.org", "deals.priceline.com", "news.hims.com",
    "digitalocean.com", "hello.wondrhealth.com", "myluckytag.com",
    "sundaysfordogs.com", "costco.com", "accounts.nintendo.com",
    "mail.beehiiv.com", "geeksforgeeks.org", "realpython.com",
    "thedailybeast.com", "hecsllc.com", "updates.cash.app",
    "express.sea1.medallia.com", "email.livenation.com", "ownid.com",
    "emails.schoolstore.com", "appstore.amazon.com", "email.jobleads.com",
    "email.gasbuddy.com", "funds.e-vanguard.com", "lastpass.com",
    "calendly.com", "email.twentytwowords.com", "signupgenius.com",
    "stanford.edu", "covered.amerisaveinsurance.com", "scratch.mit.edu",
    "system.t-mobile.com", "email.dreo.com", "costcoauto.com",
    "discord.com", "glassdoor.com", "votesaveamerica.com", "rosalind.info",
    "uber.com", "mail.postman.com", "tm.openai.com", "info.1password.com",
    "lyftmail.com", "eml.upstart.com", "raindrop.io", "youtube.com",
    "info11.citi.com", "postman.com", "secured-server.biz",
    "mail.app.supabase.io", "hbomax.com", "emails.myschoolorders.com",
}

# Subjects/snippets that indicate auto-junk regardless of sender
JUNK_SUBJECT_PATTERNS = [
    # Order / shipping / delivery
    r"order (confirmed|shipped|delivered|receipt|tracking|on the way|is ready|placed)",
    r"(shipment|package|delivery) (notification|update|confirmed|shipped|tracking|on its way)",
    r"(your order|your package|your shipment)",
    r"it('s| is) on the way",
    # Payments / billing / receipts
    r"(your|a) (payment|charge|autopay|auto pay|statement|invoice|receipt|bill)",
    r"payment (received|submitted|processed|confirmed|reminder|due|authorized)",
    r"(statement|balance|account|invoice) (is )?(now |)available",
    r"your receipt from",
    r"refund (issued|processed|on the way)",
    # Notifications / confirmations / alerts
    r"(alert|reminder|notification|notice)[:,\s]",
    r"(confirmation|confirmed):? ",
    r"was (received|approved|submitted|accepted|processed)",
    r"has been (approved|received|submitted|processed|shipped|delivered|updated|activated)",
    r"action required",
    r"(verify|confirm) your (email|account|identity|phone)",
    r"verification code",
    r"one.time (code|password|pin)",
    r"security (alert|code|notification|warning)",
    r"sign.?in (alert|notification|from new|detected)",
    r"new (device|sign.?in|login)",
    r"new login",
    # Financial / account notices
    r"(fico|credit) score",
    r"dividend",
    r"(hsa|retirement|401k|fidelity|vanguard|401).*(statement|available|ready)",
    r"large (withdrawal|deposit|transfer)",
    r"(irs|tax form|5498|1099|w-2)",
    r"(account|subscription|membership|plan|service).*(expir|renew|updat|cancel|chang)",
    r"upcoming (charge|payment|renewal|price)",
    r"privacy (notice|policy|update)",
    r"terms (of service|and conditions|update)",
    r"we('ve| have) updated",
    r"important update",
    r"important (notice|message|information)",
    # School / community
    r"(school|district|library).*(fine|overdue|balance|notice|reminder|lunch|digest)",
    r"tardy|missing assignment|attendance",
    r"(weekly|monthly|daily|quarterly) (digest|newsletter|recap|summary|update|report)",
    # Marketing
    r"(save|% off|deal|sale|promo|discount|coupon|offer|free shipping|last chance)",
    r"(new episode|now available|watch now|streaming now)",
    r"(unsubscribe|opt.out)",
    r"(last chance|ends (today|soon|tonight)|don't miss|limited time)",
    r"newsletter",
]

# Senders confirmed personal — never touch
CONFIRMED_PERSONAL_DOMAINS = {
    "aptot.com",   # OT therapist direct messages
}

# Subjects that indicate a direct personal message even from bulk-ish senders
PERSONAL_SUBJECT_PATTERNS = [
    r"^re:",
    r"^fwd?:",
    r"zoom link",
    r"new message in .* (liberty|camas)",   # direct teacher msgs via parentsquare
]

def classify_email(msg, headers):
    from_addr = headers.get("from", "").lower()
    subject = headers.get("subject", "").lower()
    snippet = msg.get("snippet", "").lower()
    has_unsubscribe = bool(headers.get("list-unsubscribe"))
    has_list_id = bool(headers.get("list-id"))
    precedence = headers.get("precedence", "").lower()
    domain = sender_key(from_addr)

    # Confirmed personal — never touch
    if domain in CONFIRMED_PERSONAL_DOMAINS:
        return "personal", "confirmed personal domain"

    # Personal subject patterns — keep even from otherwise junky senders
    for pattern in PERSONAL_SUBJECT_PATTERNS:
        if re.search(pattern, subject):
            return "personal", f"personal subject: {pattern}"

    # Confirmed junk domains
    if domain in CONFIRMED_JUNK_DOMAINS:
        return "junk", "confirmed junk domain"

    # Standard junk header signals
    if has_unsubscribe or has_list_id:
        return "junk", "has List-Unsubscribe/List-Id header"
    if precedence in ("bulk", "list", "junk"):
        return "junk", f"Precedence: {precedence}"

    # Junk sender address patterns
    junk_sender_patterns = [
        r"noreply|no-reply|donotreply|do-not-reply",
        r"(newsletter|marketing|offers|deals|promotions|notifications|updates|digest|alert|info|support|hello|team)@",
        r"@(mailchimp|sendgrid|klaviyo|constantcontact|hubspot|salesforce|marketo|iterable|customer\.io)",
    ]
    for pattern in junk_sender_patterns:
        if re.search(pattern, from_addr):
            return "junk", f"sender matches: {pattern}"

    # Junk subject patterns
    for pattern in JUNK_SUBJECT_PATTERNS:
        if re.search(pattern, subject):
            return "junk", f"subject matches: {pattern}"

    # Conversational / personal signals
    personal_conversational = [
        "hey ", "hi ", "hello", "thanks", "thank you", "sounds good",
        "let me know", "can you", "could you", "talk soon", "see you",
        "just wanted", "following up", "reaching out",
    ]
    if any(w in snippet for w in personal_conversational):
        return "personal", "conversational snippet"

    return "uncertain", "no strong signals"

def sender_key(from_addr):
    """Normalize sender to a grouping key (domain or name)."""
    match = re.search(r'@([\w.\-]+)', from_addr.lower())
    if match:
        return match.group(1)
    clean = re.sub(r'<.*?>', '', from_addr).strip().strip('"')
    return clean or from_addr

# ── Analyze mode ──────────────────────────────────────────────────────────────

def cmd_analyze(service, max_results=1000):
    print(f"Fetching up to {max_results} inbox messages...")
    messages = list_messages(service, query="in:inbox -in:sent -in:drafts", max_results=max_results)
    print(f"Found {len(messages)} messages. Analyzing...", end="", flush=True)

    by_classification = {"junk": [], "personal": [], "uncertain": []}

    for i, msg_ref in enumerate(messages):
        msg = get_message(service, msg_ref["id"])
        headers = extract_headers(msg)
        classification, reason = classify_email(msg, headers)
        from_addr = headers.get("from", "unknown")
        subject = headers.get("subject", "(no subject)")
        unsub_url, unsub_mailto = get_list_unsubscribe(headers)

        item = {
            "id": msg_ref["id"],
            "from": from_addr,
            "subject": subject,
            "snippet": msg.get("snippet", "")[:200],
            "classification": classification,
            "reason": reason,
            "unsub_url": unsub_url,
            "unsub_mailto": unsub_mailto,
            "sender_key": sender_key(from_addr),
        }
        by_classification[classification].append(item)

        if (i + 1) % 100 == 0:
            print(f" {i+1}", end="", flush=True)

    print(" done.\n")

    # Group by sender key
    grouped = {}
    for cls in ("junk", "uncertain"):
        groups = defaultdict(list)
        for item in by_classification[cls]:
            groups[item["sender_key"]].append(item)
        grouped[cls] = {k: v for k, v in sorted(groups.items(), key=lambda x: -len(x[1]))}

    analysis = {
        "total": len(messages),
        "personal_count": len(by_classification["personal"]),
        "junk_count": len(by_classification["junk"]),
        "uncertain_count": len(by_classification["uncertain"]),
        "junk_by_sender": grouped["junk"],
        "uncertain_by_sender": grouped["uncertain"],
    }

    ANALYSIS_FILE.write_text(json.dumps(analysis, indent=2))
    print(f"Analysis saved to {ANALYSIS_FILE}")
    cmd_report()

# ── Report mode ───────────────────────────────────────────────────────────────

def cmd_report():
    data = json.loads(ANALYSIS_FILE.read_text())
    print(f"\n{'='*70}")
    print(f"INBOX ANALYSIS REPORT")
    print(f"{'='*70}")
    print(f"Total analyzed : {data['total']}")
    print(f"Personal       : {data['personal_count']} (will NOT be touched)")
    print(f"Junk           : {data['junk_count']} emails across {len(data['junk_by_sender'])} senders")
    print(f"Uncertain      : {data['uncertain_count']} emails across {len(data['uncertain_by_sender'])} senders")

    print(f"\n{'─'*70}")
    print(f"JUNK SENDERS (sorted by email count)")
    print(f"{'─'*70}")
    for i, (key, items) in enumerate(list(data["junk_by_sender"].items())[:50], 1):
        sample = items[0]
        subjects = list({it["subject"][:55] for it in items[:2]})
        unsub = "unsub-available" if (sample.get("unsub_url") or sample.get("unsub_mailto")) else "no-unsub"
        print(f"  [{i:3d}] {key:<35} {len(items):4d} emails  [{unsub}]")
        for s in subjects:
            print(f"          {s}")

    if len(data["junk_by_sender"]) > 50:
        print(f"  ... and {len(data['junk_by_sender']) - 50} more senders")

    print(f"\n{'─'*70}")
    print(f"UNCERTAIN SENDERS (need judgment)")
    print(f"{'─'*70}")
    for i, (key, items) in enumerate(data["uncertain_by_sender"].items(), 1):
        sample = items[0]
        print(f"  [{i:3d}] {key:<35} {len(items):4d} emails")
        print(f"          From   : {sample['from'][:65]}")
        print(f"          Subject: {sample['subject'][:65]}")
        print(f"          Snippet: {sample['snippet'][:65]}")
        print()

# ── Execute mode ──────────────────────────────────────────────────────────────

def attempt_unsubscribe(unsub_url, unsub_mailto):
    results = []
    if unsub_url:
        try:
            req = urllib.request.Request(unsub_url, headers={"User-Agent": "Mozilla/5.0"}, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                results.append(f"HTTP GET {resp.status}")
        except Exception as e:
            results.append(f"GET failed: {e}")
    if unsub_mailto:
        results.append(f"mailto: {unsub_mailto} (manual)")
    return "; ".join(results) if results else "none"

def batch_trash(service, ids):
    for i, msg_id in enumerate(ids):
        service.users().messages().trash(userId="me", id=msg_id).execute()
        if (i + 1) % 25 == 0:
            print(".", end="", flush=True)

def cmd_execute(service, approve_all_junk=False, approve_senders=None, approve_uncertain=None, skip_uncertain=None):
    data = json.loads(ANALYSIS_FILE.read_text())
    approve_senders = set(s.strip().lower() for s in (approve_senders or []))
    approve_uncertain = set(s.strip().lower() for s in (approve_uncertain or []))
    skip_uncertain = set(s.strip().lower() for s in (skip_uncertain or []))

    to_process = []  # list of (sender_key, items)

    # Junk
    for key, items in data["junk_by_sender"].items():
        if approve_all_junk or key.lower() in approve_senders:
            to_process.append((key, items))

    # Uncertain — only those explicitly approved
    for key, items in data["uncertain_by_sender"].items():
        if key.lower() in approve_uncertain:
            to_process.append((key, items))

    if not to_process:
        print("Nothing to process. Use --approve-all-junk or --approve 'domain1,domain2'")
        return

    total_trashed = 0
    for key, items in to_process:
        print(f"\n[{key}] {len(items)} emails")
        # Unsubscribe
        unsubbed = False
        for item in items:
            if item.get("unsub_url") or item.get("unsub_mailto"):
                result = attempt_unsubscribe(item.get("unsub_url"), item.get("unsub_mailto"))
                print(f"  Unsubscribe: {result}")
                unsubbed = True
                break
        if not unsubbed:
            print(f"  Unsubscribe: no header available")

        # Trash
        ids = [it["id"] for it in items]
        print(f"  Trashing {len(ids)} emails", end="", flush=True)
        batch_trash(service, ids)
        print(f" done.")
        total_trashed += len(ids)

    print(f"\n{'='*70}")
    print(f"Done. Trashed {total_trashed} emails from {len(to_process)} senders.")

# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    mode = args[0]

    if mode == "report":
        cmd_report()
        return

    creds = authenticate()
    service = build_service(creds)

    if mode == "analyze":
        max_r = 1000
        for i, a in enumerate(args):
            if a == "--max" and i + 1 < len(args):
                max_r = int(args[i + 1])
        cmd_analyze(service, max_results=max_r)

    elif mode == "execute":
        approve_all_junk = "--approve-all-junk" in args
        approve_senders = []
        approve_uncertain = []
        skip_uncertain = []

        for i, a in enumerate(args):
            if a == "--approve" and i + 1 < len(args):
                approve_senders = [s.strip() for s in args[i + 1].split(",")]
            if a == "--approve-uncertain" and i + 1 < len(args):
                approve_uncertain = [s.strip() for s in args[i + 1].split(",")]
            if a == "--skip-uncertain" and i + 1 < len(args):
                skip_uncertain = [s.strip() for s in args[i + 1].split(",")]

        cmd_execute(service,
                    approve_all_junk=approve_all_junk,
                    approve_senders=approve_senders,
                    approve_uncertain=approve_uncertain,
                    skip_uncertain=skip_uncertain)
    else:
        print(f"Unknown mode: {mode}")
        print(__doc__)

if __name__ == "__main__":
    main()
