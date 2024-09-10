import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Set Streamlit page configuration
st.set_page_config(page_title="Greenmovement", layout="centered")

# Load and display the logo in the sidebar
logo = "logo.jpg"  # Replace with your logo file name
st.sidebar.image(logo, use_column_width=True)

# Sidebar for password input and model selection
st.sidebar.title("Configuration")
input_password = st.sidebar.text_input("Enter Password", type="password")
model_options = {
    "Llama 70B": "llama3-70b-4096",
    "Llama 8B": "llama3-8b-8192"
}
selected_model = st.sidebar.selectbox("Select Model", list(model_options.keys()))

# Preset password for API access
correct_password = "greenmovement"

# Verify the password and load API key from Streamlit secrets
if input_password != correct_password:
    st.sidebar.error("Incorrect password. Access denied.")
    st.stop()
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

if "plots" not in st.session_state:
    st.session_state["plots"] = []

# Function to generate responses using Groq Llama API
def generate_response(prompt, temperature=0.7):
    from groq import Groq
    client = Groq(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=model_options[selected_model],
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
    
    # Check if the necessary keywords are present in the prompt
    if "plot" not in prompt or "dan" not in words:
        st.error("Please specify the type of plot ('line', 'bar', 'scatter') and the columns for the plot using the word 'dan' between them (e.g., 'buat line plot Column1 dan Column2').")
        return

    try:
        dan_index = words.index("dan")
        x_axis = words[dan_index - 1]
        y_axis = words[dan_index + 1]
        plot_index = words.index("plot")
        graph_type = words[plot_index - 1]
    except (ValueError, IndexError):
        st.error("Error parsing input. Make sure the format is correct: 'buat <type> plot <Column1> dan <Column2>'.")
        return

    if x_axis not in data.columns or y_axis not in data.columns:
        st.error("The specified columns do not exist in the data. Please check the column names and try again.")
        return

    # Generate the graph
    st.subheader(f"{graph_type.title()} Plot of {y_axis} vs {x_axis}")
    fig, ax = plt.subplots()
    if graph_type == "line":
        ax.plot(data[x_axis], data[y_axis])
    elif graph_type == "bar":
        ax.bar(data[x_axis], data[y_axis])
    elif graph_type == "scatter":
        ax.scatter(data[x_axis], data[y_axis])
    ax.set_title(f"{graph_type.title()} Plot of {y_axis} vs {x_axis}")
    st.pyplot(fig)
    plt.close(fig)

# User input processing
question = st.text_input("Ask a question or make a request (e.g., 'buat line plot Column1 dan Column2'):")
if question:
    if "buat" in question.lower() and "plot" in question.lower():
        parse_and_generate_graph(question)
    else:
        answer = generate_response(question)
        st.session_state["responses"].append({"question": question, "answer": answer})

# Display previous responses and plots
for entry in reversed(st.session_state["responses"]):
    st.write(f"**Q:** {entry['question']}\n**A:** {entry['answer']}")
    st.write("---")  # Separator line
