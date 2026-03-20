"""
mcp_server.py - MoMoA MCP Bridge for Claude Desktop

What this does:
  Runs as an MCP server that Claude Desktop can call.
    When Claude calls the run_momoa_task or ask_momoa_question tool,
      this script connects to your running MoMoA server over WebSocket,
        sends the task, collects all progress logs, and returns the final
          result back to Claude.

          How to run it:
            python mcp_server.py

            Claude Desktop will start this automatically once configured.
            """

import asyncio
import json
import sys
import os
import base64
import pathlib
import threading
import websocket
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# Configuration
MOMOA_SERVER = os.environ.get("MOMOA_SERVER_ADDRESS", "localhost:3007")

app = Server("momoa-multi-agent")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
      return [
                types.Tool(
                              name="run_momoa_task",
                              description=(
                                                "Submit a software engineering task to the MoMoA multi-agent system. "
                                                "MoMoA breaks the task into sub-tasks and assigns them to specialized "
                                                "AI expert agents that debate and validate each other's work, then returns "
                                                "a final result. Best for: refactoring, building features, writing tests, "
                                                "fixing bugs, writing documentation."
                              ),
                              inputSchema={
                                                "type": "object",
                                                "properties": {
                                                                      "task": {
                                                                                                "type": "string",
                                                                                                "description": "A clear description of the engineering task."
                                                                      },
                                                                      "directory": {
                                                                                                "type": "string",
                                                                                                "description": "Optional: Absolute path to the project directory on the local machine."
                                                                      },
                                                                      "assumptions": {
                                                                                                "type": "string",
                                                                                                "description": "Optional: Constraints or rules for the agents to follow."
                                                                      },
                                                                      "max_turns": {
                                                                                                "type": "integer",
                                                                                                "description": "Optional: Maximum number of agent turns per phase (default: 15).",
                                                                                                "default": 15
                                                                      }
                                                },
                                                "required": ["task"]
                              }
                ),
                types.Tool(
                              name="ask_momoa_question",
                              description=(
                                                "Ask MoMoA a question about a codebase without making changes. "
                                                "Use this for analysis, architecture explanations, code review, "
                                                "or getting recommendations."
                              ),
                              inputSchema={
                                                "type": "object",
                                                "properties": {
                                                                      "question": {
                                                                                                "type": "string",
                                                                                                "description": "The question to ask about the code or project."
                                                                      },
                                                                      "directory": {
                                                                                                "type": "string",
                                                                                                "description": "Optional: Path to the project directory to analyse."
                                                                      }
                                                },
                                                "required": ["question"]
                              }
                )
      ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
      if name == "run_momoa_task":
                result = await run_momoa(
                              prompt=arguments.get("task", ""),
                              directory=arguments.get("directory", None),
                              assumptions=arguments.get("assumptions", None),
                              max_turns=arguments.get("max_turns", 15),
                              save_files=True
                )
                return [types.TextContent(type="text", text=result)]
elif name == "ask_momoa_question":
        result = await run_momoa(
                      prompt=arguments.get("question", ""),
                      directory=arguments.get("directory", None),
                      assumptions=None,
                      max_turns=10,
                      save_files=False
        )
        return [types.TextContent(type="text", text=result)]
else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def run_momoa(prompt, directory, assumptions, max_turns, save_files):
      log_lines = []
      final_result = None
      error_message = None
      state = {"value": "INIT"}
      all_files = []

    if directory and os.path.isdir(directory):
              all_files = _load_files_from_directory(directory)
              log_lines.append(f"Loaded {len(all_files)} files from {directory}")

    upload_index = {"value": 0}
    MAX_CHUNK_BYTES = 25 * 1024 * 1024
    done_event = threading.Event()

    def send_next_chunk(ws):
              chunk = []
              chunk_size = 0
              while upload_index["value"] < len(all_files):
                            f = all_files[upload_index["value"]]
                            f_size = len(f["name"].encode()) + len(f["content"].encode())
                            if chunk_size + f_size > MAX_CHUNK_BYTES and chunk_size > 0:
                                              break
                                          chunk.append(f)
                            chunk_size += f_size
                            upload_index["value"] += 1
                            if chunk_size >= MAX_CHUNK_BYTES:
                                              break
                                      if chunk:
                                                    ws.send(json.dumps({"status": "FILE_CHUNK", "data": {"files": chunk}}))
else:
            ws.send(json.dumps({"status": "START_TASK", "data": {}}))
              state["value"] = "TASK_RUNNING"

    def on_open(ws):
              state["value"] = "AWAITING_PARAMS_ACK"
              ws.send(json.dumps({
                  "status": "INITIAL_REQUEST_PARAMS",
                  "data": {
                      "prompt": prompt,
                      "llmName": "claude-sonnet-4-5",
                      "maxTurns": max_turns,
                      "assumptions": assumptions or "",
                      "image": "",
                      "imageMimeType": "",
                      "saveFiles": save_files,
                      "mode": "developer",
                  }
              }))

    def on_message(ws, raw_message):
              nonlocal final_result, error_message
              try:
                            msg = json.loads(raw_message)
except json.JSONDecodeError:
            log_lines.append(f"[non-JSON]: {raw_message}")
            return

        status = msg.get("status", "")
        content = msg.get("message", "")

        if state["value"] == "AWAITING_PARAMS_ACK":
                      if status == "PARAMS_RECEIVED":
                                        state["value"] = "UPLOADING_FILES"
                                        send_next_chunk(ws)

elif state["value"] == "UPLOADING_FILES":
            if status == "CHUNK_RECEIVED":
                              send_next_chunk(ws)

elif state["value"] == "TASK_RUNNING":
            if status == "WORK_LOG":
                              log_lines.append(content)
elif status == "PROGRESS_UPDATES":
                completed = msg.get("completed_status_message", "")
                if completed:
                                      log_lines.append(f"checkmark {completed}")
elif status == "HITL_QUESTION":
                question = msg.get("message", "")
                log_lines.append(f"\nMoMoA needs input:\n{question}\n")
                ws.send(json.dumps({
                                      "status": "HITL_RESPONSE",
                                      "answer": "Please use your best judgment and continue."
                }))
elif status == "COMPLETE_RESULT":
                data = msg.get("data", {})
                final_result = data.get("result", "Task completed with no result text.")
                ws.close()
                  done_event.set()
elif status == "ERROR":
                error_message = content
                ws.close()
                done_event.set()

    def on_error(ws, error):
              nonlocal error_message
        error_message = str(error)
        done_event.set()

    def on_close(ws, code, msg):
              done_event.set()

    ws_app = websocket.WebSocketApp(
              f"ws://{MOMOA_SERVER}",
              on_open=on_open,
              on_message=on_message,
              on_error=on_error,
              on_close=on_close
    )

    thread = threading.Thread(target=ws_app.run_forever)
    thread.daemon = True
    thread.start()
    done_event.wait(timeout=1800)

    if error_message:
              return f"MoMoA Error: {error_message}\n\nLog:\n" + "\n".join(log_lines)

    output_parts = []
    if log_lines:
              output_parts.append("MoMoA Work Log:\n" + "\n".join(log_lines))
    if final_result:
              output_parts.append("\nFinal Result:\n" + final_result)
else:
        output_parts.append("\nTask timed out or did not return a result.")
    return "\n".join(output_parts)


def _load_files_from_directory(directory):
      SKIP_DIRS = {
                "node_modules", ".git", "__pycache__", ".venv",
                "venv", "dist", "build", ".next", ".cache"
      }
    files = []
    root = pathlib.Path(directory).resolve()
    for path in root.rglob("*"):
              if path.is_file():
                            if any(part in SKIP_DIRS for part in path.parts):
                                              continue
                                          try:
                                                            content = path.read_bytes()
                                                            encoded = base64.b64encode(content).decode("utf-8")
                                                            files.append({"name": str(path.relative_to(root)), "content": encoded})
except Exception:
                pass
    return files


async def main():
      async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
      asyncio.run(main())
