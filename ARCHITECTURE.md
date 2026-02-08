# Dashboard Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         READING ASSISTANT APPLICATION                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  FRONTEND (React, localhost:3001)            BACKEND (Flask, localhost:5000)│
│  ┌──────────────────────────────┐           ┌──────────────────────────────┐
│  │   Browser/React Router       │           │      Flask Application       │
│  │                              │           │                              │
│  │  /signin ─────────────────────────────→ /api/auth/login               │
│  │  /signup ─────────────────────────────→ /api/auth/register            │
│  │                              │           │                              │
│  │  [Admin Check]               │           │   Email === admin@?          │
│  │   Yes: /admin                │           │   ↓ YES                      │
│  │   No:  /dashboard ───────────────────→ (no api call, frontend logic)  │
│  │                              │           │                              │
│  │  ┌─────────────────────────────────┐   │                              │
│  │  │  Dashboard (NEW COMPONENT)      │   │                              │
│  │  │                                 │   │                              │
│  │  │  [Upload PDF 📤] [Read Books 📖]  │   │                              │
│  │  │                                 │   │                              │
│  │  └─────────────────────────────────┘   │                              │
│  │         │                        │     │                              │
│  │         ↓                        ↓     │                              │
│  │     /upload              /books ──────────────────────────→ /api/history
│  │    (PdfUpload)          (ReadBooks)    │                              │
│  │         │                        │     │                              │
│  │   [Upload File]          [List PDFs]   │                              │
│  │         │                   │          │                              │
│  │         ↓                   ↓          │                              │
│  │    POST /api/pdf/         [Click PDF]  │                              │
│  │    upload-pdf ────────────────┐       │                              │
│  │         │                     │        │                              │
│  │         │              Creates state    │                              │
│  │         │              with PDF object  │                              │
│  │         │                     │        │                              │
│  │         │                     ↓        │                              │
│  │         │              navigate('/reader', │                          │
│  │         │              {state: {pdf}})    │                           │
│  │         │                     │        │                              │
│  │         │          useLocation Hook    │                              │
│  │         │          detects state       │                              │
│  │         ↓             │                │                              │
│  │    /reader ──────────→─────────────────────→ /api/pdf/load-pdf (NEW) │
│  │         │                     │        │                              │
│  │    [ReadingAssistant]   loadPdfFromHistory() │                       │
│  │    (pre-loaded mode)          │        │                              │
│  │         │                POST with  ────────→ Extract sentences       │
│  │         │                filename    │        Return in same format   │
│  │         ↓                     │      │        as /upload-pdf          │
│  │    Display sentences          ↓      │                              │
│  │    Practice pronunciation  render   │                              │
│  │                             reading  │                              │
│  │                             view     │                              │
│  │                                      │                              │
│  └──────────────────────────────────────┘                              │
│                                                                        │
│                           DATABASE (MongoDB)                           │
│                           ┌─────────────────┐                         │
│                           │  Collections:   │                         │
│                           ├─────────────────┤                         │
│                           │  - users        │                         │
│                           │  - history      │                         │
│                           │  - pdfs         │                         │
│                           └─────────────────┘                         │
│                                                                        │
│                           STORAGE (File System)                        │
│                           ┌─────────────────┐                         │
│                           │  /static/uploads/                         │
│                           │  - [uuid]_*.pdf │                         │
│                           │  - [uuid]_*.pdf │                         │
│                           └─────────────────┘                         │
│                                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
App
├── AuthProvider
│   ├── Router
│   │   ├── Route /signin
│   │   │   └── SignIn
│   │   │       └── login()
│   │   │
│   │   ├── Route /signup
│   │   │   └── SignUp
│   │   │       └── register()
│   │   │
│   │   ├── AdminRoute /admin
│   │   │   └── AdminDashboard
│   │   │       ├── User List Modal
│   │   │       └── Upload List Modal
│   │   │
│   │   ├── PrivateRoute /dashboard ⭐ NEW
│   │   │   └── Dashboard ⭐ NEW
│   │   │       ├── Upload PDF Card
│   │   │       │   └── onClick → navigate('/upload')
│   │   │       └── Read Books Card
│   │   │           └── onClick → navigate('/books')
│   │   │
│   │   ├── PrivateRoute /upload
│   │   │   └── ReadingAssistant
│   │   │       ├── PdfUpload
│   │   │       └── DocumentReader
│   │   │
│   │   ├── PrivateRoute /books ⭐ NEW
│   │   │   └── ReadBooks ⭐ NEW
│   │   │       ├── Back Button
│   │   │       ├── User Info
│   │   │       └── PDF History Grid
│   │   │           └── onClick → navigate('/reader', {state})
│   │   │
│   │   ├── PrivateRoute /reader
│   │   │   └── ReadingAssistant (pre-loaded)
│   │   │       ├── PdfUpload (hidden, pre-loaded)
│   │   │       └── DocumentReader
│   │   │
│   │   └── Fallback /* → /dashboard
│   │
│   ├── useAuth Hook
│   │   ├── user (object)
│   │   ├── token (JWT)
│   │   ├── loading (boolean)
│   │   ├── pdfHistory (array)
│   │   ├── login() → returns {success, user}
│   │   ├── register() → returns {success, user}
│   │   ├── logout()
│   │   ├── fetchHistory()
│   │   └── addToHistory()
│   │
│   └── Context State:
│       ├── user
│       ├── token
│       ├── loading
│       └── pdfHistory []

```

## Data Flow - Upload New PDF

```
User on Dashboard
   │
   ├─ Click "Upload PDF 📤"
   │
   ├─ navigate('/upload')
   │
   ├─ ReadingAssistant renders with currentView='upload'
   │     │
   │     ├─ PdfUpload component shown
   │     │
   │     ├─ User selects PDF file
   │     │
   │     ├─ handleFileUpload(file)
   │     │     │
   │     │     ├─ FormData with file
   │     │     │
   │     │     ├─ POST /api/pdf/upload-pdf
   │     │     │     │
   │     │     │     ├─ BACKEND: Save file with UUID
   │     │     │     ├─ BACKEND: Extract text with pdfplumber
   │     │     │     ├─ BACKEND: Split into sentences
   │     │     │     └─ BACKEND: Return {filename, sentences, pages, pdf_url}
   │     │     │
   │     │     ├─ setAllSentences(response.sentences)
   │     │     ├─ setPdfUrl(response.pdf_url)
   │     │     ├─ setCurrentView('reading')
   │     │     │
   │     │     └─ DocumentReader renders
   │     │
   │     └─ User practices pronunciation with feedback
   │
   └─ (Optional) Add PDF to history via POST /api/history
```

## Data Flow - Read Existing PDF

```
User on Dashboard
   │
   ├─ Click "Read Books 📖"
   │
   ├─ navigate('/books')
   │
   ├─ ReadBooks component renders
   │     │
   │     ├─ useEffect: fetchHistory()
   │     │     │
   │     │     └─ GET /api/history
   │     │         │
   │     │         ├─ BACKEND: Query MongoDB 'history' collection
   │     │         └─ BACKEND: Return [{pdf_name, pdf_path, created_at, ...}]
   │     │
   │     ├─ setPdfHistory(data.history)
   │     │
   │     ├─ Map pdfHistory to PDF cards grid
   │     │     │
   │     │     ├─ Card shows: filename, upload date, page count
   │     │     │
   │     │     └─ onClick handler: handleReadPdf(pdf)
   │     │
   │     └─ handleReadPdf(pdf)
   │         │
   │         ├─ navigate('/reader', {state: {pdf}})
   │         │     │
   │         │     └─ location.state.pdf = PDF object
   │         │
   │         └─ App.useEffect detects state change
   │             │
   │             ├─ loadPdfFromHistory(pdf)
   │             │     │
   │             │     ├─ POST /api/pdf/load-pdf with filename
   │             │     │     │
   │             │     │     ├─ BACKEND: Locate file in /uploads/
   │             │     │     ├─ BACKEND: Extract text with pdfplumber
   │             │     │     ├─ BACKEND: Split into sentences
   │             │     │     └─ BACKEND: Return {filename, sentences, pages, pdf_url}
   │             │     │
   │             │     ├─ setAllSentences(response.sentences)
   │             │     ├─ setPdfUrl(response.pdf_url)
   │             │     ├─ setCurrentView('reading')
   │             │     │
   │             │     └─ DocumentReader renders (pre-loaded)
   │             │
   │             └─ User resumes reading or starts practice
   │
   └─ User can logout or return to Dashboard
```

## Authentication Flow

```
┌─ Sign In/Sign Up Request ─┐
│                            │
▼                            ▼
POST /api/auth/login    POST /api/auth/register
│                            │
├─ Verify credentials        ├─ Check email exists
├─ Hash password match       ├─ Create new user
├─ Generate JWT token        ├─ Hash password
│                            ├─ Generate JWT token
▼                            ▼
Return {                Return {
  access_token,   OR     access_token,
  user: {name,          user: {name,
    email}              email}
}                     }
│                            │
└────────────┬───────────────┘
             │
             ▼
     AuthContext.setToken()
     AuthContext.setUser()
     localStorage.setToken()
             │
             ▼
     useAuth checks: user?.email === 'admin@example.com'
             │
        ┌────┴─────┐
        │YES        │NO
        ▼           ▼
    /admin   /dashboard (navigate)
   (AdminRoute)  (PrivateRoute)
        │           │
        ├───────────┼──────────→ Protected Routes Below:
        │           │              - /upload
        │           │              - /books
        │           │              - /reader
        │           │
        └───────────┘
             │
             ▼ (Any protected route access)
         ValidateToken
             │
        ┌────┴─────┐
        │Valid      │Expired
        ▼           ▼
      Show      logout()
      Content   redirect to /signin
```

## Database Schema (MongoDB)

```
users {
  _id: ObjectId
  name: string
  email: string (unique)
  password: string (hashed)
  created_at: datetime
}

history {
  _id: ObjectId
  user_id: ObjectId (ref to users)
  pdf_name: string
  pdf_path: string (filename with UUID)
  total_pages: number
  total_sentences: number
  file_size: number
  last_page: number (for resume)
  status: string ('in_progress', 'completed')
  created_at: datetime
  updated_at: datetime
}

uploads {
  _id: ObjectId
  user_id: ObjectId (ref to users)
  filename: string (original)
  stored_filename: string (with UUID)
  upload_date: datetime
  total_sentences: number
  total_pages: number
}
```

## Key API Endpoints

```
Authentication:
  POST   /api/auth/login           (email, password) → {token, user}
  POST   /api/auth/register        (name, email, password) → {token, user}
  GET    /api/auth/me              () → {user}

PDF Management:
  POST   /api/pdf/upload-pdf       (file) → {filename, sentences, pages, pdf_url}
  POST   /api/pdf/load-pdf (NEW)   (filename) → {sentences, pages, pdf_url}
  GET    /api/pdf/pdf-info         () → {has_pdf, stats}

History:
  GET    /api/history              () → {history: []}
  POST   /api/history              (data) → {history_id}
  DELETE /api/history/{id}         () → {success}

Admin (admin-only):
  GET    /api/admin/users          () → {users: []}
  GET    /api/admin/uploads        () → {uploads: []}

Practice/Speech:
  POST   /api/practice/evaluate-pronunciation  (audio, word) → {feedback, score}
```

---

*Diagram Created: December 2024*  
*Architecture v1.0 - Dashboard Feature Complete*
