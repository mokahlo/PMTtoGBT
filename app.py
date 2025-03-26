import streamlit as st
import os
import tempfile
import pypff

def extract_emails_from_pst(pst_file_path, output_dir):
    pst = pypff.file()
    pst.open(pst_file_path)
    root_folder = pst.get_root_folder()
    process_folder(root_folder, output_dir)
    pst.close()

def process_folder(folder, output_dir):
    folder_name = folder.get_display_name()
    folder_path = os.path.join(output_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    for message in folder.sub_messages:
        extract_message(message, folder_path)

    for subfolder in folder.sub_folders:
        process_folder(subfolder, folder_path)

def extract_message(message, output_dir):
    subject = message.get_subject() or "No_Subject"
    sender = message.get_sender_name() or "Unknown_Sender"
    recipients = message.get_recipient_names() or "Unknown_Recipients"
    body = message.get_plain_text_body() or "No Body Content"

    safe_subject = "".join([c if c.isalnum() or c in " ._-()" else "_" for c in subject])[:100]
    output_file_path = os.path.join(output_dir, f"{safe_subject}.txt")

    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(f"Subject: {subject}\n")
        f.write(f"From: {sender}\n")
        f.write(f"To: {recipients}\n\n")
        f.write(body)

st.title("PST Email Extractor")

uploaded_file = st.file_uploader("Upload a .pst file", type=["pst"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pst") as temp_pst:
        temp_pst.write(uploaded_file.read())
        temp_pst_path = temp_pst.name

    with tempfile.TemporaryDirectory() as temp_output_dir:
        st.info("Extracting emails, please wait...")
        extract_emails_from_pst(temp_pst_path, temp_output_dir)
        st.success("Extraction complete!")

        st.download_button(
            label="Download Extracted Emails as ZIP",
            data=shutil.make_archive(temp_output_dir, 'zip', temp_output_dir),
            file_name="extracted_emails.zip"
        )
