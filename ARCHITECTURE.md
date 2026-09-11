# AI Chat Assistant - System Architecture

## Component Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                      (React Frontend)                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Chat Interface                         │  │
│  │  • Type message: "Show me cardiologists"                  │  │
│  │  • Send button clicked                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ POST /api/chats/{id}/messages
                              │ Authorization: Bearer {JWT}
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND API (FastAPI)                       │
│                     routes/chat.py                               │
│                                                                   │
│  1. Verify user authentication (JWT)                             │
│  2. Save user message to database                                │
│  3. Get recent messages for context                              │
│  4. Call LLM with tools enabled ──────────────────┐             │
│  5. Parse response for tool calls                 │             │
│  6. Execute tools if needed ──┐                   │             │
│  7. Format and return result  │                   │             │
└───────────────────────────────┼───────────────────┼─────────────┘
                                │                   │
                    ┌───────────┘                   │
                    │                               │
                    ▼                               ▼
    ┌──────────────────────────┐    ┌──────────────────────────┐
    │   TOOLS SERVICE          │    │    LLM SERVICE           │
    │ tools_service.py         │    │  llm_service.py          │
    │                          │    │                          │
    │ Available Tools:         │    │ • Sends messages to LLM  │
    │ • get_doctors            │    │ • Includes system prompt │
    │ • get_hospitals          │    │ • Includes tool docs     │
    │ • book_appointment       │    │ • Parses tool calls      │
    │ • change_password        │    │                          │
    │ • get_user_appointments  │    └──────────────────────────┘
    │                          │                   │
    └──────────────────────────┘                   │
                │                                  │
                │                                  │
                ▼                                  ▼
    ┌──────────────────────────┐    ┌──────────────────────────┐
    │   DATABASE SERVICE       │    │  EXTERNAL LLM API        │
    │   db_service.py          │    │  (OpenAI-compatible)     │
    │                          │    │                          │
    │ • Users collection       │    │ Model: Medical LLaMA     │
    │ • Chats collection       │    │ Trained by: Rishabh &    │
    │ • Appointments collection│    │             Reshma       │
    │ • Doctor data (static)   │    │                          │
    │ • Hospital data (static) │    └──────────────────────────┘
    │                          │
    └──────────────────────────┘
                │
                │
    ┌───────────┴────────────────────────────────┐
    │                                            │
    ▼                                            ▼
    ┌──────────────────────────┐    ┌──────────────────────────┐
    │      MONGODB             │    │    EMAIL SERVICE         │
    │                          │    │  email_service.py        │
    │ Collections:             │    │                          │
    │ • users                  │    │ • Gmail SMTP             │
    │ • chats                  │    │ • OTP Generation         │
    │ • appointments           │    │ • Signup verification    │
    └──────────────────────────┘    │ • Password reset         │
                                    │ • Appointment emails     │
                                    └──────────────────────────┘
```

## Interaction Flow Example

### Scenario: User asks "Show me cardiologists"

```
1. USER ACTION
   ├─ User types: "Show me cardiologists"
   └─ Clicks send button

2. FRONTEND (MedicalChat.jsx)
   ├─ Captures message
   ├─ Displays user message in chat
   ├─ Shows "AI is thinking..." indicator
   └─ Sends POST to /api/chats/{chatId}/messages

3. BACKEND (chat.py)
   ├─ Authenticates user via JWT
   ├─ Saves user message to MongoDB
   ├─ Retrieves last 4 messages for context
   └─ Calls llm_service.get_completion(messages, tools_available=True)

4. LLM SERVICE (llm_service.py)
   ├─ Builds system prompt with tool instructions
   ├─ Formats conversation history
   ├─ Sends to external LLM API
   ├─ Receives response:
   │  "I can help you find cardiologists. 
   │   TOOL_CALL: {"name": "get_doctors", "parameters": {"specialization": "Cardiology"}}"
   └─ Returns response to chat.py

5. CHAT ROUTE (chat.py)
   ├─ Calls llm_service.parse_tool_call()
   ├─ Detects tool call: get_doctors with specialization="Cardiology"
   ├─ Calls tools_service.execute_tool("get_doctors", {...}, user_id)
   └─ Formats result

6. TOOLS SERVICE (tools_service.py)
   ├─ Executes _get_doctors() method
   ├─ Filters DOCTORS_DATA by specialization
   ├─ Returns: {success: true, data: [...doctors...], count: 3}
   └─ Returns to chat.py

7. CHAT ROUTE (chat.py)
   ├─ Formats doctor list for display:
   │  "Here are the available doctors:
   │   
   │   **Dr. Sarah Johnson** - Cardiology
   │     Experience: 15 years
   │     Availability: Mon-Fri, 9:00 AM - 5:00 PM
   │     Fee: ₹1500
   │   ..."
   ├─ Saves assistant message to MongoDB
   └─ Returns MessageResponse to frontend

8. FRONTEND (MedicalChat.jsx)
   ├─ Receives response
   ├─ Displays formatted message in chat
   ├─ Hides loading indicator
   └─ Scrolls to bottom
```

## Email Verification Flow (Signup)

```
1. USER ACTION
   ├─ User fills signup form (name, email, password)
   └─ Clicks "Send OTP" button

2. FRONTEND (Signup.jsx)
   ├─ Validates form data
   ├─ Sends POST to /api/auth/send-otp
   └─ Shows OTP input screen

3. BACKEND (auth.py)
   ├─ Checks if email already exists
   ├─ Generates 6-digit OTP
   ├─ Stores OTP with user data (5 min expiry)
   └─ Calls email_service.send_signup_otp()

4. EMAIL SERVICE (email_service.py)
   ├─ Builds HTML email template
   ├─ Connects to Gmail SMTP
   ├─ Sends OTP to user's email
   └─ Returns success/failure

5. USER ACTION
   ├─ User receives email
   └─ Enters 6-digit OTP

6. FRONTEND (Signup.jsx)
   └─ Sends POST to /api/auth/verify-otp

7. BACKEND (auth.py)
   ├─ Retrieves stored OTP and user data
   ├─ Validates OTP (checks expiry and match)
   ├─ Creates user in database
   ├─ Generates JWT token
   └─ Returns token + user to frontend

8. FRONTEND (Signup.jsx)
   ├─ Stores JWT in localStorage
   └─ Redirects to dashboard
```

## Forgot Password Flow

```
1. USER ACTION
   ├─ Clicks "Forgot Password?" on login page
   ├─ Enters email address
   └─ Clicks "Send New Password"

2. FRONTEND (Login.jsx)
   └─ Sends POST to /api/auth/forgot-password

3. BACKEND (auth.py)
   ├─ Looks up user by email
   ├─ Generates secure random password
   ├─ Hashes and updates password in DB
   └─ Calls email_service.send_password_reset()

4. EMAIL SERVICE (email_service.py)
   ├─ Builds password reset email
   ├─ Includes new temporary password
   └─ Sends via Gmail SMTP

5. USER ACTION
   ├─ Receives email with new password
   └─ Logs in with new password
```

## Appointment Email Notifications

```
BOOKING CONFIRMATION:
┌──────────────────────────────────────┐
│ User books appointment               │
│            │                         │
│            ▼                         │
│ Backend creates appointment in DB    │
│            │                         │
│            ▼                         │
│ BackgroundTasks.add_task(            │
│   email_service.send_appointment_    │
│   confirmation(...)                  │
│ )                                    │
│            │                         │
│            ▼                         │
│ Email sent with appointment details: │
│ • Doctor name & specialization       │
│ • Hospital name                      │
│ • Date & time                        │
│ • Confirmation status                │
└──────────────────────────────────────┘

CANCELLATION NOTIFICATION:
┌──────────────────────────────────────┐
│ User cancels appointment             │
│            │                         │
│            ▼                         │
│ Backend updates status to cancelled  │
│            │                         │
│            ▼                         │
│ BackgroundTasks.add_task(            │
│   email_service.send_appointment_    │
│   cancellation(...)                  │
│ )                                    │
│            │                         │
│            ▼                         │
│ Email sent with cancelled details    │
└──────────────────────────────────────┘
```

## Tool Execution Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    LLM DECISION TREE                          │
└──────────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  User Message         │
              └───────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Does this require     │
              │ an action?            │
              └───────────────────────┘
                     │         │
           ┌─────────┘         └─────────┐
           │ NO                           │ YES
           ▼                              ▼
┌──────────────────────┐    ┌──────────────────────────┐
│ Return normal text   │    │ Do I have all needed     │
│ response             │    │ information?             │
└──────────────────────┘    └──────────────────────────┘
                                     │         │
                           ┌─────────┘         └─────────┐
                           │ NO                           │ YES
                           ▼                              ▼
                ┌──────────────────────┐    ┌──────────────────────────┐
                │ Ask user for more    │    │ Output TOOL_CALL with    │
                │ details              │    │ name and parameters      │
                └──────────────────────┘    └──────────────────────────┘
                                                         │
                                                         ▼
                                            ┌──────────────────────────┐
                                            │ Backend executes tool    │
                                            │ and returns formatted    │
                                            │ result to user           │
                                            └──────────────────────────┘
```

## Security Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     SECURITY LAYERS                           │
└──────────────────────────────────────────────────────────────┘

1. AUTHENTICATION
   ├─ JWT tokens for API access
   ├─ Token verification on every request
   ├─ Tokens include user_id and email
   └─ Automatic token expiration

2. AUTHORIZATION
   ├─ Users can only access their own data
   ├─ Chat ownership verification
   ├─ Appointment user_id validation
   └─ Profile access restrictions

3. PASSWORD SECURITY
   ├─ bcrypt hashing (never store plain text)
   ├─ Current password verification before changes
   ├─ Minimum 6 character requirement
   ├─ Passwords not logged or exposed
   └─ Secure random password generation for reset

4. EMAIL VERIFICATION
   ├─ OTP required for new account creation
   ├─ 6-digit numeric OTP
   ├─ 5-minute expiry time
   ├─ In-memory storage (use Redis in production)
   └─ Single-use tokens (deleted after verification)

5. DATA ISOLATION
   ├─ MongoDB user-specific queries
   ├─ No cross-user data access
   └─ Tool execution in user context

6. INPUT VALIDATION
   ├─ Pydantic models for all inputs
   ├─ Type checking and validation
   ├─ Date/time format validation
   └─ Required field enforcement

7. EMAIL SECURITY
   ├─ Gmail App Passwords (not regular passwords)
   ├─ TLS/STARTTLS encryption for SMTP
   ├─ No sensitive data in email logs
   └─ Rate limiting recommended for production
```

## Database Schema

```
┌──────────────────────────────────────────────────────────────┐
│                      MONGODB COLLECTIONS                      │
└──────────────────────────────────────────────────────────────┘

USERS
├─ _id: ObjectId (auto)
├─ id: string (UUID)
├─ email: string (unique)
├─ name: string
├─ phone: string (optional)
├─ hashed_password: string
└─ created_at: datetime

CHATS
├─ _id: ObjectId (auto)
├─ id: string (UUID)
├─ title: string
├─ user_id: string (references users.id)
├─ created_at: datetime
└─ messages: array
    ├─ role: "user" | "assistant"
    ├─ content: string
    └─ timestamp: datetime

APPOINTMENTS
├─ _id: ObjectId (auto)
├─ id: string (UUID)
├─ user_id: string (references users.id)
├─ doctor_id: string
├─ doctor_name: string
├─ specialization: string
├─ appointment_date: string (YYYY-MM-DD)
├─ appointment_time: string (HH:MM)
├─ reason: string
├─ status: "scheduled" | "completed" | "cancelled"
└─ created_at: datetime
```

## Technology Stack Details

```
FRONTEND
├─ React 18
├─ React Router 6
├─ Vite (build tool)
├─ Axios (HTTP client)
└─ CSS Modules

BACKEND
├─ FastAPI
├─ Python 3.8+
├─ PyJWT (authentication)
├─ bcrypt (password hashing)
├─ httpx (LLM API client)
├─ Motor (async MongoDB driver)
└─ smtplib (email sending)

DATABASE
└─ MongoDB 4.4+

EXTERNAL SERVICES
├─ Medical LLaMA API (OpenAI-compatible)
└─ Gmail SMTP (email notifications)
```

---

**Architecture designed by**: Rishabh Kushwaha and Resham
**Last Updated**: February 2026
