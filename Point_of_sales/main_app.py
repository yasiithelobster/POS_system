from Point_of_sales.pos import Basket

pos = Basket()

print("\n------------------------------------")
print("| Welcome to Point of Sales System |")
print("------------------------------------")

while True:
    print("\n---- MAIN MENU -----")
    print("1. Add items")
    print("2. Remove an item")
    print("3. Show basket")
    print("4. Update an item")
    print("5. Generate a bill")
    print("6. Search a bill")
    print("7. Open TAX transaction file")
    print("8. Exit")

    try:
        choice = int(input("\nEnter your choice: "))
        match choice:
            case 1:
                pos.add_item()
            case 2:
                pos.remove_item()
            case 3:
                pos.show_basket()
            case 4:
                pos.update_item()
            case 5:
                pos.generate_bill()
            case 6:
                pos.search_bill()
            case 7:
                pos.open_tax_file()
            case 8:
                print("Exiting program...")
                break
            case _:
                print("Invalid choice. Please enter a number between 1 and 8.")
    except ValueError:
        print("Invalid choice. Please enter a number.")