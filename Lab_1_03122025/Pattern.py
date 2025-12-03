n = int(input("Enter the number of rows: "))

#range(n) means 0 to n-1
#range(n-i-1) means 0 to n-i-2
#range(m,n) means m to n-1


for i in range(n):
    for j in range(n - i - 1):
        print(" ", end=" ")
    for k in range(2 * i + 1):
        print("*", end=" ")
    print()


'''    *
     * * *
   * * * * *
 * * * * * * *
 n = 4'''