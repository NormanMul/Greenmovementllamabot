import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import io

# Set Streamlit page configuration
st.set_page_config(page_title="WasteWiseChatbot", layout="centered")

# Load and display the logo in the sidebar
logo = "logo.jpg"  # Replace with your logo file name
st.sidebar.image(logo, use_column_width=True)

# Sidebar for API key input and temperature slider
st.sidebar.title("Configuration")
api_key_input = st.sidebar.text_input("API Key", type="password", key="api_key")
temperature = st.sidebar.slider('Temperature', min_value=0.0, max_value=1.0, value=0.7, step=0.1)

# Store the API key in the session state
if api_key_input:
    os.environ["GROQ_API_KEY"] = api_key_input

api_key = os.getenv("GROQ_API_KEY", None)
if not api_key:
    st.sidebar.error("Please enter your API key to continue.")
    st.stop()

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

if "plots" not in st.session_state:
    st.session_state["plots"] = []

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

# Function to parse the prompt and generate a graph
def parse_and_generate_graph(prompt):
    prompt = prompt.lower().strip()
    words = prompt.split()
    try:
        x_axis = words[words.index("dan") - 1]
        y_axis = words[words.index("dan") + 1]
        graph_type = prompt.split()[0]
        fig, ax = plt.subplots()
        if graph_type == "line":
            ax.plot(data[x_axis], data[y_axis])
        elif graph_type == "bar":
            ax.bar(data[x_axis], data[y_axis])
        elif graph_type == "scatter":
            ax.scatter(data[x_axis], data[y_axis])
        ax.set_title(f"{graph_type.title()} Plot of {y_axis} vs {x_axis}")
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error generating graph: {e}")

# User input processing
question = st.text_input("Ask a question or make a request:")
if question:
    if any(word in question.lower() for word in ['line', 'bar', 'scatter']):
        parse_and_generate_graph(question)
    else:
        answer = generate_response(question, temperature)
        st.session_state["responses"].append({"question": question, "answer": answer})

# Display previous responses
for entry in reversed(st.session_state["responses"]):
    st.write(f"**Q:** {entry['question']}\n**A:** {entry['answer']}")
    st.write("---")  # Separator line
