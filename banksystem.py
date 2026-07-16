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
    def get_user_input():
        while True:
            customer_name=input("Please enter your customer name: ").strip()
            customer_email = input("Please enter your customer email: ").strip()
            if not customer_name:
                print("Please enter a customer name")
                continue
            if not customer_email:
                print("Please enter a customer email")
                continue
            break
        return customer_name,customer_email


    def handle_create_account(self):
        customer_name,customer_email = self.get_user_input()
        customer=self.database.get_customer_by_email(customer_email)
        if customer is None:
            customer=Customer(customer_name,customer_email)
            customer_created = self.database.add_customer(customer)
            if not customer_created:
                print("Customer could not be created!")
                return
        account_type = input("Please enter your account type(savings/checking): ").strip().lower()
        if not account_type or account_type not in ["savings", "checking"]:
            print("Please enter your account type: ")
            return
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
        account_number=input("Please enter your account number: ").strip().upper()
        if not account_number:
            print("Please enter a account number.")
            return
        account=self.database.get_account_by_account_number(account_number)
        if not account:
            print("Account was not found.")
            return
        try:
            amount=float(input("Please enter your deposit amount: "))
            if amount<=0:
                print("Please enter a positive amount.")
                return
        except ValueError:
            print("Please enter a integer value.")
            return
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
        account_number = input("Please enter your account number: ").strip().upper()
        if not account_number:
            print("Please enter a account number.")
            return
        account = self.database.get_account_by_account_number(account_number)
        if not account:
            print("Account was not found.")
            return
        try:
            amount=float(input("Please enter your withdraw amount: "))
            if amount<=0:
                print("Please enter a positive amount.")
                return
        except ValueError:
            print("Please enter a integer value.")
            return
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

    def transfer(self):
        source_account_number=input("Please enter source account number: ").strip().upper()
        if not source_account_number:
            print("Please enter a account number.")
            return
        source_account = self.database.get_account_by_account_number(source_account_number)
        if not source_account:
            print("Account was not found.")
            return
        destination_account_number=input("Please enter destination account number: ").strip().upper()
        if not destination_account_number:
            print("Please enter a account number.")
            return
        destination_account = self.database.get_account_by_account_number(destination_account_number)
        if not destination_account:
            print("Account was not found.")
            return
        if source_account.account_number == destination_account.account_number:
            print("Accounts cannot be the same.")
            return
        try:
            amount=float(input("Please enter your transfer amount: "))
            if amount<=0:
                print("Please enter a positive amount.")
                return
        except ValueError:
            print("Please enter a numeric value.")
            return
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
            description=f"Transfer in from {source_account.account_number}  "
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
        account_number = input("Please enter your account number: ").strip().upper()
        if not account_number:
            print("Please enter an account number.")
            return
        account = self.database.get_account_by_account_number(account_number)
        if not account:
            print("Account was not found.")
            return
        print(account)

    def handle_view_transaction_history(self):
        account_number = input("Please enter your account number: ").strip().upper()
        if not account_number:
            print("Please enter an account number.")
            return
        account = self.database.get_account_by_account_number(account_number)
        if not account:
            print("Account was not found.")
            return
        transaction_history = self.database.get_transactions_by_account_id(account)
        if transaction_history:
            print("\n===== Transaction History =====")
            print(f"Account Number: {account.account_number}\n")
            for transaction in transaction_history:
                print(transaction)
        else:
            print("Transactions could not be found.")

    def apply_interest(self):
        account_number = input("Please enter your account number: ").strip().upper()
        if not account_number:
            print("Please enter an account number.")
            return
        account = self.database.get_account_by_account_number(account_number)
        if not account:
            print("Account was not found.")
            return
        if account.account_type == "checking":
            print("No interest in checking account.")
            return
        interest_amount=account.apply_interest()
        if interest_amount<=0:
            print("Insufficient balance.")
            return
        transaction=Transaction(account.account_id,type="interest",amount=interest_amount,
                                date=date.today().isoformat(),description="Applying interest")
        completed=self.database.update_balance_and_add_transaction(account,transaction)
        if completed:
            print("Interest applied successfully.")
            print(f"Interest amount: €{interest_amount:.2f}")
            print(f"New balance: €{account.balance:.2f}")
        else:
            print("Interest could not be applied.")

    def handle_close_account(self):
        account_number = input("Please enter your account number: ").strip().upper()
        if not account_number:
            print("Please enter an account number.")
            return
        account = self.database.get_account_by_account_number(account_number)
        if not account:
            print("Account was not found.")
            return
        if account.balance ==0:
            confirmation = input(
                f"Are you sure you want to close this account({account.account_number})? (yes/no) "
            ).strip().lower()
            if confirmation=="no":
                print("Deletion cancelled.")
                return
            if confirmation != "yes":
                print("Please enter yes or no.")
                return
            completed= self.database.close_account(account)
            if completed:
                print("Close account successfully.")
            else:
                print("Account could not be closed.")
        else:
            print("The account cannot be closed.")
            print("The account balance must be €0.00.")
            print(f"Current balance: €{account.balance:.2f}")
            return

    def close(self):
        self.database.close_connection()















