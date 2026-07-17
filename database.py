import sqlite3

from checkingaccount import CheckingAccount
from customer import Customer
from savingsaccount import SavingsAccount
from transaction import Transaction


class Database:
    def __init__(self, database_name="banking.db"):
        self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()

        self.connection.execute("PRAGMA foreign_keys = ON")

        self.create_customers_table()
        self.create_accounts_table()
        self.create_savings_accounts_table()
        self.create_checking_accounts_table()
        self.create_transactions_table()

    # =========================
    # TABLE CREATION METHODS
    # =========================

    def create_customers_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        """)

        self.connection.commit()

    def create_accounts_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                account_number TEXT UNIQUE,
                balance REAL NOT NULL DEFAULT 0,
                account_type TEXT NOT NULL
                    CHECK (account_type IN ('savings', 'checking')),
                status TEXT NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'closed')),
                FOREIGN KEY (customer_id)
                    REFERENCES customers(id)
                    ON DELETE CASCADE,
                CHECK (
                    account_type = 'checking'
                    OR balance >= 0
                )
            )
        """)

        self.connection.commit()

    def create_savings_accounts_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS savings_accounts (
                account_id INTEGER PRIMARY KEY,
                interest_rate REAL NOT NULL DEFAULT 0.02
                    CHECK (interest_rate >= 0),
                FOREIGN KEY (account_id)
                    REFERENCES accounts(id)
                    ON DELETE CASCADE
            )
        """)

        self.connection.commit()

    def create_checking_accounts_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS checking_accounts (
                account_id INTEGER PRIMARY KEY,
                overdraft_limit REAL NOT NULL DEFAULT 100
                    CHECK (overdraft_limit >= 0),
                FOREIGN KEY (account_id)
                    REFERENCES accounts(id)
                    ON DELETE CASCADE
            )
        """)

        self.connection.commit()

    def create_transactions_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                type TEXT NOT NULL
                    CHECK (
                        type IN (
                            'deposit',
                            'withdrawal',
                            'transfer_in',
                            'transfer_out',
                            'interest'
                        )
                    ),
                amount REAL NOT NULL CHECK (amount > 0),
                date TEXT NOT NULL,
                description TEXT DEFAULT '',
                FOREIGN KEY (account_id)
                    REFERENCES accounts(id)
                    ON DELETE CASCADE
            )
        """)

        self.connection.commit()

    def get_customer_by_email(self,customer_email):
        self.cursor.execute("""Select * from customers where email = ?""",(customer_email,))
        customer = self.cursor.fetchone()
        if customer is None:
            return None
        else:
            return Customer(customer[1],customer[2],customer[0])

    def add_customer(self, new_customer):
        try:
            self.cursor.execute("""
                INSERT INTO customers (name, email)
                VALUES (?, ?)
            """, (
                new_customer.name,
                new_customer.email
            ))

            new_customer.customer_id = self.cursor.lastrowid

            self.connection.commit()
            return True

        except sqlite3.IntegrityError:
            self.connection.rollback()
            return False


    def create_account(self,account):
        try:
            self.cursor.execute("""Insert into accounts(customer_id,account_type) values(?,?)""",(account.customer_id,account.account_type,))
            account.account_id = self.cursor.lastrowid
            account.account_number = self.generate_account_number(account.account_id)
            self.cursor.execute("""Update accounts Set account_number=? where id=?""",(account.account_number,account.account_id,))
            if account.account_type == "savings":
                self.cursor.execute("""
                    INSERT INTO savings_accounts(account_id, interest_rate)
                    VALUES (?, ?)
                """, (
                    account.account_id,
                    account.interest_rate
                ))

            elif account.account_type == "checking":
                self.cursor.execute("""
                    INSERT INTO checking_accounts(account_id, overdraft_limit)
                    VALUES (?, ?)
                """, (
                    account.account_id,
                    account.overdraft_limit
                ))
            self.connection.commit()
            return True
        except sqlite3.Error as error:
            self.connection.rollback()
            print(f"Database error: {error}")
            return False

    def get_all_accounts(self):
        self.cursor.execute("""Select accounts.id,accounts.customer_id,accounts.account_number,accounts.balance,accounts.account_type,savings_accounts.interest_rate,
            checking_accounts.overdraft_limit,accounts.status from accounts left join savings_accounts on accounts.id = savings_accounts.account_id 
            left join checking_accounts on accounts.id = checking_accounts.account_id  ORDER BY accounts.id""")
        rows = self.cursor.fetchall()
        accounts = []
        for row in rows:
            account_id = row[0]
            customer_id = row[1]
            account_number = row[2]
            balance = row[3]
            account_type = row[4]
            interest_rate = row[5]
            overdraft_limit = row[6]
            status = row[7]
            if account_type == "savings":
                account=SavingsAccount(customer_id,balance,account_id,account_number,interest_rate,status)
            else:
                account=CheckingAccount(customer_id,balance,account_id,account_number,overdraft_limit,status)
            accounts.append(account)
        return accounts

    def get_account_by_account_number(self,account_number):
        self.cursor.execute("""Select * from accounts  where account_number = ?""",(account_number,))
        account = self.cursor.fetchone()
        if account is None:
            return None
        account_id = account[0]
        customer_id = account[1]
        account_number = account[2]
        balance = account[3]
        account_type = account[4]
        status=account[5]
        if account_type == "savings":
            self.cursor.execute("""Select * from savings_accounts  where account_id = ?""",(account_id,))
            row = self.cursor.fetchone()
            if row is None:
                return None
            return SavingsAccount(customer_id,balance,account_id,account_number,row[1],status)
        elif account_type == "checking":
            self.cursor.execute("""Select * from checking_accounts  where account_id = ?""",(account_id,))
            row = self.cursor.fetchone()
            if row is None:
                return None
            return CheckingAccount(customer_id,balance,account_id,account_number,row[1],status)
        return None

    def update_balance_and_add_transaction(self, account, transaction):
        try:
            self.cursor.execute("""
                UPDATE accounts
                SET balance = ?
                WHERE id = ?
            """, (
                account.balance,
                account.account_id
            ))
            self.cursor.execute("""
                INSERT INTO transactions (
                    account_id,
                    type,
                    amount,
                    date,
                    description
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                transaction.account_id,
                transaction.type,
                transaction.amount,
                transaction.date,
                transaction.description
            ))
            transaction.transaction_id = self.cursor.lastrowid
            self.connection.commit()
            return True
        except sqlite3.Error as error:
            self.connection.rollback()
            print(f"Database error: {error}")
            return False

    def transfer_between_accounts(self,source_account,destination_account,transfer_in,transfer_out):
        try:
            self.cursor.execute("""Update accounts set balance=? where id = ?""",(source_account.balance,source_account.account_id))
            self.cursor.execute("""Update accounts set balance=? where id = ?""",(destination_account.balance,destination_account.account_id))
            self.cursor.execute("""Insert into transactions (account_id,type,amount,date,description) values (?,?,?,?,?)""",
                                (transfer_in.account_id,transfer_in.type,transfer_in.amount,transfer_in.date,transfer_in.description))
            transfer_in.transaction_id = self.cursor.lastrowid
            self.cursor.execute(
                """Insert into transactions (account_id,type,amount,date,description) values (?,?,?,?,?)""",
                (transfer_out.account_id, transfer_out.type, transfer_out.amount, transfer_out.date,
                 transfer_out.description))
            transfer_out.transaction_id = self.cursor.lastrowid
            self.connection.commit()
            return True
        except sqlite3.Error as error:
            self.connection.rollback()
            print(f"Database error: {error}")
            return False

    def get_transactions_by_account_id(self,account):
        self.cursor.execute("""Select * from transactions  where account_id = ? ORDER BY id DESC """,(account.account_id,))
        rows = self.cursor.fetchall()
        transactions = []
        for row in rows:
            transactions.append(Transaction(row[1],row[2],row[3],row[4],row[5],row[0]))
        return transactions

    def close_account(self, account):
        try:
            self.cursor.execute("""
                UPDATE accounts
                SET status = ?
                WHERE id = ?
                  AND status = 'active'
            """, (
                account.status,
                account.account_id
            ))
            if self.cursor.rowcount != 1:
                self.connection.rollback()
                return False
            self.connection.commit()
            return True
        except sqlite3.Error as error:
            self.connection.rollback()
            print(f"Database error: {error}")
            return False



    @staticmethod
    def generate_account_number( account_id):
        return f"GR{account_id:04d}"

    def close_connection(self):
        self.connection.close()