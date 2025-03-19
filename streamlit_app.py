import streamlit as st
from research_assistant import get_summary, get_followup_answer, generate_response

# Helper function for modifying the summary
def modify_summary(instructions, current_summary, base_context, temperature=0.7):
    prompt = f"""{base_context}

Current Summary:
{current_summary}

Please modify the above summary according to these instructions:
{instructions}

Return only the modified summary."""
    modified_summary = generate_response(prompt, temperature=temperature)
    return modified_summary

# Title and instructions
st.title("Deep Research")
st.write("Enter a YouTube video URL to generate a transcript summary.")

# Initialize session state variables if they don't exist
if "base_context" not in st.session_state:
    st.session_state.base_context = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "summary_confirmed" not in st.session_state:
    st.session_state.summary_confirmed = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of dicts: {"question": ..., "answer": ...}
if "url" not in st.session_state:
    st.session_state.url = ""
if "modify_mode" not in st.session_state:
    st.session_state.modify_mode = False

# URL input section (only if summary not generated yet)
if not st.session_state.base_context:
    st.session_state.url = st.text_input("YouTube URL", st.session_state.url)

if st.button("Generate Summary") and st.session_state.url and not st.session_state.base_context:
    try:
        base_context, summary = get_summary(st.session_state.url, temperature=0.7)
        st.session_state.base_context = base_context
        st.session_state.summary = summary
        st.session_state.chat_history = []  # reset chat history for a new video
        st.session_state.summary_confirmed = False
        st.session_state.modify_mode = False
    except Exception as e:
        st.error(f"Error generating summary: {e}")

# Summary modification/confirmation stage
if st.session_state.summary and not st.session_state.summary_confirmed:
    st.markdown("### Summary")
    st.markdown(st.session_state.summary)
    col1, col2 = st.columns(2)
    # When "Modify Summary" is clicked, set modify_mode to True so that the form remains visible
    if col1.button("Modify Summary"):
        st.session_state.modify_mode = True
        st.rerun()
    # "Confirm Summary" sets the summary as final
    if col2.button("Confirm Summary"):
        st.session_state.summary_confirmed = True
        st.session_state.modify_mode = False
        st.rerun()
    # If modification mode is active, display the modification form
    if st.session_state.modify_mode:
        with st.form(key="summary_mod_form", clear_on_submit=True):
            mod_instructions = st.text_input("Modification instructions for summary", value="")
            submit_mod = st.form_submit_button("Submit Modification")
            if submit_mod and mod_instructions:
                try:
                    new_summary = modify_summary(mod_instructions, st.session_state.summary, st.session_state.base_context, temperature=0.7)
                    st.session_state.summary = new_summary  # Overwrite original summary
                    st.session_state.modify_mode = False  # Exit modification mode
                    st.rerun()  # Force immediate rerun to update the UI with the modified summary
                except Exception as e:
                    st.error(f"Error modifying summary: {e}")

# Once the summary is confirmed, move to follow-up Q&A
if st.session_state.summary_confirmed:
    st.markdown("### Confirmed Summary")
    st.markdown(st.session_state.summary)

    # Follow-up question form for new questions
    with st.form(key="followup_form", clear_on_submit=True):
        followup = st.text_input("Follow-up question", value="")
        submit_followup = st.form_submit_button("Get Answer")
        if submit_followup and followup:
            try:
                answer = get_followup_answer(st.session_state.base_context, followup, temperature=0.7)
                st.session_state.chat_history.append({"question": followup, "answer": answer})
                #st.rerun()  # Force a rerun to update the conversation history immediately
            except Exception as e:
                st.error(f"Error generating follow-up answer: {e}")
    
    # Display conversation history
    if st.session_state.chat_history:
        st.markdown("### Conversation History")
        for idx, item in enumerate(st.session_state.chat_history, start=1):
            st.markdown(f"**Q{idx}:** {item['question']}")
            st.markdown(f"**A{idx}:** {item['answer']}")
