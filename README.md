DSA Walled Garden: Local RAG Assistant

A hardware-accelerated, Retrieval-Augmented Generation (RAG) system designed to provide validated Data Structures and Algorithms (DSA) answers using Llama 3.2 and Pinecone.
    Core Features

    Walled Garden Logic: Uses a 0.75 similarity consensus threshold. If the retrieved context doesn't meet the score, the system triggers the "IDK Protocol" to prevent hallucinations.

    Hardware Accelerated: Optimized for NVIDIA GPUs (RTX 3050+) using CUDA.

    Dockerized Environment: Fully containerized backend for consistent deployment across Linux (Arch) and Windows (WSL2).

    LaTeX Support: Mathematical formulas and time complexities are rendered in clean LaTeX.

  Tech Stack

    LLM: Ollama (Llama 3.2)

    Vector DB: Pinecone

    Framework: LangChain & Python 3.12

    Infrastructure: Docker & Docker Compose

    Host OS: Arch Linux (Primary) / Windows 11 (Secondary)

 Installation & Setup
1. Host Requirements

Linux (Arch):

    Install ollama-cuda via pacman.

    Install nvidia-container-toolkit.

    Ensure the Ollama service is configured to listen on the Docker bridge (see Networking).

Windows:

    Install Docker Desktop (WSL2 Backend).

    Install Ollama for Windows.

2. Networking (The "Bridge" Fix)

To allow the Docker container to talk to the Ollama server on the host, the OLLAMA_HOST environment variable must be set.

    Linux Fix: Set OLLAMA_HOST=172.18.0.1:11434 in systemd override.

    Windows Fix: Docker Desktop handles this via host.docker.internal.

3. Environment Variables

Create a .env file in the root directory:
Bash

PINECONE_API_KEY=your_api_key_here
OLLAMA_URL=http://172.18.0.1:11434  # Use host.docker.internal for Windows

 Deployment
Running with Docker

Build and launch the assistant:
Bash

docker compose run dsa-assistant

Manual GPU Verification (Linux)

To ensure the RTX 3050 is handling the load:
Bash

watch -n 0.5 nvidia-smi

  Logic Flow: The 0.75 Consensus

    Query: User asks a DSA question.

    Search: System queries Pinecone for relevant PDF chunks.

    Validate: * If Score ≥ 0.75: Context is injected into the prompt.

        If Score < 0.75: System returns: "⚠️ This information is outside the Walled Garden."

    Generate: Llama 3.2 produces the final answer.

  Troubleshooting

    Connection Refused: Ensure the Ollama service is not bound to 127.0.0.1. It must be bound to the Gateway IP found via docker network inspect.

    Slow Response: Check if ollama-cuda is installed. If the CPU is pegged at 100%, the GPU is not being utilized.

    Orphan Containers: Run docker compose down --remove-orphans to clean up old sessions.

##  INSTRUCTION: INITIAL SETUP FOR ASSISTANT␍
 Since this project was developed on Arch Linux and uses Docker, follow these steps to get it running on **Windows**. ### **Step 1: Install Prerequisites**1. **Docker Desktop:** [Download here](https://www.docker.com/products/docker-desktop/). Ensure **WSL 2** is enabled during install. 2. **Ollama:** [Download here](https://ollama.com/download/windows). After installing, open your terminal and run: ```bash ollama run llama3.2␍
Step 2: Fix Windows Networking (Crucial)␍
By default, Ollama only listens to your local computer. We need to "open the door" so the Docker container can talk to it.␍
1.	Set Environment Variable:␍
o	Search for "Edit the system environment variables" in Windows Start.␍
o	Click Environment Variables.␍
o	Under 'User variables', click New.␍
o	Variable name: OLLAMA_HOST␍
o	Variable value: 0.0.0.0:11434␍
1.	Restart Ollama: Right-click the Ollama icon in your System Tray (near the clock), click Quit, and then restart Ollama from the Start Menu.␍

Step 3: Setup Environment Variables␍
Create a file named .env in the root folder of this project (where main.py is). Paste the following:␍
Code snippet␍
PINECONE_API_KEY=your_actual_key_here␍
PINECONE_INDEX_NAME=your_actual_index_name␍
# Use this exact URL for Windows Docker Desktop␍
OLLAMA_URL=[http://host.docker.internal:11434](http://host.docker.internal:11434)␍
␍
Step 4: Launch the System␍
Open a terminal (PowerShell or CMD) in the project folder and run:␍
Bash␍
# 1. Build the Docker Image docker compose build  # 2. Start the Assistant docker compose up ␍
The API is live when you see Uvicorn running on http://0.0.0.0:8000. Test it here: http://localhost:8000/docs␍
␍
