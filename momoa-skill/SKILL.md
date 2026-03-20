---
name: MoMoA Multi-Agent Engineer
description: >
  Connects Claude to the MoMoA (Mixture of Mixture of Agents) system.
    MoMoA breaks complex software engineering tasks into sub-tasks and
      assigns them to a swarm of specialized AI experts that debate and
        validate each other's work before reporting back. Use this skill
          when you need to refactor code, build features, write documentation,
            or perform any long-running software development task on a local
              project directory.
              version: 1.0.0
              author: glennay04-debug
              tools:
                - name: run_momoa_task
                    description: >
                          Submits a software engineering task to the MoMoA multi-agent
                                system. Provide a clear description of the task and optionally
                                      a path to the project directory on your local machine.
                                        - name: ask_momoa_question
                                            description: >
                                                  Asks MoMoA a question about a codebase or project without
                                                        making any file changes. Useful for getting analysis,
                                                              explanations, or recommendations.
                                                              requirements:
                                                                - Python 3.8 or higher
                                                                  - MoMoA server running locally on port 3007
                                                                    - ANTHROPIC_API_KEY set in your environment
                                                                    ---

                                                                    # MoMoA Multi-Agent Skill

                                                                    This skill connects Claude Desktop to a locally running MoMoA server,
                                                                    enabling Claude to delegate complex software engineering tasks to a
                                                                    swarm of specialized AI agents powered by Claude.

                                                                    ## Quick Start

                                                                    1. Follow the setup guide in README.md
                                                                    2. Start the MoMoA server: npm run dev
                                                                    3. Connect this skill to Claude Desktop (see README.md)
                                                                    4. Ask Claude to use MoMoA for any coding task

                                                                    ## Example Prompts

                                                                    - "Use MoMoA to add JWT authentication to my Express app in ./my-project"
                                                                    - "Ask MoMoA to explain the architecture of the code in ./src"
                                                                    - "Have MoMoA write unit tests for all functions in ./lib"
