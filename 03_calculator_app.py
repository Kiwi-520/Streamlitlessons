
import streamlit as st
st.title('Calculator App')

num1 = st.number_input("Enter 1st Number: ")

operation = st.selectbox('Choose Option',['+', '-', '/', '*', '%', '**'])

num2 = st.number_input("Enter 2nd Number: ")

st.slider("Pick a value", 0, 100, 50)

if operation == '+':
    result =  num1 + num2

if operation == '-':
    result =  num1 - num2

if operation == '*':
    result =  num1 * num2

if operation == '/':
    result =  num1 / num2

if operation == '%':
    result =  num1 % num2

if operation == '**':
    result =  num1 ** num2

st.write(f'Results: {result}')

st.success(f'Your answer is: {result}')

