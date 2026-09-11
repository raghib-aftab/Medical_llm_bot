# Appointment Booking AI Agent and Medical LLM Chatbot



### Core Features
- **User Authentication**: Secure login and signup with email/password
- **Email OTP Verification**: New users must verify email with 6-digit OTP before account creation
- **Forgot Password**: Password reset via email with auto-generated secure password
- **JWT Token Authentication**: Secure API access with JSON Web Tokens
- **Password Encryption**: Passwords hashed using bcrypt
- **AI UI Interface**: Clean, modern chat interface with responsive design
- **User-Specific Chat History**: Each user sees only their own conversations
- **Context-Aware Conversations**: Maintains context by sending last 3 messages to the LLM
- **MongoDB Integration**: Persistent storage for users, chats, and messages
- **Real-time Responses**: Typing indicators and auto-scroll to latest messages
- **Chat Management**: Create, view, and delete chat conversations
- **Email Notifications**: Automatic email alerts for appointment booking and cancellation

### 🆕 AI Assistant Actions
The AI assistant can now perform actions through natural conversation:

- **🩺 Medical Advice**: Get accurate, evidence-based medical information
- **👨‍⚕️ Find Doctors**: Search and filter doctors by specialization
- **🏥 Find Hospitals**: Locate hospitals by city, specialization, or emergency services
- **📅 Book Appointments**: Schedule medical appointments with doctors (with email confirmation)
- **📋 View Appointments**: Check your appointment history and upcoming bookings
- **🔐 Change Password**: Update your account password securely
- **📧 Email Notifications**: Receive confirmation emails for bookings and cancellations

**Example conversations:**
- "Show me cardiologists" → Lists all cardiology specialists
- "Book an appointment with Dr. Sarah Johnson for next Monday at 2 PM" → Books the appointment
- "What are my appointments?" → Shows your appointment history
- "Change my password" → Guides you through password update
- "Show hospitals in Mumbai with emergency services" → Filtered hospital list



## Tech Stack

- **Frontend**: React.js with Vite, React Router
- **Backend**: Python FastAPI
- **Database**: MongoDB
- **Authentication**: JWT tokens, bcrypt password hashing
- **Email Service**: Gmail SMTP for OTP verification and notifications
- **LLM API**: Custom medical LLM endpoint

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **MongoDB** (v4.4 or higher)
- **npm** or **yarn** package manager

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Rishabh9559/medical_llm_UI.git
cd medical_llm_UI
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cp .env
```

Edit the `.env` file with your configuration:

```env
MONGODB_URL=mongodb://localhost:27017  # Or use MongoDB Atlas connection string
DATABASE_NAME=medical_llm_db
LLM_API_URL=your-llm-api-url-here
LLM_API_KEY=your-api-key-here
LLM_MODEL=your-model-name-here

# JWT Settings (IMPORTANT: Change SECRET_KEY in production!)
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Email Settings (Gmail SMTP)
GMAIL_USER=your-email@gmail.com
GMAIL_PASS=your-app-password
```

**Note for Gmail Setup:**
1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password: Google Account → Security → 2-Step Verification → App passwords
3. Use the 16-character app password (without spaces) as `GMAIL_PASS`

**Note:** You can use either a local MongoDB instance or MongoDB Atlas. For MongoDB Atlas, use a connection string like:
```
mongodb+srv://username:password@cluster.mongodb.net/?appName=YourApp
```

#### Start MongoDB (if using local MongoDB)

If using a local MongoDB instance, make sure it's running:

```bash
# For macOS with Homebrew
brew services start mongodb-community

# For Linux with systemd
sudo systemctl start mongod

# Or run MongoDB directly
mongod --dbpath /path/to/your/data/directory
```

#### Run the Backend

```bash
python main.py
```

The backend server will start at `http://localhost:8000`

### 3. Frontend Setup

#### Install Node Dependencies

```bash
cd ../frontend
npm install
```

#### Configure Environment Variables

Create a `.env` file in the `frontend` directory:

```bash
cp .env
```

Edit the `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

#### Run the Frontend

```bash
npm run dev
```

The frontend development server will start at `http://localhost:5173`

## Usage

### Getting Started

1. **Access the Application**: Open your browser and navigate to `http://localhost:5173`

### Account Registration (with Email Verification)

1. Click "Sign up" on the login page
2. Fill in your name, email, phone (optional), and password
3. Click "Send OTP" - a 6-digit code will be sent to your email
4. Enter the OTP from your email (valid for 5 minutes)
5. Click "Verify & Create Account" to complete registration

### Forgot Password

1. Click "Forgot Password?" on the login page
2. Enter your registered email address
3. Click "Send New Password"
4. Check your email for the new temporary password
5. Login with the new password (recommended: change it after login)

### Using the Chat

1. **Create a New Chat**: Click the "+ New Chat" button in the sidebar

2. **Send Messages**: Type your medical question in the input field and press Enter or click the send button

3. **View Chat History**: All your previous conversations are listed in the sidebar with timestamps

4. **Switch Conversations**: Click on any chat in the sidebar to view and continue that conversation

5. **Delete Chats**: Hover over a chat in the sidebar and click the "×" button to delete it

### Booking Appointments

1. Ask the AI to find doctors: "Show me cardiologists"
2. Book an appointment: "Book appointment with Dr. Smith for Monday at 2 PM"
3. You'll receive a confirmation email with appointment details
4. View your appointments: "Show my appointments"
5. Cancel if needed - you'll receive a cancellation email

## API Endpoints

The backend provides the following REST API endpoints:

### Authentication

- `POST /api/auth/send-otp` - Send OTP for email verification (Step 1 of signup)
  - Request body: `{"email": "user@example.com", "password": "password", "name": "User Name", "phone": "optional"}`
  - Response: `{"message": "OTP sent successfully to your email"}`

- `POST /api/auth/verify-otp` - Verify OTP and complete registration (Step 2 of signup)
  - Request body: `{"email": "user@example.com", "otp": "123456"}`
  - Response: `{"access_token": "jwt_token", "token_type": "bearer", "user": {...}}`

- `POST /api/auth/signup` - Direct signup without OTP (legacy)
  - Request body: `{"email": "user@example.com", "password": "password", "name": "User Name"}`
  - Response: `{"access_token": "jwt_token", "token_type": "bearer", "user": {...}}`

- `POST /api/auth/login` - Login user
  - Request body: `{"email": "user@example.com", "password": "password"}`
  - Response: `{"access_token": "jwt_token", "token_type": "bearer", "user": {...}}`

- `POST /api/auth/forgot-password` - Send new password to email
  - Request body: `{"email": "user@example.com"}`
  - Response: `{"message": "If the email exists, a new password has been sent"}`

- `GET /api/auth/me` - Get current user info (requires authentication)
  - Response: User object

### Chats (All endpoints require authentication)

- `POST /api/chats` - Create a new chat
  - Response: Chat object with `id`, `title`, `created_at`, `updated_at`, `messages`

- `GET /api/chats` - Get all chats for current user (for sidebar)
  - Response: Array of chat objects without messages

- `GET /api/chats/{chat_id}` - Get a specific chat with all messages
  - Response: Chat object with all messages

- `DELETE /api/chats/{chat_id}` - Delete a chat
  - Response: Success message

### Messages (Requires authentication)

- `POST /api/chats/{chat_id}/messages` - Send a message and get LLM response
  - Request body: `{"content": "your message"}`
  - Response: Assistant's message object

## Project Structure

```
medical_llm_UI/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── requirements.txt     # Python dependencies
│   ├── config.py            # Configuration (DB, API keys, JWT, Email)
│   ├── models/
│   │   ├── chat.py          # Chat Pydantic models
│   │   ├── user.py          # User Pydantic models (includes OTP models)
│   │   ├── appointment.py   # Appointment Pydantic models
│   │   ├── doctor.py        # Doctor Pydantic models
│   │   └── hospital.py      # Hospital Pydantic models
│   ├── routes/
│   │   ├── auth.py          # Authentication routes (login, signup, OTP, forgot password)
│   │   ├── chat.py          # Chat API routes
│   │   ├── appointments.py  # Appointment management routes
│   │   ├── hospitals.py     # Hospital listing routes
│   │   └── profile.py       # User profile routes
│   ├── services/
│   │   ├── auth_service.py  # JWT & password utilities
│   │   ├── llm_service.py   # LLM API integration
│   │   ├── db_service.py    # MongoDB operations
│   │   ├── email_service.py # Email sending (OTP, notifications)
│   │   └── tools_service.py # AI tool integrations
│   └── .env.example         # Environment variables template
├── frontend/
│   ├── package.json
│   ├── public/
│   ├── src/
│   │   ├── App.jsx          # Main application component
│   │   ├── main.jsx         # Application entry point
│   │   ├── components/
│   │   │   ├── Sidebar.jsx       # Chat history sidebar
│   │   │   ├── ChatArea.jsx      # Main chat area
│   │   │   ├── MessageList.jsx   # List of messages
│   │   │   ├── MessageInput.jsx  # Input field
│   │   │   ├── ChatItem.jsx      # Individual chat in sidebar
│   │   │   ├── Login.jsx         # Login with forgot password
│   │   │   ├── Signup.jsx        # Signup with OTP verification
│   │   │   ├── BookAppointment.jsx    # Appointment booking
│   │   │   └── AppointmentHistory.jsx # View appointments
│   │   ├── services/
│   │   │   └── api.js            # API calls to backend
│   │   └── styles/
│   │       └── *.css             # Component styles
│   └── .env.example
└── README.md
```

## Key Implementation Details

### Context-Aware Conversations

The application maintains conversation context by:
1. Storing all messages in MongoDB
2. When sending a new message, retrieving the last 4 messages from the conversation
3. Sending these messages along with the system prompt and new user message to the LLM
4. This allows the LLM to provide contextually relevant responses

### Auto-generated Chat Titles

- When a new chat is created, it starts with the title "New Chat"
- After the first user message, the title is automatically updated to the first 50 characters of that message
- This provides meaningful identification for each conversation

### Email OTP Verification

The signup flow uses email verification:
1. User submits registration form with email, password, name
2. Backend generates 6-digit OTP and stores it with 5-minute expiry
3. OTP is sent to user's email via Gmail SMTP
4. User enters OTP on verification screen
5. If OTP matches, account is created and user is logged in

### Email Notifications

Automatic email notifications are sent for:
- **Appointment Booking**: Confirmation email with all appointment details
- **Appointment Cancellation**: Notification email when appointment is cancelled
- **Password Reset**: New auto-generated password sent to email



## Development

### Backend Development

The backend uses FastAPI with hot-reload enabled. Any changes to Python files will automatically restart the server.

### Frontend Development

The frontend uses Vite's hot module replacement (HMR). Changes to React components will be reflected immediately without full page reload.

## Troubleshooting

### MongoDB Connection Issues

If you can't connect to MongoDB:
1. Ensure MongoDB is running: `mongod --version`
2. Check the connection string in your `.env` file
3. Verify MongoDB is listening on the correct port (default: 27017)

### CORS Errors

If you encounter CORS errors:
1. Ensure the backend is running on port 8000
2. Check that the frontend's `VITE_API_URL` matches the backend URL
3. Verify CORS middleware is properly configured in `backend/main.py`

### LLM API Errors

If the LLM doesn't respond:
1. Verify the API URL and API key in `backend/.env`
2. Check your network connection
3. Look at backend console logs for detailed error messages

### Email Sending Issues

If emails are not being sent:
1. Verify `GMAIL_USER` and `GMAIL_PASS` in `backend/.env`
2. Ensure you're using an App Password, not your regular Gmail password
3. Check that 2-Factor Authentication is enabled on your Google account
4. Verify Gmail hasn't blocked the sign-in attempt (check security alerts)
5. Check backend console for SMTP error messages

To generate a Gmail App Password:
1. Go to Google Account → Security → 2-Step Verification
2. Scroll to "App passwords" at the bottom
3. Select "Mail" and your device, then click "Generate"
4. Use the 16-character password (without spaces)

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the GitHub repository.
