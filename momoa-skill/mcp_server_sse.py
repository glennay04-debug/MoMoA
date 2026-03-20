# mcp_server_sse.py - MoMoA MCP Bridge for claude.ai web (SSE transport)
# Started automatically by start.sh

import asyncio
import json
import os
import base64
import pathlib
import threading
import websocket
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp import types
from starlette.applications import Starlette
from starlette.routing import Route, Mount
import uvicorn

MOMOA_SERVER = os.environ.get("MOMOA_SERVER_ADDRESS", "localhost:3007")
MCP_PORT = int(os.environ.get("MCP_PORT", "8080"))
app_server = Server("momoa-multi-agent")

@app_server.list_tools()
async def list_tools() -> list[types.Tool]:
      return [
                types.Tool(
                              name="run_momoa_task",
                              description="Submit a software engineering task to MoMoA multi-agent system. Best for refactoring, building features, writing tests, fixing bugs.",
                              inputSchema={
                                                "type": "object",
                                                "properties": {
                                                                      "task": {"type": "string", "description": "Clear description of the task."},
                                                                      "directory": {"type": "string", "description": "Optional: absolute path to project folder."},
                                                                      "assumptions": {"type": "string", "description": "Optional: rules for agents to follow."},
                                                                      "max_turns": {"type": "integer", "description": "Optional: max agent turns (default 15).", "default": 15}
                                                },
                                                "required": ["task"]
                              }
                ),
                types.Tool(
                              name="ask_momoa_question",
                              description="Ask MoMoA a question about a codebase without making changes.",
                              inputSchema={
                                                "type": "object",
                                                "properties": {
                                                                      "question": {"type": "string", "description": "Question to ask about code or project."},
                                                                      "directory": {"type": "string", "description": "Optional: path to project folder."}
                                                },
                                                "required": ["question"]
                              }
                )
      ]

@app_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
      if name == "run_momoa_task":
                result = await run_momoa(arguments.get("task",""), arguments.get("directory"), arguments.get("assumptions"), arguments.get("max_turns",15), True)
elif name == "ask_momoa_question":
        result = await run_momoa(arguments.get("question",""), arguments.get("directory"), None, 10, False)
else:
        result = f"Unknown tool: {name}"
      return [types.TextContent(type="text", text=result)]

async def run_momoa(prompt, directory, assumptions, max_turns, save_files):
      log_lines, final_result, error_message = [], None, None
      state = {"v": "INIT"}
      all_files = _load_files_from_directory(directory) if directory and os.path.isdir(directory) else []
      if all_files:
                log_lines.append(f"Loaded {len(all_files)} files from {directory}")
            idx = {"v": 0}
    MAX_CHUNK = 25 * 1024 * 1024
    done = threading.Event()

    def send_chunk(ws):
              chunk, size = [], 0
              while idx["v"] < len(all_files):
                            f = all_files[idx["v"]]
                            fs = len(f["name"].encode()) + len(f["content"].encode())
                            if size + fs > MAX_CHUNK and size > 0:
                                break
                                          chunk.append(f); size += fs; idx["v"] += 1
                                          if size >= MAX_CHUNK:
                                                            break
                                                    if chunk:
                                                                  ws.send(json.dumps({"status":"FILE_CHUNK","data":{"files":chunk}}))
                            else:
                                          ws.send(json.dumps({"status":"START_TASK","data":{}}))
                                          state["v"] = "TASK_RUNNING"

                    def on_open(ws):
                              state["v"] = "AWAITING_PARAMS_ACK"
                              ws.send(json.dumps({"status":"INITIAL_REQUEST_PARAMS","data":{"prompt":prompt,"llmName":"claude-sonnet-4-5","maxTurns":max_turns,"assumptions":assumptions or "","image":"","imageMimeType":"","saveFiles":save_files,"mode":"developer"}}))

    def on_message(ws, raw):
              nonlocal final_result, error_message
        try:
                      msg = json.loads(raw)
except Exception:
            return
        s = msg.get("status","")
        if state["v"] == "AWAITING_PARAMS_ACK" and s == "PARAMS_RECEIVED":
                      state["v"] = "UPLOADING_FILES"; send_chunk(ws)
elif state["v"] == "UPLOADING_FILES" and s == "CHUNK_RECEIVED":
            send_chunk(ws)
elif state["v"] == "TASK_RUNNING":
                      if s == "WORK_LOG":
                                        log_lines.append(msg.get("message",""))
elif s == "PROGRESS_UPDATES" and msg.get("completed_status_message"):
                log_lines.append(f"[done] {msg['completed_status_message']}")
elif s == "HITL_QUESTION":
                log_lines.append(f"Agent question: {msg.get('message','')}")
                ws.send(json.dumps({"status":"HITL_RESPONSE","answer":"Use your best judgment and continue."}))
elif s == "COMPLETE_RESULT":
                final_result = msg.get("data",{}).get("result","Task complete."); ws.close(); done.set()
elif s == "ERROR":
                error_message = msg.get("message",""); ws.close(); done.set()

    def on_error(ws, err):
              nonlocal error_message
        error_message = str(err); done.set()

    def on_close(ws, *a):
              done.set()

    ws_app = websocket.WebSocketApp(f"ws://{MOMOA_SERVER}", on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
    threading.Thread(target=ws_app.run_forever, daemon=True).start()
    done.wait(timeout=1800)

    if error_message:
              return f"Error: {error_message}\n\nLog:\n" + "\n".join(log_lines)
    parts = []
    if log_lines:
              parts.append("Log:\n" + "\n".join(log_lines))
    parts.append(f"\nResult:\n{final_result}" if final_result else "\nTask timed out.")
    return "\n".join(parts)

def _load_files_from_directory(directory):
      SKIP = {"node_modules",".git","__pycache__",".venv","venv","dist","build"}
    files, root = [], pathlib.Path(directory).resolve()
    for p in root.rglob("*"):
              if p.is_file() and not any(s in p.parts for s in SKIP):
                            try:
                                              files.append({"name":str(p.relative_to(root)),"content":base64.b64encode(p.read_bytes()).decode()})
except Exception:
                pass
    return files

sse = SseServerTransport("/messages/")

async def handle_sse(request):
      async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
                await app_server.run(streams[0], streams[1], app_server.create_initialization_options())

starlette_app = Starlette(routes=[Route("/sse", endpoint=handle_sse), Mount("/messages/", app=sse.handle_post_message)])

if __name__ == "__main__":
      print(f"MCP SSE bridge running at http://0.0.0.0:{MCP_PORT}/sse")
    uvicorn.run(starlette_app, host="0.0.0.0", port=MCP_PORT)
