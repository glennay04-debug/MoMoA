# MoMoA MCP Skill - Setup Guide

Connect Claude Desktop to the MoMoA multi-agent engineering system
so Claude can delegate complex coding tasks to a swarm of AI experts.

## Step 1: Install Python Dependencies

Open a terminal in this folder and run:

    pip install -r requirements.txt

    ## Step 2: Start the MoMoA Server

    In your MoMoA project root folder, run:

        npm run dev

        Leave this running. It listens on port 3007.

        ## Step 3: Connect to Claude Desktop

        1. Open Claude Desktop
        2. Go to Settings then Developer then Edit Config
        3. Add this block to your claude_desktop_config.json file replacing the path and API key:

            {
                  "mcpServers": {
                          "momoa": {
                                    "command": "python",
                                              "args": ["/FULL/PATH/TO/momoa-skill/mcp_server.py"],
                                                        "env": {
                                                                    "ANTHROPIC_API_KEY": "sk-ant-YOUR-KEY-HERE",
                                                                                "MOMOA_SERVER_ADDRESS": "localhost:3007"
                                                                                          }
                                                                                                  }
                                                                                                        }
                                                                                                            }
                                                                                                            
                                                                                                            4. Save the file and restart Claude Desktop.
                                                                                                            5. You should see a hammer icon in the chat bar meaning tools are connected.
                                                                                                            
                                                                                                            ## Step 4: Use It
                                                                                                            
                                                                                                            Just ask Claude naturally:
                                                                                                            
                                                                                                            - Use MoMoA to refactor the login system in my project at /Users/me/myapp
                                                                                                            - Ask MoMoA to explain what the code in ./src does
                                                                                                            - Have MoMoA write unit tests for all exported functions in ./lib
                                                                                                            
                                                                                                            ## Troubleshooting
                                                                                                            
                                                                                                            Connection refused: MoMoA server is not running. Run npm run dev first.
                                                                                                            
                                                                                                            Tool not showing in Claude: Check the path in claude_desktop_config.json is correct and absolute.
                                                                                                            
                                                                                                            ANTHROPIC_API_KEY missing: Add it to the env block in claude_desktop_config.json.
                                                                                                            
                                                                                                            Module not found: Run pip install -r requirements.txt again.
