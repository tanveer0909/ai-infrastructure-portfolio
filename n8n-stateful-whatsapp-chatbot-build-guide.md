# N8N Stateful WhatsApp Sales Chatbot — Complete Build Guide

**Purpose:** Build a smart WhatsApp sales pipeline chatbot that remembers client state, sends videos at the right time, captures info, books meetings, and follows up automatically.

**Created:** March 28, 2026
**For:** Doniya, Act Local
**AI Brain:** Anthropic Claude 3.5 Sonnet
**Database:** Airtable (tracks client state/stage)

---

## 🎯 What We're Building

A WhatsApp bot that guides clients through this flow:

```
Client sends message
       ↓
Check client's current stage (via Airtable)
       ↓
   ┌───┴───┬─────────┬────────┬─────────┐
   ↓       ↓         ↓        ↓         ↓
 STAGE 1  STAGE 2   STAGE 3  STAGE 4   STAGE 5
 "NEW"    "VIDEO"   "INFO"   "BOOKING" "FOLLOW"
   ↓       ↓         ↓        ↓         ↓
Send      Send      Ask for  Offer    Auto
Intro     Service   Insta/   Meeting  Follow-up
Video     Video     Website  Options  2x/day
   ↓       ↓         ↓        ↓         ↓
Move to   Move to   Move to  Move to   Mark
STAGE 2   STAGE 3   STAGE 4  STAGE 5   DONE
```

**Each client has:**
- Phone number (unique ID)
- Current stage (NEW → VIDEO → INFO → BOOKING → FOLLOW)
- Videos sent? (yes/no)
- Instagram profile (captured)
- Website (captured)
- Booking confirmed? (yes/no)
- Their location (captured)
- Our location shared? (yes/no)
- Follow-ups sent count (1st, 2nd, or done)

---

## 📊 DATABASE SCHEMA (Airtable)

### Table 1: "Clients" (Main tracking table)

```
Columns:
- Phone (Primary Field) — Text — +971XXXXXXXXX
- Name — Text — Customer name
- Stage — Single Select — NEW / VIDEO / INFO / BOOKING / FOLLOW / DONE
- Intro Video Sent — Checkbox — yes/no
- Service Video Sent — Checkbox — yes/no
- Instagram Profile — Text — @username (captured from user)
- Website — Text — https://website.com (captured from user)
- Booking Confirmed — Checkbox — yes/no
- Booking Time — Date — when they want to meet
- Meeting Type — Single Select — ONLINE / OFFLINE
- Their Location — Text — where they want to meet (if offline)
- Their Latitude — Number — for map
- Their Longitude — Number — for map
- Our Location Shared — Checkbox — yes/no
- Follow-ups Sent Count — Number — 0, 1, or 2
- Last Message — Long Text — what they said last
- Created At — Date — when they first messaged
- Updated At — Date — last interaction
- Notes — Long Text — internal notes
```

### Table 2: "Messages Log" (Conversation history)

```
Columns:
- ID (Primary) — Auto-ID
- Phone — Text — +971XXXXXXXXX
- Direction — Single Select — INBOUND / OUTBOUND
- Message Type — Single Select — TEXT / VIDEO / IMAGE / LOCATION
- Content — Long Text — what was sent/received
- Intent — Single Select — greeting / ask_services / ask_booking / share_location / etc
- Created At — Date — timestamp
- Response Type — Single Select — intro_video / service_video / ask_info / booking_offer / follow_up / etc
```

### Table 3: "Scheduled Follow-ups" (For 2x daily automation)

```
Columns:
- ID (Primary) — Auto-ID
- Phone — Text — +971XXXXXXXXX
- Client Name — Text — Name
- Stage — Text — current stage
- Follow-up Number — Number — 1 or 2
- Scheduled For — Date — when to send
- Sent At — Date — when actually sent
- Status — Single Select — PENDING / SENT / SKIPPED
- Created At — Date — timestamp
```

---

## 🏗️ BUILD ORDER (Step-by-Step)

### **PHASE 1: Setup & Infrastructure**

#### Step 1: Create Airtable Base
1. Go to airtable.com
2. Create new base called "Act Local WhatsApp Chatbot"
3. Create 3 tables: "Clients", "Messages Log", "Scheduled Follow-ups"
4. Add all columns from schema above
5. Copy Base ID (from URL: airtable.com/appXXXXXX)
6. Create Personal Access Token (Settings → Tokens)

**Save these:**
```
AIRTABLE_BASE_ID = appXXXXXX
AIRTABLE_TOKEN = pat_XXXXX
AIRTABLE_TABLE_CLIENTS = Clients
AIRTABLE_TABLE_MESSAGES = Messages Log
AIRTABLE_TABLE_FOLLOWUPS = Scheduled Follow-ups
```

#### Step 2: Set Up API Credentials in N8N

In N8N, go to Settings → Environment Variables, add:

```
CLAUDE_API_KEY = sk-ant-XXXXX...
WHATSAPP_BUSINESS_API_TOKEN = EAAB...
WHATSAPP_PHONE_NUMBER_ID = 120123456789
AIRTABLE_BASE_ID = appXXXXXX
AIRTABLE_TOKEN = pat_XXXXX
INTRO_VIDEO_URL = https://cdn.com/intro.mp4
SERVICE_VIDEO_URL = https://cdn.com/services.mp4
OFFICE_ADDRESS = Act Local, Dubai
OFFICE_PHONE = +971 XX XXX XXXX
OFFICE_LAT = 25.2048
OFFICE_LNG = 55.2708
```

#### Step 3: Upload Videos

1. Upload intro video to Cloudinary / AWS S3
2. Upload services video to Cloudinary / AWS S3
3. Get public URLs
4. Add to N8N environment variables above

---

### **PHASE 2: Build Main Workflow**

#### Step 4: Create Workflow "WhatsApp Sales Bot - Main"

**Trigger:** Webhook (WhatsApp messages)

**Overall workflow:**
```
[1. Webhook: Receive Message]
    ↓
[2. Extract Client Data]
    ↓
[3. Look Up Client in Airtable]
    ↓
[4. Determine Client's Current Stage]
    ↓
[5. Route to Stage Handler]
    ├─ Stage: NEW → Send Intro Video (go to Stage 2)
    ├─ Stage: VIDEO → Ask for Instagram/Website (go to Stage 3)
    ├─ Stage: INFO → Send Booking Options (go to Stage 4)
    ├─ Stage: BOOKING → Ask for Meeting Type (online/offline)
    └─ Stage: FOLLOW → Send Auto Follow-up
    ↓
[6. Update Client Stage in Airtable]
    ↓
[7. Log Message to Messages Log]
    ↓
[Done]
```

---

## 🔨 DETAILED NODE BUILD

### **NODE 1: Webhook Trigger**

**Name:** WhatsApp Incoming Message

**Type:** Webhook

**Configuration:**
```
HTTP Method: POST
URL: (auto-generated by N8N)
Respond: Use default
Response Code: 200
Authentication: None
```

**Register with Meta:**
1. Go to Meta Business Manager → WhatsApp API → Webhooks
2. Add N8N webhook URL
3. Verify Token: (create any random string like "verify_token_123")
4. Webhook Fields: messages, contacts
5. Subscribe to: messages, message_status

**Expected Input:**
```json
{
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "from": "971XXXXXXXXX",
          "id": "wamid.xxx",
          "timestamp": "1711615200",
          "text": { "body": "Hi, I need help" },
          "type": "text"
        }],
        "contacts": [{
          "profile": { "name": "Ahmed" },
          "wa_id": "971XXXXXXXXX"
        }],
        "metadata": {
          "phone_number_id": "120123456789"
        }
      }
    }]
  }]
}
```

---

### **NODE 2: Extract Client Data**

**Name:** Extract Message Data

**Type:** Set (Data Transformation)

**Configuration:**

```javascript
// Extract all needed data from WhatsApp message
customerPhone = $json.entry[0].changes[0].value.messages[0].from
customerName = $json.entry[0].changes[0].value.contacts[0].profile.name || "Customer"
messageText = $json.entry[0].changes[0].value.messages[0].text.body
messageId = $json.entry[0].changes[0].value.messages[0].id
timestamp = $json.entry[0].changes[0].value.messages[0].timestamp
phoneNumberId = $json.entry[0].changes[0].value.metadata.phone_number_id

// Normalize phone (remove + if present)
normalizedPhone = customerPhone.replace("+", "")

// Log data
console.log(`New message from ${customerName} (${customerPhone}): ${messageText}`)
```

---

### **NODE 3: Look Up Client in Airtable**

**Name:** Find Client in Database

**Type:** Airtable

**Configuration:**
```
Action: Read
Base: ${AIRTABLE_BASE_ID}
Table: Clients

Filter:
- Phone = ${normalizedPhone}

If no client found, we'll create one in the next step.
```

**Output:**
```json
{
  "records": [
    {
      "id": "recXXXXX",
      "fields": {
        "Phone": "971XXXXXXXXX",
        "Name": "Ahmed",
        "Stage": "NEW",
        "Intro Video Sent": false,
        "Service Video Sent": false,
        "Instagram Profile": null,
        "Website": null,
        ...
      }
    }
  ]
}
```

---

### **NODE 4: Check if Client Exists**

**Name:** Is New Client?

**Type:** Switch

**Configuration:**

```
Condition 1: recordCount > 0
  → Go to NODE 5 (Client exists, continue)

Default: recordCount = 0
  → Go to NODE 4b (Create new client first)
```

---

### **NODE 4b: Create New Client (If New)**

**Name:** Create New Client in Airtable

**Type:** Airtable

**Configuration:**
```
Action: Create record
Base: ${AIRTABLE_BASE_ID}
Table: Clients

Fields:
- Phone: ${normalizedPhone}
- Name: ${customerName}
- Stage: NEW
- Intro Video Sent: false
- Service Video Sent: false
- Instagram Profile: (blank)
- Website: (blank)
- Booking Confirmed: false
- Follow-ups Sent Count: 0
- Last Message: ${messageText}
- Created At: ${new Date().toISOString()}
- Updated At: ${new Date().toISOString()}
```

**Then merge back to NODE 5**

---

### **NODE 5: Get Current Client Record**

**Name:** Get Client Details

**Type:** Set (Data Transformation)

**Configuration:**

```javascript
// Get the client record (from NODE 3 or NODE 4b)
clientRecord = $previous.records && $previous.records.length > 0 ? 
  $previous.records[0] : 
  $previous // if from NODE 4b create response

clientId = clientRecord.id
clientPhone = clientRecord.fields.Phone
clientName = clientRecord.fields.Name
currentStage = clientRecord.fields.Stage
introVideoSent = clientRecord.fields["Intro Video Sent"]
serviceVideoSent = clientRecord.fields["Service Video Sent"]
instagram = clientRecord.fields["Instagram Profile"]
website = clientRecord.fields["Website"]
bookingConfirmed = clientRecord.fields["Booking Confirmed"]
followupsSentCount = clientRecord.fields["Follow-ups Sent Count"] || 0
lastMessage = clientRecord.fields["Last Message"]
```

---

### **NODE 6: Route by Stage**

**Name:** Route by Client Stage

**Type:** Switch

**Configuration:**

```
Switch on: currentStage

Condition 1: currentStage = "NEW"
  → Go to NODE 7a (Send Intro Video)

Condition 2: currentStage = "VIDEO"
  → Go to NODE 7b (Ask for Instagram/Website)

Condition 3: currentStage = "INFO"
  → Go to NODE 7c (Ask for Booking Preference)

Condition 4: currentStage = "BOOKING"
  → Go to NODE 7d (Handle Booking/Location)

Condition 5: currentStage = "FOLLOW"
  → Go to NODE 7e (Send Follow-up)

Default: currentStage = "DONE"
  → Go to NODE 8 (Thank you message)
```

---

## 📹 **NODE 7a: STAGE 1 - SEND INTRO VIDEO**

**Name:** Send Intro Video Handler

**Type:** Group of nodes

### 7a-1: Prepare Intro Message

**Type:** Set

```javascript
introText = `Hey ${clientName}! 👋\n\nGreat to hear from you! Let me show you what we do at Act Local.`
```

### 7a-2: Send Text Before Video

**Type:** HTTP Request (WhatsApp API)

```
Method: POST
URL: https://graph.instagram.com/v18.0/${phoneNumberId}/messages

Headers:
Authorization: Bearer ${WHATSAPP_BUSINESS_API_TOKEN}
Content-Type: application/json

Body:
{
  "messaging_product": "whatsapp",
  "to": "${clientPhone}",
  "type": "text",
  "text": {
    "body": "${introText}"
  }
}
```

### 7a-3: Wait 2 Seconds

**Type:** Wait

```
Time: 2 seconds
```

### 7a-4: Send Intro Video

**Type:** HTTP Request (WhatsApp API)

```
Method: POST
URL: https://graph.instagram.com/v18.0/${phoneNumberId}/messages

Body:
{
  "messaging_product": "whatsapp",
  "to": "${clientPhone}",
  "type": "video",
  "video": {
    "link": "${INTRO_VIDEO_URL}",
    "caption": "🎥 Act Local Intro Video"
  }
}
```

### 7a-5: Wait 2 Seconds

**Type:** Wait

```
Time: 2 seconds
```

### 7a-6: Send Next Step Message

**Type:** HTTP Request (WhatsApp API)

```
Body:
{
  "messaging_product": "whatsapp",
  "to": "${clientPhone}",
  "type": "text",
  "text": {
    "body": "Now, tell us about your business! 🚀\n\nWhat's your Instagram profile? (e.g., @yourname)"
  }
}
```

### 7a-7: Update Client to Stage 2

**Type:** Airtable

```
Action: Update record
Base: ${AIRTABLE_BASE_ID}
Table: Clients
Record ID: ${clientId}

Fields:
- Stage: VIDEO
- Intro Video Sent: true
- Last Message: ${messageText}
- Updated At: ${new Date().toISOString()}
```

**Then → Go to NODE 8 (Log Message)**

---

## 📝 **NODE 7b: STAGE 2 - ASK FOR INSTAGRAM/WEBSITE**

**Name:** Capture Instagram & Website

**Type:** Group of nodes

### 7b-1: Check if Message Has Instagram/Website

**Type:** Set

```javascript
// Simple pattern matching
hasInstagram = messageText.includes("@") || messageText.includes("instagram")
hasWebsite = messageText.includes("http") || messageText.includes(".com") || messageText.includes(".ae")
isLikelyInstagram = messageText.length < 50 && messageText.startsWith("@")

extractedInstagram = isLikelyInstagram ? messageText.trim() : null
extractedWebsite = hasWebsite ? messageText.trim() : null
```

### 7b-2: Validate Input (Optional - Use Claude)

**Type:** HTTP Request (Anthropic Claude)

```
Method: POST
URL: https://api.anthropic.com/v1/messages

Headers:
x-api-key: ${CLAUDE_API_KEY}
anthropic-version: 2023-06-01

Body:
{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 200,
  "messages": [{
    "role": "user",
    "content": "The client said: '${messageText}'\n\nDoes this contain an Instagram handle? Does it contain a website? Respond with ONLY: INSTAGRAM:@handle or WEBSITE:url.com or BOTH or NEITHER"
  }]
}
```

### 7b-3: Extract Claude's Response

**Type:** Set

```javascript
claudeResponse = $previous.content[0].text

instagram = claudeResponse.includes("INSTAGRAM") ? 
  claudeResponse.match(/@[\w.]+/)[0] : 
  extractedInstagram

website = claudeResponse.includes("WEBSITE") ? 
  claudeResponse.match(/https?:\/\/[^\s]+|[\w.-]+\.[a-z]{2,}/)[0] : 
  extractedWebsite
```

### 7b-4: Build Response Message

**Type:** Set

```javascript
if(instagram && website) {
  responseMsg = `Perfect! 🎯\n\nInstagram: ${instagram}\nWebsite: ${website}\n\nGreat! Now let's talk about your goals. When would you like to have a quick call? 📞`
  moveToStage = "INFO"
} else if(instagram) {
  responseMsg = `Got your Instagram: ${instagram} ✅\n\nNow, what's your website or business URL?`
  moveToStage = "VIDEO" // Stay in same stage
} else if(website) {
  responseMsg = `Got your website: ${website} ✅\n\nWhat's your Instagram handle? (e.g., @yourname)`
  moveToStage = "VIDEO" // Stay in same stage
} else {
  responseMsg = `Sorry, I didn't catch that! 😅\n\nPlease share your Instagram handle or website. For example:\n@yourbusiness or www.yourbusiness.com`
  moveToStage = "VIDEO" // Stay in same stage
}
```

### 7b-5: Send Response

**Type:** HTTP Request (WhatsApp API)

```
Body:
{
  "messaging_product": "whatsapp",
  "to": "${clientPhone}",
  "type": "text",
  "text": {
    "body": "${responseMsg}"
  }
}
```

### 7b-6: Update Client

**Type:** Airtable

```
Action: Update record

Fields:
- Stage: ${moveToStage}
- Instagram Profile: ${instagram || ""}
- Website: ${website || ""}
- Last Message: ${messageText}
- Updated At: ${new Date().toISOString()}
```

**Then → Go to NODE 8 (Log Message)**

---

## 📅 **NODE 7c: STAGE 3 - BOOKING OPTIONS**

**Name:** Offer Booking

**Type:** Group of nodes

### 7c-1: Ask Booking Type

**Type:** HTTP Request (WhatsApp API)

```
Body:
{
  "messaging_product": "whatsapp",
  "to": "${clientPhone}",
  "type": "text",
  "text": {
    "body": "Perfect! Ready to chat? 📅\n\nHow would you prefer to meet?\n\n1️⃣ Online Meeting (via Zoom/Teams)\n2️⃣ In-person at our office\n3️⃣ At your location\n\nJust reply with 1, 2, or 3!"
  }
}
```

### 7c-2: Parse Response

**Type:** Set

```javascript
choice = messageText.trim()

if(choice === "1") {
  meetingType = "ONLINE"
  response = `Great! Let's do an online meeting. 🎥\n\nClick here to book: https://calendly.com/actlocal`
} else if(choice === "2") {
  meetingType = "OFFLINE"
  response = `Perfect! We'd love to meet in person. 📍\n\nOur office:\n${OFFICE_ADDRESS}\n\nWhat time works for you?`
} else if(choice === "3") {
  meetingType = "OFFLINE"
  response = `Got it! We can meet at your location. 📍\n\nWhat's your address or nearest area?`
} else {
  meetingType = null
  response = `I didn't catch that! Please reply:\n1️⃣ Online\n2️⃣ Our office\n3️⃣ Your location`
}
```

### 7c-3: Send Response

**Type:** HTTP Request (WhatsApp API)

```
Body:
{
  "messaging_product": "whatsapp",
  "to": "${clientPhone}",
  "type": "text",
  "text": {
    "body": "${response}"
  }
}
```

### 7c-4: Update Client

**Type:** Airtable

```
Fields:
- Stage: BOOKING
- Meeting Type: ${meetingType}
- Last Message: ${messageText}
- Updated At: ${new Date().toISOString()}
```

**Then → Go to NODE 8 (Log Message)**

---

## 📍 **NODE 7d: STAGE 4 - LOCATION HANDLING**

**Name:** Handle Location (Online/Offline)

**Type:** Group of nodes

### 7d-1: Check Meeting Type

**Type:** Switch

```
Condition 1: Meeting Type = "ONLINE"
  → Go to NODE 7d-2a (Send Calendar Link)

Condition 2: Meeting Type = "OFFLINE"
  → Go to NODE 7d-2b (Send Our Location + Ask for Theirs)
```

### 7d-2a: ONLINE MEETING

**Name:** Send Calendar Link

**Type:** HTTP Request (WhatsApp API)

```
Body:
{
  "messaging_product": "whatsapp",
  "to": "${clientPhone}",
  "type": "text",
  "text": {
    "body": "📅 Book your free consultation:\n\nhttps://calendly.com/actlocal\n\nPick your preferred time and we'll meet on Zoom! 🎥"
  }
}
```

### 7d-2b: OFFLINE MEETING

**Name:** Send Our Location + Ask for Theirs

**Type:** HTTP Request (WhatsApp API)

**First, send our location:**

```
Body:
{
  "messaging_product": "whatsapp",
  "to": "${clientPhone}",
  "type": "location",
  "location": {
    "latitude": ${OFFICE_LAT},
    "longitude": ${OFFICE_LNG},
    "name": "Act Local Office",
    "address": "${OFFICE_ADDRESS}"
  }
}
```

### 7d-3: Wait 2 Seconds

**Type:** Wait

```
Time: 2 seconds
```

### 7d-4: Ask for Their Location

**Type:** HTTP Request (WhatsApp API)

```
Body:
{
  "messaging_product": "whatsapp",
  "to": "${clientPhone}",
  "type": "text",
  "text": {
    "body": "☝️ That's our office location! 📍\n\nNow, can you share your location so we know where to meet you? (Use the attachment button → Location)"
  }
}
```

### 7d-5: Wait for Location (This happens in next message cycle)

When client sends their location, it will be processed in the next webhook call:

```javascript
// In NODE 2, detect location type:
messageType = $json.entry[0].changes[0].value.messages[0].type

if(messageType === "location") {
  theirLat = $json.entry[0].changes[0].value.messages[0].location.latitude
  theirLng = $json.entry[0].changes[0].value.messages[0].location.longitude
  theirLocationName = $json.entry[0].changes[0].value.messages[0].location.name
}
```

### 7d-6: Update Client with Location

**Type:** Airtable

```
Fields:
- Stage: FOLLOW
- Booking Confirmed: true
- Their Location: ${theirLocationName}
- Their Latitude: ${theirLat}
- Their Longitude: ${theirLng}
- Our Location Shared: true
- Last Message: ${messageText}
- Updated At: ${new Date().toISOString()}
```

**Then → Go to NODE 8 (Log Message)**

---

## 📧 **NODE 7e: STAGE 5 - AUTO FOLLOW-UPS**

**Name:** Send Follow-up (This is for manual/triggered follow-ups)

**Type:** HTTP Request (WhatsApp API)

### Check Follow-up Count

**Type:** Set

```javascript
followupCount = followupsSentCount || 0

if(followupCount === 0) {
  followupMsg = `Hi ${clientName}! 👋\n\nJust checking in—are you ready to get started with Act Local? We're excited to help you grow! 🚀`
  newCount = 1
} else if(followupCount === 1) {
  followupMsg = `${clientName}, this is our last message! ⏰\n\nDon't miss out on this opportunity. Reply NOW and let's transform your business! 💪`
  newCount = 2
} else {
  followupMsg = null
  newCount = 2
}
```

### Send Follow-up

**Type:** HTTP Request (WhatsApp API)

```
Body:
{
  "messaging_product": "whatsapp",
  "to": "${clientPhone}",
  "type": "text",
  "text": {
    "body": "${followupMsg}"
  }
}
```

### Update Follow-up Count

**Type:** Airtable

```
Fields:
- Follow-ups Sent Count: ${newCount}
- Updated At: ${new Date().toISOString()}

If newCount = 2:
- Stage: DONE
```

---

## 📝 **NODE 8: LOG MESSAGE TO DATABASE**

**Name:** Log Interaction

**Type:** Airtable

**Configuration:**

```
Action: Create record
Base: ${AIRTABLE_BASE_ID}
Table: Messages Log

Fields:
- Phone: ${clientPhone}
- Direction: INBOUND (if message from client) or OUTBOUND (if we sent)
- Message Type: TEXT / VIDEO / LOCATION
- Content: ${messageText}
- Intent: [detected by Claude if needed]
- Created At: ${new Date().toISOString()}
- Response Type: [what we sent back]
```

---

## ⏰ **PHASE 3: AUTO FOLLOW-UP WORKFLOW (Cron-based)**

### Step 5: Create Separate Workflow "WhatsApp Auto Follow-ups"

This workflow runs at **10:00 and 14:00** daily and sends follow-ups.

```
[1. Cron Trigger: 10:00 & 14:00]
    ↓
[2. Query Clients in FOLLOW Stage]
    ↓
[3. For Each Client: Check Follow-up Count]
    ↓
[4. Generate Follow-up Message (1st or 2nd)]
    ↓
[5. Send via WhatsApp]
    ↓
[6. Update Follow-up Count + Stage]
    ↓
[7. Log Follow-up in Messages Log]
```

### NODE 1: Cron Trigger

**Type:** Cron

```
Name: Daily Follow-ups Trigger
Trigger: Every day
Times: 10:00, 14:00
Cron: 0 10,14 * * *
Timezone: Asia/Dubai
```

### NODE 2: Query Pending Clients

**Type:** Airtable

```
Action: Read
Table: Clients

Filter:
- Stage = FOLLOW
- Follow-ups Sent Count < 2

This gets all clients who need follow-ups.
```

### NODE 3: Loop Through Clients

**Type:** Loop (For Each)

```
Iterate: Over query results
Max: 50 clients per run
```

### NODE 4: Inside Loop - Generate Message

**Type:** Set

```javascript
followupCount = $item.json["Follow-ups Sent Count"] || 0

if(followupCount === 0) {
  msg = `Hi ${$item.json.Name}! 👋\n\nJust following up—are you ready to get started with Act Local? We're excited to help! 🚀`
} else {
  msg = `${$item.json.Name}, this is our FINAL message! ⏰\n\nDon't miss this opportunity. Reply NOW! 💪`
}
```

### NODE 5: Send Follow-up

**Type:** HTTP Request (WhatsApp API)

```
Method: POST
URL: https://graph.instagram.com/v18.0/${phoneNumberId}/messages

Body:
{
  "messaging_product": "whatsapp",
  "to": "${$item.json.Phone}",
  "type": "text",
  "text": {
    "body": "${msg}"
  }
}
```

### NODE 6: Update Client

**Type:** Airtable

```
Action: Update record
Record ID: ${$item.json.id}

Fields:
- Follow-ups Sent Count: ${followupCount + 1}
- Updated At: ${new Date().toISOString()}

If Follow-ups Sent Count reaches 2:
- Stage: DONE
```

### NODE 7: Log Follow-up

**Type:** Airtable

```
Action: Create record
Table: Messages Log

Fields:
- Phone: ${$item.json.Phone}
- Direction: OUTBOUND
- Message Type: TEXT
- Content: ${msg}
- Response Type: follow_up_${followupCount + 1}
- Created At: ${new Date().toISOString()}
```

---

## 🎯 COMPLETE SETUP CHECKLIST

### Pre-Build Checklist
- [ ] Airtable base created with 3 tables
- [ ] Airtable tokens + Base ID saved
- [ ] Claude API key obtained
- [ ] WhatsApp Business API token obtained
- [ ] Phone number ID from Meta
- [ ] Videos uploaded to CDN (get URLs)
- [ ] Office location details ready
- [ ] Calendly link or calendar booking system ready

### N8N Setup
- [ ] All environment variables added
- [ ] N8N credentials saved
- [ ] Test webhook connection works

### Build Main Workflow
- [ ] NODE 1: Webhook created & registered with Meta
- [ ] NODE 2: Extract message data
- [ ] NODE 3: Lookup client in Airtable
- [ ] NODE 4: Check if new or existing
- [ ] NODE 4b: Create new client if needed
- [ ] NODE 5: Get client details
- [ ] NODE 6: Route by stage
- [ ] NODE 7a: Intro video handler
- [ ] NODE 7b: Instagram/website capture
- [ ] NODE 7c: Booking options
- [ ] NODE 7d: Location handling
- [ ] NODE 7e: Follow-up message
- [ ] NODE 8: Log to database
- [ ] Test end-to-end with 1 test user

### Build Follow-up Workflow
- [ ] Cron trigger configured (10:00 & 14:00)
- [ ] Query pending clients
- [ ] Loop + send logic
- [ ] Update + log
- [ ] Test one manual run

### Live Deployment
- [ ] Both workflows activated
- [ ] Error notifications set up
- [ ] Monitor first 24 hours
- [ ] Train team on system

---

## 🧪 TESTING GUIDE

### Test Scenario 1: New Client (Full Flow)

```
Day 1, 10:00 AM:
- Send: "Hi"
- Expected: Intro video + ask for Instagram
- Bot Stage: NEW → VIDEO

Day 1, 10:30 AM:
- Send: "@mybusiness"
- Expected: Ask for website
- Bot Stage: VIDEO (still waiting for website)

Day 1, 11:00 AM:
- Send: "www.mybusiness.com"
- Expected: "Great! Now let's talk about booking"
- Bot Stage: VIDEO → INFO

Day 1, 11:30 AM:
- Send: "Tell me more about your services"
- Expected: Services video
- Bot Stage: INFO

Day 1, 2:00 PM:
- Send: "1" (online meeting)
- Expected: "Book here: calendly.com/actlocal"
- Bot Stage: INFO → BOOKING → FOLLOW

Day 2, 10:00 AM:
- Cron trigger fires
- Expected: "Just following up..." message
- Bot Stage: FOLLOW (Follow-ups count: 1)

Day 3, 10:00 AM:
- Cron trigger fires
- Expected: "Final message!" message
- Bot Stage: FOLLOW → DONE (Follow-ups count: 2)
```

### Test Scenario 2: Repeat Client (Should Remember State)

```
Day 5, 2:00 PM:
- Same client sends: "Hi again!"
- Bot looks up phone in Airtable
- Finds: Stage = DONE, Instagram = @mybusiness, Website = www.mybusiness.com
- Expected: Smart response (not restart flow)
- Example: "Hey again! Ready to move forward?" or "How can we help next?"
```

### Test Scenario 3: Offline Meeting

```
Day 1:
- Send: "Hi"
- Expected: Intro video

Day 1:
- Send: "@business"
- Send: "www.business.com"

Day 1:
- Send: "2" (in-person at your office)
- Expected: Map location of office + "Share your location"

Day 1:
- Share live location
- Expected: "Perfect! Here's our meeting time..."
- Bot Stage: BOOKING → FOLLOW
```

---

## 📊 MONITORING & MAINTENANCE

### Daily Check
- [ ] Number of messages processed
- [ ] New clients vs repeat clients
- [ ] Most common stages (where are people dropping off?)
- [ ] Follow-up delivery success rate

### Weekly Check
- [ ] Update videos if needed
- [ ] Review client feedback
- [ ] Adjust responses based on common questions
- [ ] Check database size (clean old logs if needed)

### Monthly Check
- [ ] Success rate (NEW → DONE)
- [ ] Booking confirmation rate
- [ ] Cost of API calls (Claude + WhatsApp)
- [ ] Optimization opportunities

---

## 💰 COST ESTIMATE

**Per 100 conversations:**
- WhatsApp messages: ~50 outbound × $0.05 = $2.50
- Claude API: 100 messages × 300 tokens avg × $0.003 per 1M = $0.09
- Airtable: Free tier (up to 1,200 records)
- N8N: Free tier (up to 5M executions/month)

**Total: ~$2.60 per 100 conversations**

---

## 🚀 NEXT STEPS

1. **Create Airtable base** (15 min)
2. **Get all API credentials** (ask Mujib/Tanveer) (30 min)
3. **Upload videos** (15 min)
4. **Build main workflow** (2-3 hours)
5. **Build follow-up workflow** (1 hour)
6. **Test end-to-end** (1 hour)
7. **Deploy to production** (30 min)

**Total: ~5-6 hours to full working chatbot**

---

**Built by:** Lina, Act Local Operations
**For:** Doniya, Junior AI Ops
**Created:** March 28, 2026
**Status:** Complete build guide, ready to implement
**Last Updated:** March 28, 2026
