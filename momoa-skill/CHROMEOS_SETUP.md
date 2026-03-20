# MoMoA on ChromeOS - Complete Setup Guide

For total beginners. Do INSTALL once. Use START every time after.

---

## WHAT IS HAPPENING

Your browser talks to an MCP bridge running in Linux.
The bridge talks to MoMoA. MoMoA uses Claude to run AI agents on your code.

---

## ONE-TIME INSTALL

### 1. Open Linux terminal (penguin icon in app drawer)

### 2. Clone MoMoA (skip if already done)

    git clone https://github.com/glennay04-debug/MoMoA.git

    ### 3. Run install script

        cd ~/MoMoA/momoa-skill
            bash install.sh

            Wait for it to finish. It installs everything automatically.

            ### 4. Add your API key

                nano ~/MoMoA/.env

                Replace PASTE_YOUR_KEY_HERE with your real Anthropic key (sk-ant-...).
                Get one free at: https://console.anthropic.com > API Keys > Create Key

                Save: press Ctrl+X then Y then Enter

                ---

                ## EVERY TIME YOU USE MOMOA

                ### 1. Open Linux terminal

                ### 2. Start everything with one command

                    cd ~/MoMoA/momoa-skill
                        bash start.sh

                        It will print a URL like: http://100.115.92.200:8080/sse
                        Copy that URL.

                        ### 3. Connect claude.ai to MoMoA

                        1. Go to https://claude.ai in your browser
                        2. Click your profile picture (top right)
                        3. Click Settings
                        4. Click Integrations (or Connections)
                        5. Click Add Integration
                        6. Paste the URL from your terminal
                        7. Name it: MoMoA
                        8. Click Save

                        A hammer icon will appear in the chat. MoMoA is connected!

                        ### 4. Use it - just type naturally

                        Examples:
                        - Use MoMoA to refactor my login code in /home/user/myproject
                        - Ask MoMoA to explain what the code in /home/user/myapp does
                        - Have MoMoA add unit tests to /home/user/mylib

                        ### 5. When done - press Ctrl+C in terminal

                        ---

                        ## QUICK REFERENCE

                        First time only:
                            cd ~/MoMoA/momoa-skill && bash install.sh
                                nano ~/MoMoA/.env

                                Every time:
                                    cd ~/MoMoA/momoa-skill && bash start.sh

                                    ---

                                    ## FIXES FOR COMMON PROBLEMS

                                    No such file install.sh:
                                        Make sure you are in the right folder: cd ~/MoMoA/momoa-skill

                                        API key error:
                                            Run: nano ~/MoMoA/.env and check your key is correct

                                            Connection refused in claude.ai:
                                                Run bash start.sh in terminal first, then retry

                                                Hammer icon not showing:
                                                    The URL changes each restart. Copy the new URL from the terminal and update it in claude.ai Settings > Integrations

                                                    npm not found:
                                                        Run: bash install.sh again

                                                        pip3 not found:
                                                            Run: sudo apt-get install python3-pip

                                                            ---

                                                            ## IMPORTANT NOTES

                                                            Keep the terminal open while using MoMoA.
                                                            Your project files must be in Linux (path starts with /home/ or ~/).
                                                            The URL shown by start.sh changes each time Linux restarts. Always use the latest one.
