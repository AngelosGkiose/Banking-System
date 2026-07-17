from datetime import date


from transaction import Transaction
from checkingaccount import CheckingAccount
from customer import Customer
from database import Database
from savingsaccount import SavingsAccount


class BankSystem:
    def __init__(self):
       self.database=Database()

    @staticmethod
    def get_customer_name():
        while True:
            customer_name = input(
                "Please enter your customer name: "
            ).strip()

            if not customer_name:
                print("Please enter a customer name.")
                continue

            return customer_name

    @staticmethod
    def get_customer_email():
        while True:
            customer_email = input(
                "Please enter your customer email: "
            ).strip().lower()

            if not customer_email:
                print("Please enter a customer email.")
                continue

            if "@" not in customer_email or "." not in customer_email:
                print("Please enter a valid email address.")
                continue

            return customer_email

    def get_account(self, message="Please enter your account number: ",allow_closed=False):
        while True:
            account_number = input(message).strip().upper()

            if not account_number:
                print("Please enter an account number.")
                continue

            account = self.database.get_account_by_account_number(account_number)

            if account is None:
                print("Account was not found.")
                continue

            if account.status == "closed" and not allow_closed:
                print("This account is closed and cannot be used.")
                continue

            return account

    @staticmethod
    def get_amount( message):
        while True:
            try:
                amount = float(input(message).strip())

                if amount <= 0:
                    print("Please enter a positive amount.")
                    continue

                return amount

            except ValueError:
                print("Please enter a numeric value.")

    @staticmethod
    def get_confirmation( message):
        while True:
            confirmation = input(message).strip().lower()

            if confirmation == "yes":
                return True

            if confirmation == "no":
                return False

            print("Please enter yes or no.")


    def handle_create_account(self):
        customer_name = self.get_customer_name()
        customer_email = self.get_customer_email()
        customer=self.database.get_customer_by_email(customer_email)
        if customer is None:
            customer=Customer(customer_name,customer_email)
            customer_created = self.database.add_customer(customer)
            if not customer_created:
                print("Customer could not be created!")
                return
        while True:
            account_type = input("Please enter your account type(savings/checking): ").strip().lower()
            if not account_type or account_type not in ["savings", "checking"]:
                print("Please enter your account type: ")
                continue
            break
        if account_type == "savings":
            account = SavingsAccount(customer_id=customer.customer_id)
        else:
            account = CheckingAccount(customer_id=customer.customer_id)
        account_created = self.database.create_account(account)
        if account_created:
            print(
                f"{account.account_type.capitalize()} account "
                f"created successfully.")
            print(f"Account number: {account.account_number}")
        else:
            print("Account could not be created.")

    def handle_view_account(self):
        accounts=self.database.get_all_accounts()
        if not accounts:
            print("No accounts found.")
            return
        print("\n===== All Accounts =====")
        for account in accounts:
            print(account)

    def handle_deposit(self):
        account = self.get_account()
        amount = self.get_amount(
            "Please enter your deposit amount: "
        )
        deposited = account.deposit(amount)
        if not deposited:
            print("Deposit could not be completed.")
            return
        transaction = Transaction(
            account_id=account.account_id,
            type="deposit",
            amount=amount,
            date=date.today().isoformat(),
            description="Cash deposit"
        )
        completed = self.database.update_balance_and_add_transaction(account,transaction)
        if completed:
            print("Deposit successful.")
            print(f"New balance: €{account.balance:.2f}")
        else:
            print("Deposit could not be completed.")

    def handle_withdraw(self):
        account = self.get_account()
        amount = self.get_amount(
            "Please enter your withdrawal amount: "
        )
        withdrawn = account.withdraw(amount)
        if not withdrawn:
            print("Insufficient balance.")
            return
        transaction = Transaction(
            account_id=account.account_id,
            type="withdrawal",
            amount=amount,
            date=date.today().isoformat(),
            description="Cash withdrawal"
        )
        completed = self.database.update_balance_and_add_transaction(
            account,
            transaction
        )
        if completed:
            print("Withdrawal successful.")
            print(f"New balance: €{account.balance:.2f}")
        else:
            print("Withdrawal could not be completed.")

    def handle_transfer(self):
        source_account = self.get_account(
            "Please enter source account number: "
        )
        while True:
            destination_account = self.get_account(
                "Please enter destination account number: "
            )
            if source_account.account_number == destination_account.account_number:
                print("Accounts cannot be the same.")
                continue
            break
        amount = self.get_amount(
            "Please enter your transfer amount: "
        )
        withdrawn=source_account.withdraw(amount)
        if not withdrawn:
            print("Insufficient balance.")
            return
        deposited=destination_account.deposit(amount)
        if not deposited:
            print("Deposit could not be completed.")
            return
        transfer_out = Transaction(
            account_id=source_account.account_id,
            type="transfer_out",
            amount=amount,
            date=date.today().isoformat(),
            description=f"Transfer to {destination_account.account_number}"
        )
        transfer_in = Transaction(account_id=destination_account.account_id,
            type="transfer_in",
            amount=amount,
            date=date.today().isoformat(),
            description=f"Transfer from {source_account.account_number}  "
        )
        completed = self.database.transfer_between_accounts(source_account,destination_account,transfer_in,transfer_out)
        if completed:
            print("Transfer successful.")
            print(
                f"Source account balance: "
                f"€{source_account.balance:.2f}"
            )
            print(
                f"Destination account balance: "
                f"€{destination_account.balance:.2f}"
            )
        else:
            print("Transfer could not be completed.")

    def handle_view_balance(self):
        account = self.get_account()
        print(account)

    def handle_view_transaction_history(self):
        account = self.get_account(
            message="Please enter your account number: ",
            allow_closed=True
        )
        transaction_history = (
            self.database.get_transactions_by_account_id(account)
        )
        if not transaction_history:
            print("No transactions found.")
            return
        print("\n===== Transaction History =====")
        print(f"Account Number: {account.account_number}")
        print(f"Account Status: {account.status.capitalize()}\n")
        for transaction in transaction_history:
            print(transaction)

    def handle_apply_interest(self):
        account = self.get_account()
        if account.account_type == "checking":
            print("No interest in checking account.")
            return
        interest_amount=account.apply_interest()
        if interest_amount<=0:
            print("Insufficient balance.")
            return
        transaction = Transaction(
            account_id=account.account_id,
            type="interest",
            amount=interest_amount,
            date=date.today().isoformat(),
            description="Interest applied"
        )
        completed=self.database.update_balance_and_add_transaction(account,transaction)
        if completed:
            print("Interest applied successfully.")
            print(f"Interest amount: €{interest_amount:.2f}")
            print(f"New balance: €{account.balance:.2f}")
        else:
            print("Interest could not be applied.")

    def handle_close_account(self):
        account = self.get_account(
            message="Please enter your account number: ",
            allow_closed=True
        )
        if account.balance != 0:
            print("The account cannot be closed.")
            print("The account balance must be €0.00.")
            print(f"Current balance: €{account.balance:.2f}")
            return
        confirmed = self.get_confirmation(
            f"Are you sure you want to close this account "
            f"({account.account_number})? (yes/no): "
        )
        if not confirmed:
            print("Deletion cancelled.")
            return
        closed=account.disable_account()
        if not closed:
            print("Account is already closed.")
            return
        completed= self.database.close_account(account)
        if completed:
            print("Account closed successfully.")
        else:
            account.status = "active"
            print("Account could not be closed.")

    def close(self):
        self.database.close_connection()















