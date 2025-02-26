import streamlit as st

if "users" not in st.session_state:
    st.session_state.users = []

def add_user():
    user_name = st.text_input("Enter user's name")
    if st.button("Add User"):
        if user_name and user_name not in st.session_state.users:
            st.session_state.users.append({
                "name": user_name,
                "spent": 0
            })
            st.success("User added")
        else:
            st.error("Something went wrong")

def list_users():
    if not st.session_state.users:
        st.write("No users added yet.")
    else:
        for user in st.session_state.users:
            st.write(f"{user["name"]} spent {user["spent"]}")

def add_expense():
    user = st.selectbox("Choose a user:", [i["name"] for i in st.session_state.users])
    amount = st.number_input("Enter the amount of money spent: ", step=float(10))
    if st.button("Add Expense"):
        for i in st.session_state.users:
            if i["name"] == user:
                i["spent"] += amount
                st.success(f"Added {amount} to {i["name"]}")
                st.rerun()

def settle_up():
    if st.button("Settle Up"):
      user_balances = {}
      sum = 0
      count = 0
      for i in st.session_state.users:
          amount = i["spent"]
          sum = sum + amount
      print(user_balances)
      average = sum/len(st.session_state.users)
      for i in st.session_state.users:
          name = i["name"]
          spent = i["spent"]
          if spent <= 0:
              user_balances[count] = f"{name} owes {average}"
          elif spent <= average:
              user_balances[count] = f"{name} is owed {average - spent}"
          else:
              user_balances[count] = f"{name} is owed {spent - average}"
          count += 1
      print(user_balances)
      for key in user_balances:
          st.info(user_balances[key])
          
              

st.title("Splitwise App")
st.divider()
st.subheader("Add Users")
add_user()
st.divider()
st.subheader("List Users")
list_users()
st.divider()
st.subheader("Add Expense")
add_expense()
st.divider()
st.subheader("Settle Up")
settle_up()