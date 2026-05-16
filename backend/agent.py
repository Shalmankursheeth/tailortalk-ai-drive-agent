import os
import functools
from datetime import datetime
from typing import TypedDict, Annotated, Sequence
import operator

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain_core.messages import ToolMessage
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from langchain_core.tools import tool
from langchain_groq import ChatGroq

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")

SERVICE_ACCOUNT_FILE = os.getenv(
    "SERVICE_ACCOUNT_FILE",
    "service_account.json"
)


@functools.lru_cache(maxsize=1)
def _get_drive_service():

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    return build(
        "drive",
        "v3",
        credentials=creds,
        cache_discovery=False
    )

def get_all_folder_ids(parent_id):

    drive = _get_drive_service()

    folder_ids = [parent_id]

    query = (
        f"'{parent_id}' in parents "
        "and mimeType='application/vnd.google-apps.folder'"
    )

    result = drive.files().list(
        q=query,
        fields="files(id,name)"
    ).execute()

    folders = result.get("files", [])

    for folder in folders:

        child_id = folder["id"]

        folder_ids.extend(
            get_all_folder_ids(child_id)
        )

    return folder_ids

def quick_drive_test():

    drive = _get_drive_service()

    result = drive.files().list(
        pageSize=5,
        fields="files(name)"
    ).execute()

    return result

def _mime_label(mime: str):

    labels = {
        "application/pdf": "📄 PDF",
        "application/vnd.google-apps.document": "📝 Google Doc",
        "application/vnd.google-apps.spreadsheet": "📊 Google Sheet",
        "application/vnd.google-apps.presentation": "📑 Google Slides",
        "application/vnd.google-apps.folder": "📁 Folder",
        "image/jpeg": "🖼️ JPEG Image",
        "image/png": "🖼️ PNG Image",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
    "📝 Word Document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
    "📊 Excel Spreadsheet",

"application/vnd.openxmlformats-officedocument.wordprocessingml.document":
    "📝 Word Document",

"video/mp4":
    "🎥 MP4 Video",
    }

    return labels.get(
        mime,
        f"📎 {mime.split('/')[-1]}"
    )



def _format_date(ts: str):

    try:
        return datetime.fromisoformat(
            ts.replace("Z", "+00:00")
        ).strftime("%b %d, %Y")

    except Exception:
        return ts



def _add_folder_scope(query: str):

    if not FOLDER_ID:
        return query

    folder_ids = get_all_folder_ids(FOLDER_ID)

    print("ALL FOLDER IDS:", folder_ids)

    folder_query = " or ".join([
        f"'{fid}' in parents"
        for fid in folder_ids
    ])

    return f"({folder_query}) and ({query})"
def _format_file_list(files: list):

    if not files:
        return "⚠️ No matching files found."

    lines = [f"Found **{len(files)} file(s)**:\n"]

    for f in files:

        name = f.get("name", "Untitled")

        mime = _mime_label(
            f.get("mimeType", "")
        )

        modified = _format_date(
            f.get("modifiedTime", "")
        )

        link = f.get("webViewLink", "")

        lines.append(f"**{name}**")

        lines.append(
            f"{mime} · Modified: {modified}"
        )

        if link:
            lines.append(
                f"[🔗 Open in Drive]({link})"
            )

        lines.append("")

    return "\n".join(lines)

@tool
def drive_search(query: str):
    """Search Google Drive using Drive API q syntax."""

    try:

        drive = _get_drive_service()

        scoped_query = _add_folder_scope(query)
        print("SCOPED QUERY:", scoped_query)

        result = drive.files().list(
            q=scoped_query,
            pageSize=20,
            fields="files(id,name,mimeType,modifiedTime,webViewLink,size)",
            orderBy="modifiedTime desc"
        ).execute()

        files = result.get("files", [])

        return _format_file_list(files)

    except HttpError as e:
        return f"Google Drive API Error: {e.reason}"

    except Exception as e:
        return f"Search Error: {str(e)}"

def get_all_folder_ids(parent_id):

    drive = _get_drive_service()

    folder_ids = [parent_id]

    query = (
        f"'{parent_id}' in parents "
        "and mimeType='application/vnd.google-apps.folder'"
    )

    result = drive.files().list(
        q=query,
        fields="files(id,name)"
    ).execute()

    folders = result.get("files", [])

    for folder in folders:

        child_id = folder["id"]

        folder_ids.extend(
            get_all_folder_ids(child_id)
        )

    return folder_ids

@tool
def list_all_files(max_files: int = 25):
    """List all files in Google Drive."""

    try:

        drive = _get_drive_service()

        kwargs = {
            "pageSize": max_files,
            "fields": "files(id,name,mimeType,modifiedTime,webViewLink,size)",
            "orderBy": "modifiedTime desc"
        }

        if FOLDER_ID:
            folder_ids = get_all_folder_ids(FOLDER_ID)
            kwargs["q"] = " or ".join([
    f"'{fid}' in parents"
    for fid in folder_ids
])

        result = drive.files().list(**kwargs).execute()

        files = result.get("files", [])

        return _format_file_list(files)

    except Exception as e:
        return f"List Error: {str(e)}"


@tool
def get_file_details(file_name: str):
    """Get details about a specific file."""

    query = f"name contains '{file_name}'"

    return drive_search(query)


TOOLS_LIST = [
    drive_search,
    list_all_files,
    get_file_details
]


SYSTEM_PROMPT = """
You are TailorTalk AI.

You are a Google Drive search assistant.

Your job:
Convert natural language requests
into accurate Google Drive API q queries.

You MUST ALWAYS use tools.

AVAILABLE TOOLS:
- drive_search
- list_all_files
- get_file_details

IMPORTANT:

Generate ONLY valid Google Drive q syntax
inside tool calls.

Never answer from memory.
Always retrieve results using tools.

If user asks:
- show all files
- list all files
- show everything

Use:
list_all_files

Google Drive query syntax examples:

PDF files:
mimeType='application/pdf'

Invoices:
name contains 'invoice'

Finance documents:
fullText contains 'finance'

Images:
mimeType contains 'image/'

Files after 2024:
modifiedTime > '2024-01-01T00:00:00'

Files before 2025:
modifiedTime < '2025-01-01T00:00:00'

Use RFC3339 timestamp format for dates.

Combine conditions using and.

Examples:

User:
find financial reports from 2024

Query:
fullText contains 'financial'
and modifiedTime > '2024-01-01T00:00:00'

User:
show invoice PDFs

Query:
mimeType='application/pdf'
and name contains 'invoice'

User:
show all spreadsheets

Query:
mimeType='application/vnd.google-apps.spreadsheet'
or
mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

User:
show Google Docs

Query:
mimeType='application/vnd.google-apps.document'
or
mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'

RULES:
- NEVER generate Python code
- NEVER explain implementation
- NEVER hallucinate files
- ALWAYS call tools
"""


class AgentState(TypedDict):
    messages: Annotated[
        Sequence[BaseMessage],
        operator.add
    ]



def _get_llm_with_tools():

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
        max_tokens=1200,
    )

    return llm.bind_tools(TOOLS_LIST)



def agent_node(state: AgentState):

    #response = llm.invoke(state["messages"])
    print("\n===== AGENT INPUT =====")
    print(state["messages"])

    llm = _get_llm_with_tools()

    response = llm.invoke(state["messages"])

    print("\n===== AI RESPONSE =====")
    print(response)

    print("\n===== TOOL CALLS =====")
    print(response.tool_calls)

    return {
    "messages": [response]
}



def should_continue(state: AgentState):

    last = state["messages"][-1]

    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"

    return END



def build_graph():

    tool_node = ToolNode(TOOLS_LIST)

    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )

    graph.add_edge("tools", END)

    return graph.compile()


_GRAPH = None



def _get_graph():

    global _GRAPH

    if _GRAPH is None:
        _GRAPH = build_graph()

    return _GRAPH



def get_agent_response(user_message: str, history: list):

    try:

        messages = [
            SystemMessage(content=SYSTEM_PROMPT)
        ]

        for msg in history[-10:]:

            role = msg.get("role")
            content = msg.get("content")

            if role == "user":
                messages.append(
                    HumanMessage(content=content)
                )

            elif role == "assistant":
                messages.append(
                    AIMessage(content=content)
                )


        messages.append(
            HumanMessage(content=user_message)
        )


        graph = _get_graph()

        final_state = graph.invoke({
            "messages": messages
        })


        for msg in reversed(final_state["messages"]):

    # Final AI response
            if isinstance(msg, AIMessage) and msg.content:
                return msg.content

    # Tool output fallback
            if isinstance(msg, ToolMessage):
                return msg.content

        return "I encountered an issue."


    except Exception as e:
        return f"⚠️ Error: {str(e)}"