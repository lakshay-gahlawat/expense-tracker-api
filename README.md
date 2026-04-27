# 💰 Expense Tracker API

A production-ready REST API built with **FastAPI**, **SQLAlchemy**, and **SQLite**.

## Features
- JWT Authentication (register, login, protected routes)
- Accounts management (multiple accounts per user)
- Transactions (income & expense) with filters, search, pagination
- Analytics: summaries, category breakdowns, monthly trends
- Full test suite with pytest

## Quick Start

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
copy .env.example .env        # Windows
cp .env.example .env          # Mac/Linux
# Then edit .env and set a strong SECRET_KEY

# 4. Run the server
uvicorn app.main:app --reload

# 5. Open API docs
# http://127.0.0.1:8000/docs
```

## Running Tests

```bash
pytest app/tests/ -v
```

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /users/register | Register a new user |
| POST | /users/login | Login and get JWT token |
| GET | /users/me | Get current user profile |

### Accounts
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /accounts/ | Create account |
| GET | /accounts/ | List accounts (paginated) |
| GET | /accounts/{id} | Get account |
| PATCH | /accounts/{id} | Update account |
| DELETE | /accounts/{id} | Delete account |
| GET | /accounts/summary/{id} | Income/expense balance for one account |

### Transactions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /transactions/ | Create transaction |
| GET | /transactions/ | List with filters + search + pagination |
| GET | /transactions/{id} | Get transaction |
| PATCH | /transactions/{id} | Update transaction |
| DELETE | /transactions/{id} | Delete transaction |
| GET | /transactions/summary | Overall income/expense/balance |
| GET | /transactions/categories | Breakdown by category |
| GET | /transactions/trends/{year} | Monthly income vs expense |
