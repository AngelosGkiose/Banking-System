from account import Account


class CheckingAccount(Account):
    def __init__(self, customer_id,balance=0.0, account_id=None,account_number=None, overdraft_limit=100,status="active"):
        super().__init__(customer_id=customer_id,account_type="checking",balance=balance,account_id=account_id,account_number=account_number,status=status)
        self.overdraft_limit = overdraft_limit

    def __str__(self):
        return (
            "===== Account Information =====\n"
            f"Account Number   : {self.account_number}\n"
            f"Account Type     : Checking\n"
            f"Balance          : €{self.balance:.2f}\n"
            f"Status         : {self.status.capitalize()}\n"
            f"Overdraft Limit  : €{self.overdraft_limit:.2f}"
        )

    def withdraw(self, amount):
        if self.status != "active":
            return False
        if amount <= 0:
            return False
        if amount > self.balance + self.overdraft_limit:
            return False
        self.balance -= amount
        return True