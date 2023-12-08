import random
import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import configparser

class ATM:
    def __init__(self, user_data):
        self.user_data = user_data
        self.transactions = []
        self.wallets = {}  # E-wallets for each user

    def display_menu(self):
        print("\n===== ATM Menu =====")
        print("1. Check Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Send Money")
        print("5. Receive Money")
        print("6. Generate Receipt")
        print("7. Create E-Wallet")
        print("8. Transaction History")
        print("9. Exit")

    def authenticate_user(self, card_number, entered_pin):
        if card_number in self.user_data:
            stored_salt = bytes.fromhex(self.user_data[card_number]['salt'])
            stored_key = bytes.fromhex(self.user_data[card_number]['key'])

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                salt=stored_salt,
                length=32,
                iterations=100000,
                backend=default_backend()
            )

            entered_pin_hash = kdf.derive(entered_pin.encode())

            if stored_key == entered_pin_hash:
                return True
            else:
                print("Incorrect PIN. Authentication failed.")
        else:
            print("Card not found. Authentication failed.")

        return False

    def check_balance(self, card_number):
        print(f"Your balance: ${self.user_data[card_number]['balance']}")

    def deposit(self, card_number, amount):
        self.user_data[card_number]['balance'] += amount
        self.transactions.append((datetime.datetime.now(), card_number, 'Deposit', amount))
        print(f"Deposited ${amount}. New balance: ${self.user_data[card_number]['balance']}")

    def withdraw(self, card_number, amount):
        if amount <= self.user_data[card_number]['balance']:
            self.user_data[card_number]['balance'] -= amount
            self.transactions.append((datetime.datetime.now(), card_number, 'Withdrawal', amount))
            print(f"Withdrew ${amount}. New balance: ${self.user_data[card_number]['balance']}")
        else:
            print("Insufficient funds!")

    def send_money(self, sender_card_number, recipient_card_number, amount):
        if sender_card_number in self.user_data and recipient_card_number in self.user_data:
            if amount <= self.user_data[sender_card_number]['balance']:
                self.user_data[sender_card_number]['balance'] -= amount
                self.user_data[recipient_card_number]['balance'] += amount
                self.transactions.append((datetime.datetime.now(), sender_card_number, 'Send Money', amount))
                print(f"Sent ${amount} from {sender_card_number} to {recipient_card_number}.")
            else:
                print("Insufficient funds for the transaction.")
        else:
            print("Invalid card numbers.")

    def receive_money(self, recipient_card_number, amount):
        if recipient_card_number in self.user_data:
            self.user_data[recipient_card_number]['balance'] += amount
            self.transactions.append((datetime.datetime.now(), recipient_card_number, 'Receive Money', amount))
            print(f"Received ${amount} on {recipient_card_number}. New balance: ${self.user_data[recipient_card_number]['balance']}")
        else:
            print("Invalid card number.")

    def generate_receipt(self):
        if self.transactions:
            latest_transaction = self.transactions[-1]
            print(f"Receipt for {latest_transaction[1]}:")
            print(f"Date: {latest_transaction[0]}")
            print(f"Transaction Type: {latest_transaction[2]}")
            print(f"Amount: ${latest_transaction[3]}")
        else:
            print("No transactions to generate a receipt.")

    def create_e_wallet(self, card_number):
        if card_number not in self.wallets:
            self.wallets[card_number] = 0  # Initial balance for the e-wallet
            print(f"E-Wallet created for {card_number}.")
        else:
            print("E-Wallet already exists for this card number.")

    def display_transactions(self):
        print("\n===== Transaction History =====")
        for transaction in self.transactions:
            print(f"{transaction[0]} - Card: {transaction[1]}, {transaction[2]}: ${transaction[3]}")

    def display_wallet_balance(self, card_number):
        if card_number in self.wallets:
            print(f"E-Wallet balance for {card_number}: ${self.wallets[card_number]}")
        else:
            print("E-Wallet not found for this card number.")

def generate_card_number():
    return ''.join([str(random.randint(0, 9)) for _ in range(16)])

def generate_salt_and_key(pin):
    salt = os.urandom(16)  # 16 bytes for the salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        salt=salt,
        length=32,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(pin.encode())
    return salt, key

def load_configuration():
    config = configparser.ConfigParser()
    config.read('config.ini')  # Replace with the actual path to your configuration file
    return config

def main():
    config = load_configuration()
    user_data = {
        '1234567890123456': {'salt': config.get('User1', 'salt'), 'key': config.get('User1', 'key'), 'balance': 10000},
        '9876543210987654': {'salt': config.get('User2', 'salt'), 'key': config.get('User2', 'key'), 'balance': 5000}
    }

    atm = ATM(user_data)

    card_number = input("Enter card number: ")
    pin = input("Enter PIN: ")

    if atm.authenticate_user(card_number, pin):
        while True:
            atm.display_menu()
            choice = input("Enter your choice (1-9): ")

            if choice == '1':
                atm.check_balance(card_number)
            elif choice == '2':
                amount = float(input("Enter the deposit amount: $"))
                atm.deposit(card_number, amount)
            elif choice == '3':
                amount = float(input("Enter the withdrawal amount: $"))
                atm.withdraw(card_number, amount)
            elif choice == '4':
                recipient_card_number = input("Enter recipient card number: ")
                amount = float(input("Enter the amount to send: $"))
                atm.send_money(card_number, recipient_card_number, amount)
            elif choice == '5':
                sender_card_number = input("Enter sender card number: ")
                amount = float(input("Enter the amount to receive: $"))
                atm.receive_money(card_number, amount)
            elif choice == '6':
                atm.generate_receipt()
            elif choice == '7':
                atm.create_e_wallet(card_number)
            elif choice == '8':
                atm.display_transactions()
            elif choice == '9':
                print("Exiting ATM. Thank you!")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
