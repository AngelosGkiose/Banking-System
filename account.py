class Account:
    def __init__(self, customer_id,account_type,balance=0.0, account_id=None,account_number=None):
        self.account_id = account_id
        self.customer_id = customer_id
        self.account_number = account_number
        self.balance = balance
        self.account_type = account_type

    def __str__(self):
        return (
            "===== Account Information =====\n"
            f"Account Number : {self.account_number}\n"
            f"Account Type   : {self.account_type.capitalize()}\n"
            f"Balance        : €{self.balance:.2f}"
        )

    def deposit(self, amount):
        if amount <= 0:
            return False
        self.balance += amount
        return True

    def withdraw(self, amount):
        if amount <= 0:
            return False

        if amount > self.balance:
            return False

        self.balance -= amount
        return True