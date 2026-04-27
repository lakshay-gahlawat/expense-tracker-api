from fastapi import HTTPException, status
from app.models.account import Account
from app.models.transaction import Transaction
from sqlalchemy import or_, func
from app.utils.pagination import paginate
from datetime import datetime


class TransactionService:
    def __init__(self, db):
        self.db = db

    def _get_owned_account(self, account_id, current_user):
        account = self.db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        if account.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        return account

    def create_transaction(self, trans_data, current_user):
        self._get_owned_account(trans_data.account_id, current_user)
        trans = Transaction(**trans_data.model_dump())
        self.db.add(trans)
        self.db.commit()
        self.db.refresh(trans)
        return trans

    def get_transactions(self, current_user, page, limit, filters, search, sort_by, order):
        query = self.db.query(Transaction).join(Account).filter(
            Account.user_id == current_user.id
        )

        if filters:
            if filters.get("min_amount"):
                query = query.filter(Transaction.amount >= float(filters["min_amount"]))
            if filters.get("max_amount"):
                query = query.filter(Transaction.amount <= float(filters["max_amount"]))
            if filters.get("transaction_type") in ["income", "expense"]:
                query = query.filter(Transaction.transaction_type == filters["transaction_type"])
            if filters.get("category"):
                query = query.filter(Transaction.category.ilike(f"%{filters['category']}%"))
            if filters.get("account_id"):
                query = query.filter(Transaction.account_id == filters["account_id"])
            if filters.get("from_date"):
                query = query.filter(Transaction.date >= datetime.fromisoformat(filters["from_date"]))
            if filters.get("to_date"):
                query = query.filter(Transaction.date <= datetime.fromisoformat(filters["to_date"]))

        if search:
            query = query.filter(
                or_(
                    Transaction.description.ilike(f"%{search}%"),
                    Transaction.category.ilike(f"%{search}%"),
                )
            )

        allowed_sort_fields = {
            "amount": Transaction.amount,
            "category": Transaction.category,
            "type": Transaction.transaction_type,
            "date": Transaction.date,
            "description": Transaction.description,
        }

        return paginate(
            query=query,
            page=page,
            limit=limit,
            sort_by=sort_by,
            order=order,
            allowed_sort_fields=allowed_sort_fields,
            default_sort_column=Transaction.date,
        )

    def get_transaction_by_id(self, trans_id, current_user):
        trans = self.db.query(Transaction).filter(Transaction.id == trans_id).first()
        if not trans:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        self._get_owned_account(trans.account_id, current_user)
        return trans

    def update_transaction(self, trans_id, trans_update, current_user):
        trans = self.db.query(Transaction).filter(Transaction.id == trans_id).first()
        if not trans:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        self._get_owned_account(trans.account_id, current_user)

        for key, value in trans_update.model_dump(exclude_unset=True).items():
            setattr(trans, key, value)

        self.db.commit()
        self.db.refresh(trans)
        return trans

    def delete_transaction(self, trans_id, current_user):
        trans = self.db.query(Transaction).filter(Transaction.id == trans_id).first()
        if not trans:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        self._get_owned_account(trans.account_id, current_user)
        self.db.delete(trans)
        self.db.commit()
        return trans

    def get_summary(self, current_user, from_date=None, to_date=None):
        """Overall income / expense / balance summary, optionally filtered by date range."""
        query = self.db.query(
            Transaction.transaction_type,
            func.sum(Transaction.amount).label("total"),
        ).join(Account).filter(Account.user_id == current_user.id)

        if from_date:
            query = query.filter(Transaction.date >= from_date)
        if to_date:
            query = query.filter(Transaction.date <= to_date)

        results = query.group_by(Transaction.transaction_type).all()

        income = 0.0
        expense = 0.0
        for row in results:
            if row.transaction_type == "income":
                income = float(row.total)
            elif row.transaction_type == "expense":
                expense = float(row.total)

        return {
            "total_income": income,
            "total_expense": expense,
            "balance": income - expense,
            "from_date": from_date.isoformat() if from_date else None,
            "to_date": to_date.isoformat() if to_date else None,
        }

    def get_category_breakdown(self, current_user, transaction_type=None, from_date=None, to_date=None):
        """Spending / income breakdown by category."""
        query = self.db.query(
            Transaction.category,
            Transaction.transaction_type,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count"),
        ).join(Account).filter(Account.user_id == current_user.id)

        if transaction_type in ["income", "expense"]:
            query = query.filter(Transaction.transaction_type == transaction_type)
        if from_date:
            query = query.filter(Transaction.date >= from_date)
        if to_date:
            query = query.filter(Transaction.date <= to_date)

        results = query.group_by(Transaction.category, Transaction.transaction_type).all()

        return [
            {
                "category": row.category,
                "transaction_type": row.transaction_type,
                "total": float(row.total),
                "count": row.count,
            }
            for row in results
        ]

    def get_monthly_trends(self, current_user, year: int):
        """Monthly income vs expense for a given year — useful for charts."""
        query = self.db.query(
            func.strftime("%m", Transaction.date).label("month"),
            Transaction.transaction_type,
            func.sum(Transaction.amount).label("total"),
        ).join(Account).filter(
            Account.user_id == current_user.id,
            func.strftime("%Y", Transaction.date) == str(year),
        ).group_by("month", Transaction.transaction_type).all()

        # Build a full 12-month structure even for months with no data
        months = {str(i).zfill(2): {"income": 0.0, "expense": 0.0} for i in range(1, 13)}
        for row in query:
            months[row.month][row.transaction_type] = float(row.total)

        return [
            {
                "month": month,
                "income": data["income"],
                "expense": data["expense"],
                "balance": data["income"] - data["expense"],
            }
            for month, data in months.items()
        ]
