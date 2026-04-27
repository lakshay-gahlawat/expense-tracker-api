from fastapi import HTTPException, status
from app.models.account import Account
from app.models.transaction import Transaction
from sqlalchemy import func
from app.utils.pagination import paginate


class AccountService:
    def __init__(self, db):
        self.db = db

    def _get_owned(self, account_id, current_user):
        account = self.db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        if account.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        return account

    def create_account(self, account_data, current_user):
        account = Account(name=account_data.name, user_id=current_user.id)
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def get_accounts(self, current_user, page, limit, filters, sort_by, order):
        allowed_sort_fields = {
            "name": Account.name,
            "id": Account.id,
            "created_at": Account.created_at,
        }

        query = self.db.query(Account).filter(Account.user_id == current_user.id)

        if filters.get("name"):
            query = query.filter(Account.name.ilike(f"%{filters['name']}%"))

        return paginate(
            query=query,
            page=page,
            limit=limit,
            sort_by=sort_by,
            order=order,
            allowed_sort_fields=allowed_sort_fields,
            default_sort_column=Account.created_at,
        )

    def get_account_by_id(self, account_id, current_user):
        return self._get_owned(account_id, current_user)

    def update_account(self, account_id, update_data, current_user):
        account = self._get_owned(account_id, current_user)
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(account, key, value)
        self.db.commit()
        self.db.refresh(account)
        return account

    def delete_account(self, account_id, current_user):
        account = self._get_owned(account_id, current_user)
        self.db.delete(account)
        self.db.commit()
        return account

    def get_account_summary(self, account_id, current_user):
        """Returns total income, expense, and net balance for one account."""
        account = self._get_owned(account_id, current_user)

        def _sum(t_type):
            val = (
                self.db.query(func.sum(Transaction.amount))
                .filter(
                    Transaction.account_id == account_id,
                    Transaction.transaction_type == t_type,
                )
                .scalar()
            )
            return float(val or 0)

        income = _sum("income")
        expense = _sum("expense")

        return {
            "account_id": account_id,
            "name": account.name,
            "total_income": income,
            "total_expense": expense,
            "balance": income - expense,
        }
