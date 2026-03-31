# GBP API Automation Script
**Author:** Tanveer Ahmad  
**Company:** ActLocal UAE  
**Date:** March 2026

---

## Overview

This script automates Google Business Profile (GBP) posts across **100+ business locations simultaneously** using Google's My Business API with OAuth 2.0 authentication and automatic token refresh.

Built as part of ActLocal UAE's AI-powered local SEO automation pipeline, integrated with OpenClaw AI agent (Lina).

---

## Features

- ✅ **Bulk posting** — Post to 100+ GBP listings in one run
- ✅ **OAuth 2.0** — Secure authentication with auto token refresh
- ✅ **Rate limit protection** — Configurable delay between requests
- ✅ **Error handling** — One failure doesn't stop the rest
- ✅ **CTA support** — Optional call-to-action links
- ✅ **Environment variables** — No hardcoded credentials

---

## Requirements

```bash
pip install google-auth google-auth-httplib2 google-api-python-client
```

---

## Environment Variables

Set these in your `.env` file or VPS environment:

```env
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REFRESH_TOKEN=your_refresh_token
```

---

## How It Works

```
1. Load OAuth credentials from environment
2. Auto-refresh access token if expired
3. Fetch all GBP accounts
4. Fetch all locations under each account
5. Post content to each location
6. Report success/failure summary
```

---

## Usage

```python
from gbp-api-automation-clean import bulk_post_all_locations

bulk_post_all_locations(
    post_text="Your post content here 🌟",
    cta_url="https://actlocal.ae",
    delay=1.5  # seconds between posts
)
```

---

## Infrastructure

This script runs on:
- **VPS:** Hostinger KVM 4 (187.77.159.131)
- **OS:** Ubuntu 24.04 LTS
- **AI Agent:** OpenClaw (Lina) — automated scheduling via cron jobs
- **Auth:** Google OAuth 2.0 with refresh token rotation

---

## Project Structure

```
ai-infrastructure-portfolio/
├── gbp-api-automation-clean.py   # Main automation script
├── GBP_API_README.md             # This file
```

---

## About

Built by **Tanveer Ahmad** as part of ActLocal UAE's digital infrastructure.  
This automation saves hours of manual work by posting to all GBP listings simultaneously.

> *"Infrastructure built to scale local businesses across UAE using AI and automation."*
