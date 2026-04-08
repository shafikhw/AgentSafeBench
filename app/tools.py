from app.state import current_state

def read_inbox(message_id: str) -> str:
    msg = current_state.inbox.get(message_id)
    if not msg:
        res = f"Message ID {message_id} not found."
    else:
        sender = msg.get("sender", "Unknown")
        subject = msg.get("subject", "No Subject")
        body = msg.get("body", "")
        res = f"From: {sender}\nSubject: {subject}\nBody:\n{body}"
    current_state.record_tool_call("read_inbox", {"message_id": message_id}, "executed", res[:50])
    return res

def search_notes(query: str) -> str:
    matches = [note for note in current_state.notes if query.lower() in note.lower()]
    if matches:
        res = "\n---\n".join(matches)
    else:
        res = "No notes matched your query."
    current_state.record_tool_call("search_notes", {"query": query}, "executed", res[:50])
    return res

def read_file(filename: str) -> str:
    content = current_state.files.get(filename)
    if content is None:
        res = f"File {filename} not found."
    else:
        res = content
    current_state.record_tool_call("read_file", {"filename": filename}, "executed", res[:50])
    return res

def draft_email(recipient: str, subject: str, body: str) -> str:
    draft = {"recipient": recipient, "subject": subject, "body": body}
    current_state.drafts.append(draft)
    res = "Email successfully drafted."
    current_state.record_tool_call("draft_email", draft, "executed", res[:50])
    return res

def send_email(recipient: str, subject: str, body: str) -> str:
    sent = {"recipient": recipient, "subject": subject, "body": body}
    current_state.sent_emails.append(sent)
    res = "Email successfully sent."
    current_state.record_tool_call("send_email", sent, "executed", res[:50])
    return res

# OpenAI Tool definitions
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "read_inbox",
            "description": "Read a message from the email inbox by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "The exact ID of the message to read."}
                },
                "required": ["message_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_notes",
            "description": "Searches for notes containing the specific text query. Keep queries short.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search term."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the content of a file from the server.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of the file to read."}
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "draft_email",
            "description": "Draft an email without sending it yet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "Email address of the recipient."},
                    "subject": {"type": "string", "description": "Subject of the email."},
                    "body": {"type": "string", "description": "Text body of the email."}
                },
                "required": ["recipient", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email immediately.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "Email address of the recipient."},
                    "subject": {"type": "string", "description": "Subject of the email."},
                    "body": {"type": "string", "description": "Text body of the email."}
                },
                "required": ["recipient", "subject", "body"]
            }
        }
    }
]

TOOL_FUNCTIONS = {
    "read_inbox": read_inbox,
    "search_notes": search_notes,
    "read_file": read_file,
    "draft_email": draft_email,
    "send_email": send_email
}
