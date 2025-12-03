'''3. WAP in python to convert given paisa into its equivalent rupee and paisa as per the
following format.
Example. 550 paisa = 5 Rupee and 50 paisa'''
paisa = int(input("Enter amount in paisa: "))
rupee = paisa // 100 # Integer division to get rupees
remaining_paisa = paisa % 100
print(paisa, "paisa =", rupee, "Rupee and", remaining_paisa, "paisa")