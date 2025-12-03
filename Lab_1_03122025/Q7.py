'''7. WAP in python to display the grade system of KIIT University based on total marks
secured by a student in a semester. Use else..if ladder statement.'''
marks = int(input("Enter the total marks secured by the student: "))
if marks >= 90:
    grade = 'O'
elif marks >= 80:
    grade = 'E'
elif marks >= 70:
    grade = 'A'
elif marks >= 60:
    grade = 'B'
elif marks >= 50:
    grade = 'C'
elif marks >= 40:
    grade = 'D'
else:
    grade = 'F'
print(f"The grade secured by the student is: {grade}")