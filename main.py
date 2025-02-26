import streamlit as st

form_values = {
    "name": None,
    "age": None
}

with st.form(key="form"):
    form_values["name"] = st.text_input("Enter your name")
    form_values["age"] = st.number_input("Enter your age")

    submit = st.form_submit_button("Submit")

    if submit:
        if not all(form_values.values()):
            st.warning("You must fill out all the values")
        else:
            st.balloons()
            st.subheader("Info:")
            for (k, v) in form_values.items():
                st.write(f"{k}: {v}")