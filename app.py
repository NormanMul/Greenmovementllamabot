import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import io

# Set Streamlit page configuration
st.set_page_config(page_title="GreenMovement", layout="centered")

# Load and display the logo in the sidebar
logo = "logo.jpg"  # Replace with your logo file name
st.sidebar.image(logo, use_column_width=True)

# Load API key from Streamlit secrets
api_key = st.secrets["groq"]["api_key"]

# Load CSV data
@st.cache
def load_data(file_path):
    return pd.read_csv(file_path)

data = load_data('datasampah1.csv')

# Display data if necessary
if st.checkbox('Show CSV Data'):
    st.write(data)

# Initialize session state to store responses and plots
if "responses" not in st.session_state:
    st.session_state["responses"] = []

# Function to generate responses using the Groq Llama API
def generate_response(prompt, temperature=0.7):
    from groq import Groq
    client = Groq(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return "I'm sorry, I couldn't generate a response."

# User input processing
question = st.text_input("Ask a question or make a request:")
if question:
    answer = generate_response(question)
    st.session_state["responses"].append({"question": question, "answer": answer})

# Display previous responses
for entry in reversed(st.session_state["responses"]):
    st.write(f"**Q:** {entry['question']}\n**A:** {entry['answer']}")
    st.write("---")  # Separator line
