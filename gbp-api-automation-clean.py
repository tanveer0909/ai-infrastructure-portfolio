"""
GBP API Automation Script
Author: Tanveer Ahmad
Company: ActLocal UAE
Date: March 2026

Description:
    Automates Google Business Profile (GBP) posts across 100+ business locations
    using OAuth 2.0 authentication with automatic token refresh.
    Built for ActLocal UAE's AI-powered local SEO automation pipeline.
"""

import os
import json
import time
import requests
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ─── CONFIG ───────────────────────────────────────────────────────────────────

CLIENT_ID       = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET   = os.getenv("GOOGLE_CLIENT_SECRET")
REFRESH_TOKEN   = os.getenv("GOOGLE_REFRESH_TOKEN")
TOKEN_URI       = "https://oauth2.googleapis.com/token"

GBP_API_VERSION = "v4"
SCOPES          = ["https://www.googleapis.com/auth/business.manage"]

# ─── AUTH: AUTO TOKEN REFRESH ─────────────────────────────────────────────────

def get_credentials():
    """
    Load credentials from env variables.
    Automatically refreshes access token using refresh token.
    """
    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        token_uri=TOKEN_URI,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES,
    )
    # Auto-refresh if expired
    if not creds.valid:
        creds.refresh(Request())
        print(f"[AUTH] Token refreshed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return creds


# ─── FETCH ALL BUSINESS ACCOUNTS ──────────────────────────────────────────────

def get_all_accounts(service):
    """
    Fetch all GBP accounts accessible via authenticated credentials.
    Returns list of account names.
    """
    accounts = []
    response = service.accounts().list().execute()
    for account in response.get("accounts", []):
        accounts.append(account["name"])
    print(f"[INFO] Found {len(accounts)} account(s)")
    return accounts


# ─── FETCH ALL LOCATIONS FOR AN ACCOUNT ───────────────────────────────────────

def get_locations(service, account_name):
    """
    Fetch all business locations under a given account.
    Returns list of location objects.
    """
    locations = []
    page_token = None

    while True:
        kwargs = {"parent": account_name, "pageSize": 100}
        if page_token:
            kwargs["pageToken"] = page_token

        response = service.accounts().locations().list(**kwargs).execute()
        locations.extend(response.get("locations", []))

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    print(f"[INFO] Found {len(locations)} location(s) under {account_name}")
    return locations


# ─── CREATE POST FOR A SINGLE LOCATION ────────────────────────────────────────

def create_post(service, location_name, post_text, cta_url=None):
    """
    Create a Google Business Profile post for a single location.

    Args:
        location_name: Full resource name e.g. accounts/123/locations/456
        post_text: Text content of the post
        cta_url: Optional call-to-action URL
    """
    post_body = {
        "languageCode": "en-US",
        "summary": post_text,
        "topicType": "STANDARD",
    }

    if cta_url:
        post_body["callToAction"] = {
            "actionType": "LEARN_MORE",
            "url": cta_url,
        }

    try:
        response = service.accounts().locations().localPosts().create(
            parent=location_name,
            body=post_body
        ).execute()
        print(f"[POST] ✅ Posted to {location_name.split('/')[-1]}")
        return response
    except Exception as e:
        print(f"[ERROR] ❌ Failed for {location_name}: {e}")
        return None


# ─── BULK POST TO ALL LOCATIONS ───────────────────────────────────────────────

def bulk_post_all_locations(post_text, cta_url=None, delay=1.5):
    """
    Main function: Post to ALL locations across ALL accounts.
    Built to handle 100+ businesses simultaneously.

    Args:
        post_text: Content to post on all GBP listings
        cta_url: Optional call-to-action link
        delay: Seconds between each post (avoid rate limiting)
    """
    print("\n" + "="*60)
    print("  GBP Bulk Post Automation - ActLocal UAE")
    print("  Author: Tanveer Ahmad")
    print("="*60 + "\n")

    creds   = get_credentials()
    service = build("mybusiness", GBP_API_VERSION, credentials=creds)

    accounts  = get_all_accounts(service)
    total     = 0
    success   = 0
    failed    = 0

    for account in accounts:
        locations = get_locations(service, account)
        for location in locations:
            location_name = location["name"]
            result = create_post(service, location_name, post_text, cta_url)
            total += 1
            if result:
                success += 1
            else:
                failed += 1
            time.sleep(delay)  # Rate limit protection

    print("\n" + "="*60)
    print(f"  DONE | Total: {total} | ✅ Success: {success} | ❌ Failed: {failed}")
    print("="*60 + "\n")


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

if __name__ == "__main__":

    POST_TEXT = """
    🌟 Special offer this week at our location!
    Contact us today for more details.
    #ActLocal #Dubai #UAE
    """

    CTA_URL = "https://actlocal.ae"

    bulk_post_all_locations(post_text=POST_TEXT, cta_url=CTA_URL)




