import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from mcp import Client
from openai import AsyncOpenAI


REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / f".env.{os.getenv('APP_ENV', 'local')}"
load_dotenv(ENV_FILE)
openai = AsyncOpenAI()
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:9090/mcp")
SYSTEM_PROMPT = Path(__file__).with_name("system_prompt.txt").read_text(encoding="utf-8").strip()
READ_ONLY_TOOL_PREFIXES = ("get_", "list_", "ping")
WRITE_TOOL_PREFIXES = ("restart_", "trigger_", "deploy_", "delete_", "update_", "create_")


async def list_tools():

    async with Client(MCP_SERVER_URL) as client:

        result = await client.list_tools()

        print("Available MCP tools:")

        for tool in result.tools:
            print(f"- {tool.name}")
            print(f"  {tool.description}")


def convert_mcp_tools_to_openai(mcp_tools):

    tools = []

    for tool in mcp_tools:

        tools.append({
            "type": "function",
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.input_schema,
        })

    return tools


def categorize_tool(tool_name):

    if tool_name.startswith(READ_ONLY_TOOL_PREFIXES):
        return "read"

    if tool_name.startswith(WRITE_TOOL_PREFIXES):
        return "write"

    return "unknown"


def format_tool_arguments(arguments):

    if not arguments:
        return "no arguments"

    return ", ".join(
        f"{key}={value!r}"
        for key, value in arguments.items()
    )


def build_denied_output(tool_name):

    return (
        "User denied permission for write tool "
        f"'{tool_name}'."
    )


def build_unknown_output(tool_name):

    return (
        f"Tool '{tool_name}' is not classified as read or write. "
        "Do not use it until it is explicitly categorized."
    )


def build_approval_request(call, arguments):

    return {
        "status": "needs_approval",
        "tool_name": call.name,
        "arguments": arguments,
        "call_id": call.call_id,
        "message": (
            f"Approve write tool `{call.name}` with "
            f"{format_tool_arguments(arguments)}?"
        ),
    }


async def ask_llm(user_message, tools):

    response = await openai.responses.create(
        model="gpt-5",
        instructions=SYSTEM_PROMPT,
        input=user_message,
        tools=tools
    )

    return response


async def run_agent(
    user_message=None,
    conversation=None,
    approval_decision=None
):

    async with Client(MCP_SERVER_URL) as mcp_client:

        mcp_result = await mcp_client.list_tools()
        tools = convert_mcp_tools_to_openai(
            mcp_result.tools
        )

        if conversation is None:
            conversation = []

        if user_message is not None:
            conversation.append({
                "role": "user",
                "content": user_message
            })

        if approval_decision is not None:
            tool_name = approval_decision["tool_name"]
            if approval_decision["approved"]:
                tool_category = categorize_tool(tool_name)
                print(
                    f"Calling {tool_category} MCP tool: {tool_name}"
                )
                result = await mcp_client.call_tool(
                    tool_name,
                    approval_decision["arguments"]
                )
                conversation.append({
                    "type": "function_call_output",
                    "call_id": approval_decision["call_id"],
                    "output": str(result.content)
                })
            else:
                conversation.append({
                    "type": "function_call_output",
                    "call_id": approval_decision["call_id"],
                    "output": build_denied_output(tool_name)
                })

        while True:

            response = await openai.responses.create(
                model="gpt-5",
                input=conversation,
                tools=tools
            )

            conversation.extend(response.output)

            tool_calls = [
                item
                for item in response.output
                if item.type == "function_call"
            ]

            if not tool_calls:

                return {
                    "status": "completed",
                    "answer": response.output_text,
                    "conversation": conversation,
                }

            for call in tool_calls:

                tool_name = call.name
                arguments = json.loads(call.arguments)
                tool_category = categorize_tool(tool_name)

                if tool_category == "write":
                    return {
                        "conversation": conversation,
                        **build_approval_request(call, arguments),
                    }

                if tool_category == "unknown":
                    conversation.append({
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": build_unknown_output(tool_name)
                    })
                    continue

                print(
                    f"Calling {tool_category} MCP tool: {tool_name}"
                )

                result = await mcp_client.call_tool(
                    tool_name,
                    arguments
                )

                conversation.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": str(result.content)
                })


def confirm_write_tool(tool_name, arguments):

    prompt = (
        f"Tool '{tool_name}' is a write operation "
        f"({format_tool_arguments(arguments)}).\n"
        "Type 'yes' to allow it: "
    )
    confirmation = input(prompt).strip().lower()
    return confirmation == "yes"


async def main():

    print("DevOps AI Agent")
    print("Type 'exit' to quit.\n")
    conversation = []

    while True:

        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        result = await run_agent(
            user_message=user_input,
            conversation=conversation
        )
        conversation = result["conversation"]

        while result["status"] == "needs_approval":
            approved = confirm_write_tool(
                result["tool_name"],
                result["arguments"]
            )
            result = await run_agent(
                conversation=conversation,
                approval_decision={
                    "tool_name": result["tool_name"],
                    "arguments": result["arguments"],
                    "call_id": result["call_id"],
                    "approved": approved,
                }
            )
            conversation = result["conversation"]

        print(f"\nAI: {result['answer']}\n")


if __name__ == "__main__":
    asyncio.run(main())
