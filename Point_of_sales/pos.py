import json
import os

class Item:
    def __init__(self, item_code, internal_price, discount, sale_price, quantity):
        self.item_code = item_code
        self.internal_price = internal_price
        self.discount = discount
        self.sale_price = sale_price
        self.quantity = quantity

    def line_total(self):
        return self.sale_price * self.quantity

    def to_dict(self):
        return {
            'internal_price': self.internal_price,
            'discount': self.discount,
            'sale_price': self.sale_price,
            'quantity': self.quantity
        }

class Basket:
    def __init__(self):
        self.items = {}
        self.bills = {}
        self.cart = []
        self.current_bill_number = 1000
        self.load_last_bill_number()

    def load_last_bill_number(self):
        try:
            with open("tax_transactions.txt", "r", encoding="utf-8") as f:
                max_bill_number = 0
                for line in f:
                    try:
                        bill_data = json.loads(line.strip())
                        if "bill_number" in bill_data:
                            max_bill_number = max(max_bill_number, bill_data["bill_number"])
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON from line: {line.strip()}")
                self.current_bill_number = max_bill_number + 1 if max_bill_number > 0 else 1000
        except FileNotFoundError:
            print("Tax transactions file not found. Starting with bill number 1000.")

    def add_item(self):
        while True:
            print("\nAdding Item:")
            while True:
                item_code = input("\nEnter Item Code: ").strip()
                if item_code:
                    if item_code in self.items:
                        print(f"Item with code '{item_code}' already exists in the basket.")
                    else:
                        break
                else:
                    print("\nItem code cannot be empty. Please enter a value.")

            internal_price = self.get_float("Enter Internal Price: Rs.")
            discount = self.get_optional_float("Enter Discount(%) (leave blank for no discount): ")
            sale_price = self.get_float("Enter Sale Price: Rs.")
            quantity = self.get_int("Enter Quantity: ")

            self.items[item_code] = Item(item_code, internal_price, discount, sale_price, quantity)
            print(f"\nItem '{item_code}' added to the basket.")

            if not self.ask_yes_no("Do you want to add more items?"):
                return

    def show_basket(self):
        if not self.items:
            print("\nYour basket is empty.")
        else:
            print("\n---- Shopping Basket ----")
            for i, (item_code, item) in enumerate(self.items.items(), 1):
                print(f"{i}. Item Code: {item_code}, "
                      f"Internal Price: Rs.{item.internal_price}, "
                      f"Discount: {item.discount}%, "
                      f"Sale Price: Rs.{item.sale_price}, "
                      f"Quantity: {item.quantity}, "
                      f"Line Total: {item.line_total()}")

    def remove_item(self):
        if not self.items:
            print("\nYour basket is empty.")
            return
        while True:
            print("\n---- Current Shopping Basket ----")
            line_map = {}
            for i, (code, item) in enumerate(self.items.items(), 1):
                print(f"{i}. Item Code: {code}, Internal Price: Rs.{item.internal_price}, "
                      f"Sale Price: Rs.{item.sale_price}, Quantity: {item.quantity}")
                line_map[str(i)] = code

            print("\nEnter M to go back to main menu.")
            choice = input("Enter Item line to remove: ").strip()
            if choice.lower() == 'm':
                return
            elif choice in line_map:
                del self.items[line_map[choice]]
                print(f"Item at line {choice} removed from the basket.")
                break
            else:
                print("\nInvalid line number.")
                if not self.ask_yes_no("Do you want to try again?"):
                    return

    def update_item(self):
        if not self.items:
            print("\nYour basket is empty.")
            return
        while True:
            print("\n---- Current Shopping Basket Details ----\n")
            line_map = {}
            for i, (code, item) in enumerate(self.items.items(), 1):
                print(f"{i}. Item Code: {code}, Internal Price: Rs.{item.internal_price}, "
                      f"Discount: {item.discount}%, Sale Price: Rs.{item.sale_price}, Quantity: {item.quantity}")
                line_map[str(i)] = code

            print("\nEnter M to go back to main menu.")
            line = input("Enter Item line to update: ").strip()
            if line.lower() == 'm':
                return
            elif line in line_map:
                code = line_map[line]
                item = self.items[code]
                try:
                    d = input("Enter new Discount(%)(leave blank to skip): ").strip()
                    if d:
                        item.discount = float(d)
                    s = input("Enter new Sale Price (leave blank to skip): Rs.").strip()
                    if s:
                        item.sale_price = float(s)
                    q = input("Enter new Quantity (leave blank to skip): ").strip()
                    if q:
                        item.quantity = int(q)
                    print(f"Item '{code}' updated.")
                except ValueError:
                    print("Invalid input. Please enter numeric values.")
            else:
                print(f"\nItem with line '{line}' not found.")
                if not self.ask_yes_no("Do you want to try again?"):
                    return

    def generate_bill(self):
        if not self.items:
            print("Your basket is empty. Cannot generate bill.")
            return

        self.cart = []
        for item in self.items.values():
            line_total = item.line_total()
            item_data = {
                "item_code": item.item_code,
                "quantity": item.quantity,
                "sale_price": "{:.2f}".format(item.sale_price),
                "line_total": "{:.2f}".format(line_total)
            }
            json_string = json.dumps(item_data, sort_keys=True, indent=2)
            checksum = self.calculate_checksum(json_string)

            self.cart.append({
                "item_code": item.item_code,
                "quantity": item.quantity,
                "internal_price": item.internal_price,
                "discount": item.discount,
                "sale_price": item.sale_price,
                "line_total": line_total,
                "checksum": checksum
            })

        total_amount = sum(i['line_total'] for i in self.cart)
        print(f"\n------------ BILL #{self.current_bill_number} ------------")
        print(f"{'Item Code':<12}{'Qty':<6}{'Price':<8}{'Total':<10}{'Checksum'}")
        for i in self.cart:
            print(f"{i['item_code']:<12}{i['quantity']:<6}{i['sale_price']:<8}{i['line_total']:<10}{i['checksum']}")
        print("-" * 50)
        print(f"Total Amount: {total_amount}")
        print("-" * 50)

        bill_data = {
            "bill_number": self.current_bill_number,
            "items": self.cart,
            "total_amount": total_amount
        }

        with open("tax_transactions.txt", "a", encoding="utf-8") as f:
            json.dump(bill_data, f)
            f.write('\n')

        self.bills[self.current_bill_number] = bill_data
        self.items.clear()
        self.cart.clear()
        self.current_bill_number += 1
        print("Bill generated and written to tax_transactions.txt")

    def search_bill(self):
        bill_no = input("Enter the bill number to search: ").strip()
        if not bill_no.isdigit():
            print("Invalid bill number format.")
            return

        bill_number = int(bill_no)
        found = False

        try:
            with open("tax_transactions.txt", "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        bill_data = json.loads(line.strip())
                        if bill_data.get("bill_number") == bill_number:
                            print(f"\n----- Bill Number: {bill_number} -----")
                            print(f"{'Item Code':<12}{'Qty':<6}{'Price':<8}{'Total':<10}{'Checksum'}")
                            for item in bill_data["items"]:
                                print(f"{item['item_code']:<12}{item['quantity']:<6}{item['sale_price']:<8}"
                                      f"{item['line_total']:<10}{item['checksum']}")
                            print("-" * 50)
                            print(f"Total Amount: Rs.{bill_data['total_amount']:.2f}")
                            print("-" * 50)
                            found = True
                            break
                    except json.JSONDecodeError:
                        print(f"Error decoding line: {line.strip()}")
        except FileNotFoundError:
            print("Tax transactions file not found.")

        if not found:
            print(f"\nBill number {bill_number} not found.")

    def open_tax_file(self):
        if not self.bills:
            print("\nTAX files have not been generated yet.")
            return
        filename = "tax_transactions.txt"
        try:
            if os.name == 'nt':
                os.startfile(filename)
            elif os.name == 'posix':
                os.system(f"open {filename}")
            else:
                print(f"Cannot automatically open file. File path: {os.path.abspath(filename)}")
        except Exception as e:
            print(f"An error occurred: {e}")

    @staticmethod
    def calculate_checksum(data_string):
        return sum(c.isupper() or c.islower() or c.isdigit() for c in data_string)

    @staticmethod
    def ask_yes_no(prompt):
        while True:
            answer = input(f"{prompt} (Y/N): ").strip().upper()
            if answer in ("Y", "N"):
                return answer == "Y"
            print("Invalid input.")

    @staticmethod
    def get_float(prompt):
        while True:
            try:
                return float(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a number.")

    @staticmethod
    def get_int(prompt):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Invalid input. Please enter an integer.")

    @staticmethod
    def get_optional_float(prompt):
        while True:
            try:
                value = input(prompt).strip()
                return float(value) if value else 0.0
            except ValueError:
                print("Invalid input.")