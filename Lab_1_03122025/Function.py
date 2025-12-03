def func():
    a = int(input("Enter a number "))
    b = int(input("Enter a number again "))
    print(a+b)
    a = [1,2,3,4]
    for i in a:
        print(i ," ",end='')
def main():
    func()
if __name__ == '__main__':
    main()