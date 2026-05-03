# 💰 Expense Tracker API

A production-ready REST API for tracking personal expenses built with **FastAPI**, **SQLAlchemy**, and **SQLite**.

🔗 **Live API:** https://expense-tracker-api-vq60.onrender.com
📄 **Interactive Docs:** https://expense-tracker-api-vq60.onrender.com/docs

---

## ✨ Features

- 🔐 JWT Authentication (register, login, protected routes)
- 👤 User management with password strength validation
- 🏦 Multiple accounts per user
- 💸 Income & expense transactions with categories
- 🔍 Search, filter, sort and paginate transactions
- 📊 Analytics — summaries, category breakdowns, monthly trends
- ✅ 37 tests with pytest

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.12 | Programming language |
| FastAPI | Web framework |
| SQLAlchemy | ORM / Database layer |
| SQLite | Database |
| JWT (python-jose) | Authentication |
| Passlib + Bcrypt | Password hashing |
| Pytest | Testing |
| Render | Deployment |

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/lakshay-gahlawat/expense-tracker-api.git
cd expense-tracker-api

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
copy .env.example .env        # Windows
cp .env.example .env          # Mac/Linux
# Open .env and set a strong SECRET_KEY

# 5. Run the server
uvicorn app.main:app --reload

# 6. Open docs
# http://127.0.0.1:8000/docs
```

---

## 📡 API Examples

### Register a new user
```bash
curl -X POST https://expense-tracker-api-vq60.onrender.com/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "mypass123"}'
```
Response:
```json
{
  "id": "abc-123",
  "email": "user@example.com",
  "created_at": "2025-05-02T10:00:00"
}
```

### Login and get token
```bash
curl -X POST https://expense-tracker-api-vq60.onrender.com/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "mypass123"}'
```
Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "token_type": "bearer"
}
```

### Create a transaction
```bash
curl -X POST https://expense-tracker-api-vq60.onrender.com/transactions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "your-account-id",
    "amount": 500,
    "transaction_type": "expense",
    "category": "Food",
    "date": "2025-05-02T10:00:00"
  }'
```

### Get spending summary
```bash
curl https://expense-tracker-api-vq60.onrender.com/transactions/summary \
  -H "Authorization: Bearer YOUR_TOKEN"
```
Response:
```json
{
  "total_income": 50000.0,
  "total_expense": 12000.0,
  "balance": 38000.0,
  "from_date": null,
  "to_date": null
}
```

### Get category breakdown
```bash
curl "https://expense-tracker-api-vq60.onrender.com/transactions/categories?transaction_type=expense" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
Response:
```json
[
  {"category": "Food", "transaction_type": "expense", "total": 5000.0, "count": 10},
  {"category": "Rent", "transaction_type": "expense", "total": 7000.0, "count": 1}
]
```

---

## 📁 Project Structure

---

## 🔒 API Endpoints

### Users
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/users/register` | ❌ | Register new user |
| POST | `/users/login` | ❌ | Login and get JWT token |
| GET | `/users/me` | ✅ | Get current user profile |
| PATCH | `/users/{id}` | ✅ | Update user |
| DELETE | `/users/{id}` | ✅ | Delete user |

### Accounts
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/accounts/` | ✅ | Create account |
| GET | `/accounts/` | ✅ | List accounts (paginated) |
| GET | `/accounts/{id}` | ✅ | Get account |
| PATCH | `/accounts/{id}` | ✅ | Update account |
| DELETE | `/accounts/{id}` | ✅ | Delete account |
| GET | `/accounts/summary/{id}` | ✅ | Income/expense balance |

### Transactions
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/transactions/` | ✅ | Create transaction |
| GET | `/transactions/` | ✅ | List with filters + search |
| GET | `/transactions/{id}` | ✅ | Get transaction |
| PATCH | `/transactions/{id}` | ✅ | Update transaction |
| DELETE | `/transactions/{id}` | ✅ | Delete transaction |
| GET | `/transactions/summary` | ✅ | Overall income/expense/balance |
| GET | `/transactions/categories` | ✅ | Breakdown by category |
| GET | `/transactions/trends/{year}` | ✅ | Monthly income vs expense |

---

## 🧪 Running Tests

```bash
pytest app/tests/ -v
```

---

## 📬 Contact

**Lakshay Gahlawat**
[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:lakshaygahlawat65@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/lakshay-gahlawat)