from banksystem import BankSystem


def show_menu():
    print("""===== Banking System =====

1. View All Accounts
2. Create Account
3. Deposit
4. Withdraw
5. Transfer Between Accounts
6. View Account Balance
7. View Transaction History
8. Apply Interest (Savings Accounts)
9. Close Account
10. Exit""")




def main():
    system = BankSystem()
    try:
        while True:
            show_menu()
            user_choice = input("Enter your choice: ")
            if user_choice == "1":
                system.handle_view_account()
            elif user_choice == "2":
                system.handle_create_account()
            elif user_choice == "3":
                system.handle_deposit()
            elif user_choice == "4":
                system.handle_withdraw()
            elif user_choice == "5":
                system.transfer()
            elif user_choice == "6":
                system.handle_view_balance()
            elif user_choice == "7":
                system.handle_view_transaction_history()
            elif user_choice == "8":
                system.apply_interest()
            elif user_choice == "9":
                system.handle_close_account()
            elif user_choice == "10":
                print("Thank you for your time!")
                break
            else:
                print("Please enter a valid choice.")
    finally:
        system.close()



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

