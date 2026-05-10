import streamlit as st
import json
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_mail_from_topic(topic):
    prompt = f"""
You are an email writing assistant.
Generate a professional email for this topic:
{topic}

Return ONLY valid JSON in this format:
{{
  "subject": "short clear subject",
  "body": "professional email body without signature",
  "signature": "best possible sign-off name/designation inferred from topic context"
}}

Rules:
- NEVER invent or guess a signature.
- NEVER use generic signatures like "Team Member", "Employee", "Your Name", "Sender", "ABC Team", or placeholders.
- Use a non-empty signature ONLY when sender identity is explicitly present in topic/context.
- If sender identity is not explicitly present, return an empty string for "signature".

Examples:
1) Topic: "Write leave mail to Vaishali Kale for 3 days leave due to uncle accident"
Output:
{{
  "subject": "Request for 3 Days Leave (11th May to 13th May)",
  "body": "Dear Vaishali Kale,\\n\\nI am writing to request leave for three days from 11th May to 13th May due to an accident involving my uncle. I need to be with my family during this time.\\n\\nI apologize for any inconvenience and will ensure a smooth handover of pending work.",
  "signature": ""
}}

2) Topic: "Write leave mail to Vaishali Kale from Arindam Das, Software Engineer"
Output:
{{
  "subject": "Leave Request",
  "body": "Dear Vaishali Kale,\\n\\nPlease approve my leave request.",
  "signature": "Arindam Das\\nSoftware Engineer"
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        raw_reply = response.choices[0].message.content or "{}"
        mail_json = json.loads(raw_reply)

        subject = str(mail_json.get("subject", "")).strip()
        body = str(mail_json.get("body", "")).strip()
        signature = str(mail_json.get("signature", "")).strip()

        if not subject or not body:
            raise ValueError("Missing subject/body in generated JSON")

        return subject, body, signature
    except Exception:
        fallback_subject = f"Regarding: {topic}"
        fallback_body = (
            f"Hello,\n\n"
            f"I hope you are doing well.\n\n"
            f"I am writing regarding {topic}. Please let me know a convenient time "
            f"to discuss this further."
        )
        return fallback_subject, fallback_body, ""


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
        else:
            st.session_state.mail_data["cc"] = ""

        st.session_state.mail_step = "bcc"

        return "Enter BCC email (or type skip):"

    # BCC STEP
    elif step == "bcc":

        if user_input.lower() != "skip":
            st.session_state.mail_data["bcc"] = user_input
        else:
            st.session_state.mail_data["bcc"] = ""

        st.session_state.mail_step = "topic"

        return "Enter the topic of the email (AI will generate subject and body):"

    # TOPIC STEP (AI GENERATED SUBJECT + BODY)
    elif step == "topic":
        st.session_state.mail_data["topic"] = user_input
        subject, body, signature = generate_mail_from_topic(user_input)
        st.session_state.mail_data["subject"] = subject
        st.session_state.mail_data["body"] = body
        st.session_state.mail_data["signature"] = signature

        if not signature:
            st.session_state.mail_step = "signature"
            return "Could not infer signature from topic. Please enter signature (name/designation):"

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

{data["signature"]}

Type SEND to send email
Type EXIT to cancel
'''

    # SIGNATURE STEP (USER PROVIDED FALLBACK)
    elif step == "signature":
        st.session_state.mail_data["signature"] = user_input
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

{data["signature"]}

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
                "topic": "",
                "subject": "",
                "body": "",
                "signature": ""
            }

            return result

        return "Type SEND to send or EXIT to cancel"

    return "Mail workflow error."