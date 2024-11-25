import streamlit as st
import random
import time
import model_load

# Initialize the app
st.title("Proteomics Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question about a protein..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            protein_name = model_load.extract_protein_name(prompt)

            context = model_load.fetch_protein_context(protein_name)

            response = model_load.generate_response(prompt, context)

            # Streamed response emulator
            def response_generator():
                for word in response.split():
                    yield word + " "
                    time.sleep(0.05)  

            st.write_stream(response_generator())

            st.session_state.messages.append({"role": "assistant", "content": response})

            # Refresh the app and update the chat history
            st.rerun()   
