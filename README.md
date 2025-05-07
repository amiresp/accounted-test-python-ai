# Simple Accounting Web App

A lightweight accounting tool for non-technical users to manage accounts, customers, sales invoices, and financial reports.

## Features

- User Authentication
- Account Management
- Customer Management
- Sales Invoice Management
- Financial Reporting
- Backup & Restore functionality

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
.\venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend server:
```bash
python backend/app.py
```

### Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

## Project Structure

```
accounted-project/
├── backend/
│   ├── app.py
│   ├── models/
│   ├── routes/
│   └── utils/
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── requirements.txt
└── README.md
```

## Development

The application is built using:
- Backend: Python (Flask)
- Frontend: HTML, CSS (Tailwind), JavaScript
- Charts: Chart.js
- Authentication: Flask-Login 