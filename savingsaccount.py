from account import Account


class SavingsAccount(Account):
    def __init__(self, customer_id,balance=0.0,account_id=None,account_number=None, interest_rate=0.02,status="active"):
        super().__init__(customer_id=customer_id,account_type="savings",balance=balance, account_id=account_id,account_number=account_number,status=status)
        self.interest_rate = interest_rate

    def __str__(self):
        return (
            "===== Account Information =====\n"
            f"Account Number : {self.account_number}\n"
            f"Account Type   : Savings\n"
            f"Balance        : €{self.balance:.2f}\n"
            f"Status         : {self.status.capitalize()}\n"
            f"Interest Rate  : {self.interest_rate * 100:.2f}%"
        )

    def apply_interest(self):
        interest_amount = self.balance * self.interest_rate

        if interest_amount <= 0:
            return 0

        self.balance += interest_amount
        return interest_amount
