#!/bin/bash
# =============================================================
# MoMoA + MCP Install Script for ChromeOS Linux (Crostini)
# Run this ONCE to set everything up automatically.
# Usage: bash install.sh
# =============================================================

set -e  # Stop immediately if any command fails

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  MoMoA MCP Installer for ChromeOS  ${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# --- Step 1: Check we are in the right place ---
if [ ! -f "../package.json" ]; then
  echo -e "${RED}ERROR: Please run this script from inside the momoa-skill folder.${NC}"
    echo "Example: cd ~/MoMoA/momoa-skill && bash install.sh"
      exit 1
      fi

      MOMOA_DIR="$(cd .. && pwd)"
      SKILL_DIR="$(pwd)"

      echo -e "${YELLOW}Step 1/6: Updating package lists...${NC}"
      sudo apt-get update -q

      echo ""
      echo -e "${YELLOW}Step 2/6: Installing Node.js (if not already installed)...${NC}"
      if ! command -v node &> /dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
          sudo apt-get install -y nodejs
            echo -e "${GREEN}Node.js installed: $(node --version)${NC}"
            else
              echo -e "${GREEN}Node.js already installed: $(node --version)${NC}"
              fi

              echo ""
              echo -e "${YELLOW}Step 3/6: Installing Python3 and pip (if not already installed)...${NC}"
              if ! command -v python3 &> /dev/null; then
                sudo apt-get install -y python3 python3-pip
                  echo -e "${GREEN}Python3 installed: $(python3 --version)${NC}"
                  else
                    echo -e "${GREEN}Python3 already installed: $(python3 --version)${NC}"
                    fi

                    echo ""
                    echo -e "${YELLOW}Step 4/6: Installing MoMoA Node.js dependencies...${NC}"
                    cd "$MOMOA_DIR"
                    npm install
                    echo -e "${GREEN}Node dependencies installed.${NC}"

                    echo ""
                    echo -e "${YELLOW}Step 5/6: Installing Python MCP dependencies...${NC}"
                    cd "$SKILL_DIR"
                    pip3 install -r requirements.txt --quiet
                    echo -e "${GREEN}Python dependencies installed.${NC}"

                    echo ""
                    echo -e "${YELLOW}Step 6/6: Setting up your .env file...${NC}"
                    cd "$MOMOA_DIR"
                    if [ ! -f ".env" ]; then
                      echo "ANTHROPIC_API_KEY=PASTE_YOUR_KEY_HERE" > .env
                        echo -e "${GREEN}.env file created at $MOMOA_DIR/.env${NC}"
                          echo -e "${YELLOW}ACTION REQUIRED: Open .env and replace PASTE_YOUR_KEY_HERE with your real Anthropic API key.${NC}"
                          else
                            echo -e "${GREEN}.env file already exists. Skipping.${NC}"
                            fi

                            echo ""
                            echo -e "${GREEN}=====================================${NC}"
                            echo -e "${GREEN}  Installation Complete!             ${NC}"
                            echo -e "${GREEN}=====================================${NC}"
                            echo ""
                            echo "Next steps:"
                            echo "  1. Edit $MOMOA_DIR/.env and add your Anthropic API key"
                            echo "  2. Run:  bash $SKILL_DIR/start.sh"
                            echo "  3. Follow CHROMEOS_SETUP.md to connect to claude.ai"
                            echo ""
