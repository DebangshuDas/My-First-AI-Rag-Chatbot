import streamlit as st


def process_mail_flow(user_input):

    step = st.session_state.mail_step

    # EXIT
    if user_input.lower() == "exit":

        st.session_state.mode = "normal"
        st.session_state.mail_step = None

        return "Mail workflow cancelled."

    # TO STEP
    if step == "to":

        st.session_state.mail_data["to"] = user_input
        st.session_state.mail_step = "cc"

        return "Enter CC email (or type skip):"

    # CC STEP
    elif step == "cc":

        if user_input.lower() != "skip":
            st.session_state.mail_data["cc"] = user_input

        st.session_state.mail_step = "bcc"

        return "Enter BCC email (or type skip):"

    # BCC STEP
    elif step == "bcc":

        if user_input.lower() != "skip":
            st.session_state.mail_data["bcc"] = user_input

        st.session_state.mail_step = "subject"

        return "Enter email subject:"

    # SUBJECT STEP
    elif step == "subject":

        st.session_state.mail_data["subject"] = user_input
        st.session_state.mail_step = "body"

        return "Enter email body:"

    # BODY STEP
    elif step == "body":

        st.session_state.mail_data["body"] = user_input
        st.session_state.mail_step = "confirm"

        data = st.session_state.mail_data

        return f'''
EMAIL PREVIEW

To: {data["to"]}
CC: {data["cc"]}
BCC: {data["bcc"]}

Subject:
{data["subject"]}

Body:
{data["body"]}

Type SEND to send email
Type EXIT to cancel
'''

    # CONFIRM STEP
    elif step == "confirm":

        if user_input.lower() == "send":

            from send_mail import send_email

            result = send_email(
                st.session_state.mail_data
            )

            # RESET
            st.session_state.mode = "normal"
            st.session_state.mail_step = None

            st.session_state.mail_data = {
                "to": "",
                "cc": "",
                "bcc": "",
                "subject": "",
                "body": ""
            }

            return result

        return "Type SEND to send or EXIT to cancel"

    return "Mail workflow error."