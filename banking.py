import random
import sqlite3 as sq
conn = sq.connect("card.s3db")
cur = conn.cursor()


cur.execute("CREATE TABLE IF NOT EXISTS card(id INTEGER PRIMARY KEY AUTOINCREMENT"
            ", number TEXT, pin TEXT,balance INTEGER DEFAULT 0);")
conn.commit()
cur.execute("DELETE FROM card;")
conn.commit()

user_invitation_str = """1. Create an account
2. Log into account
0. Exit\n"""
CARD_NUMBER, USER_PIN = "", ""
BALANCE = 0
EXIT_FLAG = False


def card_creations():
    global cur, conn
    bin_str = "400000"
    account_identifier_str = ""
    user_pin_str = ""

    for i in range(9):
        account_identifier_str += f"{random.randint(0,9)}"
    user_card_number_str = bin_str+f"{account_identifier_str}"#+f"{random.randint(0,9)}"

    user_card_number_str += luhn_algorithm(user_card_number_str)

    for i in range(4):
        user_pin_str += f"{random.randint(0,9)}"

    cur.execute(f"INSERT INTO card(number,pin) VALUES({user_card_number_str},{user_pin_str});")
    conn.commit()
    return user_card_number_str, user_pin_str


def luhn_algorithm(user_card_number_str, valid_check=False):
    if len(user_card_number_str) == 16 and valid_check == True:
        user_card_number_str = user_card_number_str[:15]

    card_number_ch = ""
    count = 0
    sum_of_new_indf = 0
    for digit in user_card_number_str:
        count += 1
        if count == 1:
            current_num = int(digit)
            current_num *= 2
            if current_num > 9:
                current_num -= 9
            card_number_ch += str(current_num)
        else:
            count = 0
            card_number_ch += digit
    for cur_num in card_number_ch:
        sum_of_new_indf += int(cur_num)
    lim1 = (sum_of_new_indf // 10) * 10 + 10
    lim2 = (sum_of_new_indf // 10) * 10 - 10
    lim1 = abs(lim1 - sum_of_new_indf)
    lim2 = abs(lim2 - sum_of_new_indf)
    if lim1 > lim2:
        return str(lim2)
    elif lim1 < lim2:
        return str(lim1)
    else:
        return "0"


def card_logging():
    log_card = input("Enter your card number:\n")
    log_pin = input("Enter your PIN:\n")
    cur.execute(f"SELECT * FROM card WHERE number = {log_card} AND pin = {log_pin}")
    if bool(cur.fetchall()):
        print("You have successfully logged in!")
        card_operation(log_card, log_pin)
    else:
        print("Wrong card number or PIN!")
        return


def card_operation(log_card, log_pin):
    global EXIT_FLAG
    operation_list_str = """1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit\n"""
    user_operation_choice = int(input(operation_list_str))
    if user_operation_choice == 0:
        EXIT_FLAG = True
        return
    elif user_operation_choice == 1:
        cur.execute(f"SELECT balance FROM card WHERE number = {log_card} AND pin = {log_pin}")
        print(f"Balance: {cur.fetchall()[0][0]}")
    elif user_operation_choice == 2:
        cur.execute(f"SELECT balance FROM card WHERE number = {log_card} AND pin = {log_pin}")
        user_balance = cur.fetchall()[0][0]
        income = int(input("Enter income:\n"))
        cur.execute(f"UPDATE card SET balance = {user_balance+income} WHERE number = {log_card} AND pin = {log_pin}")
        conn.commit()
        print("Income was added!")
        card_operation(log_card, log_pin)
    elif user_operation_choice == 3:
        card_to_transfer_number = input("Transfer\nEnter card number:\n")
        check_sum = luhn_algorithm(card_to_transfer_number, True)
        if len(card_to_transfer_number) == 16 and check_sum == card_to_transfer_number[15]:
            cur.execute(f"SELECT * FROM card WHERE number = {card_to_transfer_number}")
            if bool(cur.fetchall()):
                money_to_transfer = int(input("Enter how much money you want to transfer:"))
                cur.execute(f"SELECT balance FROM card WHERE number = {log_card} AND pin = {log_pin}")
                user_money = cur.fetchall()[0][0]
                if user_money >= money_to_transfer:
                    cur.execute(f"UPDATE card SET balance = {user_money - money_to_transfer} WHERE number = {log_card} AND pin = {log_pin}")
                    conn.commit()
                    cur.execute(f"SELECT balance FROM card WHERE number = {card_to_transfer_number}")
                    target_balance = cur.fetchall()[0][0]
                    cur.execute(f"UPDATE card SET balance = {target_balance + money_to_transfer} WHERE number = {card_to_transfer_number}")
                    conn.commit()
                    print("Success!\n")
                else:
                    print("Not enough money!\n")
                    card_operation(log_card, log_pin)
            else:
                print("Such a card does not exist.\n")
                card_operation(log_card, log_pin)
        else:
            print("Probably you made a mistake in the card number. Please try again!\n")
            card_operation(log_card, log_pin)
    elif user_operation_choice == 4:
        cur.execute(f"DELETE FROM card WHERE number = {log_card} AND pin = {log_pin}")
        conn.commit()
        print("The account has been closed!")
        return
    else:
        print("You have successfully logged out!")
        return


while True:
    if EXIT_FLAG:
        print("Bye!")
        break
    user_choice = int(input(user_invitation_str))
    if user_choice == 0:
        print("Bye!")
        break
    elif user_choice == 1:
        CARD_NUMBER, USER_PIN = card_creations()
        print(f"""Your card has been created
Your card number:
{CARD_NUMBER}
Your card PIN:
{USER_PIN}""")
    elif user_choice == 2:
        card_logging()


