import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Set Streamlit page configuration
st.set_page_config(page_title="Greenmovement", layout="centered")

# Load and display the logo in the sidebar
logo = "logo.jpg"
st.sidebar.image(logo, use_column_width=True)

st.sidebar.title("Configuration")
input_password = st.sidebar.text_input("Enter Password", type="password")

correct_password = "greenmovement"
if input_password != correct_password:
    st.sidebar.error("Incorrect password. Access denied.")
    st.stop()

model_options = {
    "Llama 70B Versatile": "llama-3.1-70b-versatile",
    "Llama 8B Instant": "llama-3.1-8b-instant",
    "Llama Guard 8B": "llama-guard-3-8b"
}
selected_model = st.sidebar.selectbox("Select Model", list(model_options.keys()))
api_key = st.secrets["groq"]["api_key"]

@st.cache(allow_output_mutation=True)
def load_data(file_path):
    return pd.read_csv(file_path)

data = load_data('datasampah1.csv')

# Function to prepare data as context for the AI
def prepare_data_context(data):
    return "\n".join([f"{row.Index}: {', '.join(map(str, row))}" for row in data.itertuples()])

# Include a checkbox to display data if necessary
if st.checkbox('Show CSV Data'):
    st.write(data)

if "responses" not in st.session_state:
    st.session_state["responses"] = []

def generate_response(prompt, temperature=0.7):
    from groq import Groq
    client = Groq(api_key=api_key)
    context = prepare_data_context(data.head(50))  # Sending only the first 50 rows as context
    full_prompt = f"Based on the following data:\n{context}\n\nQuestion: {prompt}"
    try:
        response = client.chat.completions.create(
            model=model_options[selected_model],
            messages=[
                {"role": "system", "content": "You are a helpful assistant equipped with the following data."},
                {"role": "user", "content": full_prompt},
            ],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return "I'm sorry, I couldn't generate a response."

question = st.text_input("Ask a question or make a request:")
if question:
    answer = generate_response(question)
    st.session_state["responses"].append({"question": question, "answer": answer})

for entry in reversed(st.session_state["responses"]):
    st.write(f"**Q:** {entry['question']}\n**A:** {entry['answer']}")
    st.write("---")
