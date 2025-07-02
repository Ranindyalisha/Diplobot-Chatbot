import streamlit as st
import uuid
from google.oauth2 import service_account
from google.cloud import dialogflow_v2 as dialogflow

# --- Configuration ---
# Load credentials from Streamlit's secrets
try:
    creds_dict = st.secrets["google_credentials"]
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    PROJECT_ID = creds_dict["project_id"]
    st.session_state.creds_loaded = True
except (KeyError, FileNotFoundError):
    st.error("🚨 Google credentials not found in secrets.toml or Streamlit Cloud secrets.")
    st.info("Please follow the setup instructions to add your credentials.")
    st.stop()


# --- Dialogflow Interaction Function ---
def detect_intent_with_text(credentials, project_id, session_id, text, language_code="en-US"):
    """Sends a text query to the Dialogflow agent and returns the response."""
    session_client = dialogflow.SessionsClient(credentials=credentials)
    session_path = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    try:
        response = session_client.detect_intent(
            request={"session": session_path, "query_input": query_input}
        )
        return response.query_result.fulfillment_text
    except Exception as e:
        st.error(f"Error communicating with Dialogflow: {e}")
        return "Sorry, I'm having trouble connecting right now."


# --- Streamlit App Interface ---
st.title("🤖 Maya Chatbot")
st.write("I'm live! Deployed from GitHub to Streamlit Community Cloud.")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hey there! What's on your mind?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Talk to Maya..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = detect_intent_with_text(
                credentials, PROJECT_ID, st.session_state.session_id, prompt
            )
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})