# Email Sender

Professional bulk email sending platform with campaign management, analytics, and tracking.

## Features

- 📧 Bulk email campaigns with CSV upload
- 📊 Real-time analytics & tracking
- 📝 Rich text email editor with 150+ fonts
- 🎯 Dynamic personalization tags
- 📈 Campaign performance metrics
- 🔄 SMTP profile management
- 📱 Responsive modern UI

## Tech Stack

- **Frontend:** React + Vite + TailwindCSS
- **Backend:** FastAPI (Python)
- **Database:** SQLite

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python run.py
```

### Frontend Setup
```bash
npm install
npm run dev
```

## Production Deployment

### Free Hosting Options:
- **Railway** (Recommended)
- **Render**
- **Vercel** (Frontend) + **Railway** (Backend)

### Paid Options:
- **Hostinger VPS** (Ubuntu)
- **DigitalOcean**
- **AWS/GCP**

## License

MIT
