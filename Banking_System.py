import random
import sqlite3


class Account:
    def __init__(self):
        self.acc_num = "400000"
        self.pin = str(random.randint(0,9999)).zfill(4)
        self.balance = 0
        #self.accounts = account_nums

    def make_account(self, account_list):
        # generating a random number
        temp_num = self.acc_num + str(random.randint(0,999999999)).zfill(9)
        temp_num += self.check_sum(temp_num)

        while account_list.count(temp_num) != 0:
            temp_num = self.acc_num + str(random.randint(0,999999999)).zfill(9)
            temp_num += self.check_sum(temp_num)
        self.acc_num = temp_num


    def check_sum(self, temp_card):
        # generating a checksum with the Luhn method
        num_list = [int(x) for x in temp_card]
        for i in range(0, len(num_list)):
            if (i + 1) % 2 != 0:
                num_list[i] *= 2
        for i in range(0, len(num_list)):
            if num_list[i] > 9:
                num_list[i] -= 9
        num_sum = sum(num_list)
        ck_sum = 10 - (num_sum % 10)
        if ck_sum == 10:
            ck_sum = 0

        return str(ck_sum)
    
    def set_account(self, new_num):
        self.acc_num = new_num

    def set_pin(self, new_num):
        self.pin = new_num

    def set_balance(self, bal):
        self.balance = bal

    def update_balance(self, deposit):
        self.balance += deposit


def acc_menu(this_account, conn):
    curr = conn.cursor()
    curr.execute("SELECT id FROM card WHERE number = :num", {"num": this_account.acc_num})
    id = curr.fetchone()[0]
    print("\nYou have successfully logged in!")
    print("\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")
    sel = input()
    while sel != "0":
        if sel == "1":
            print("\nBalance: ${0:,.2f}".format(this_account.balance))
        elif sel == "2":
            print("\nEnter income:")
            deposit = float(input())
            this_account.update_balance(deposit)
            curr.execute("UPDATE card SET balance = ? WHERE id = ?", (this_account.balance, id))
            conn.commit()
        elif sel == "3":
            print("\nTransfer")
            balance_transfer(this_account, conn)
        elif sel == "4":
            curr.execute("DELETE FROM card WHERE number = :num", {"num": this_account.acc_num})
            conn.commit()
            print("\nThe account has been closed!")
            return sel
        elif sel == "5":
            print("\nYou have successfully logged out!")
            return sel
        print("\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")
        sel = input()
    return sel


def balance_transfer(transfer_account, conn):
    curr = conn.cursor()
    print("Enter card number:")
    trans_to = input()
    is_good = luhn(trans_to)
    if not is_good:
        print("Probably you made a mistake in the card number. Please try again!")
    else:
        curr.execute("SELECT * FROM card WHERE number = :num", {"num": trans_to})
        temp = curr.fetchone()
        if not temp:
            print("Such a card does not exist.")
        else:
            print("Enter how much money you want to transfer:")
            trans_amount = float(input())
            if trans_amount > transfer_account.balance:
                print("Not enough money!")
            else:
                receive_acc = Account()
                receive_acc.set_account(temp[1])
                receive_acc.set_pin(temp[2])
                receive_acc.set_balance(temp[3])
                receive_acc.update_balance(trans_amount)
                curr.execute("UPDATE card SET balance = ? WHERE id = ?", (receive_acc.balance, temp[0]))
                conn.commit()
                transfer_account.update_balance(-trans_amount)
                curr.execute("SELECT id FROM card WHERE number = :num", {"num": transfer_account.acc_num})
                temp = curr.fetchone()[0]
                curr.execute("UPDATE card SET balance = ? WHERE id = ?", 
                             (transfer_account.balance, temp))
                conn.commit()
                print("\nSuccess!")


def luhn(account_number):
    num_list = [int(x) for x in account_number]
    last_digit = num_list.pop()
    for i in range(0, len(num_list)):
        if (i + 1) % 2 != 0:
            num_list[i] *= 2
    for i in range(0, len(num_list)):
        if num_list[i] > 9:
            num_list[i] -= 9
    num_sum = sum(num_list)
    ck_sum = 10 - (num_sum % 10)
    if ck_sum == 10:
        ck_sum = 0
        
    return last_digit == ck_sum


# ********** MAIN **********

# creating a database for the accounts
conn = sqlite3.connect("card.s3db")
cur = conn.cursor()
# Creating a table that will give each card a sequential ID number.
# The table will be in this format:
# id, card number, pin number, balance
cur.execute("CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " number TEXT, pin TEXT, balance INTEGER DEFAULT 0);")
conn.commit()

# This will store all the account numbers that are made
account_nums = []
cur.execute("SELECT number FROM card")
temp = cur.fetchall()
for i in range(0, len(temp)):
    account_nums.append(temp[i][0])

# printing the main menu
print("1. Create an account\n2. Log into account\n0. Exit")
selection = input()

while selection != "0":
    if selection == "1":
        new_account = Account()
        new_account.make_account(account_nums)
        print("\nYour card has been created")
        print("Your card number:")
        print(new_account.acc_num)
        print("Your card PIN:")
        print(new_account.pin)
        cur.execute("INSERT INTO card (number, pin) VALUES (?, ?)", 
                    (new_account.acc_num, new_account.pin))
        conn.commit()
    
    elif selection == "2":
        print("\nEnter your card number:")
        card_num = input()
        print("Enter your PIN:")
        card_pin = input()

        cur.execute("SELECT number, pin, balance FROM card WHERE number = :num", {"num": card_num})
        this_card = cur.fetchall()
        
        if len(this_card) > 0:
            if this_card[0][1] == card_pin:
                new_account = Account()
                new_account.set_account(this_card[0][0])
                new_account.set_pin(this_card[0][1])
                new_account.set_balance(this_card[0][2])
                selection = acc_menu(new_account, conn)
            else:
                print("Wrong card number or PIN!")
        else:
            print("Wrong card number or PIN!")
        
    if selection != "0":        
        print("\n1. Create an account\n2. Log into account\n0. Exit")
        selection = input()

print("\nBye!")
conn.close()
