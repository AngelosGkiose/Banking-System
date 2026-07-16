class Transaction:
    def __init__(self, account_id, type, amount, date, description="", transaction_id=None):
        self.transaction_id = transaction_id
        self.account_id = account_id
        self.type = type              # "deposit", "withdrawal", "transfer_in", "transfer_out"
        self.amount = amount
        self.date = date
        self.description = description

    def __str__(self):
        return (
            f"ID: {self.transaction_id} | "
            f"Type: {self.type.replace('_', ' ').title()} | "
            f"Amount: €{self.amount:.2f} | "
            f"Date: {self.date} | "
            f"Description: {self.description}"
        )
