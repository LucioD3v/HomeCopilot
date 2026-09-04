# 🛡️ HomeCopilot: Everyday Family Agent

## - Strands Agents SDK + AgentCore -

> Your everyday autonomous copilot for household logistics, designed to eliminate family mental load by proactively navigating daily tasks, grocery budgets, and schedule conflicts.

[![Track: Everyday Agents](https://img.shields.io/badge/Track-Everyday_Agents-blue.svg)](https://agentsforhumans.devpost.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Powered by Strands](https://img.shields.io/badge/Powered%20by-Strands%20Agents%20SDK-purple.svg)](https://github.com/strands-agents)

---

## 📋 Table of Contents
- [The Inspiration & The Problem](#-the-inspiration--the-problem)
- [Target Audience](#-target-audience)
- [System Architecture](#-system-architecture)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Setup & Installation](#-setup--installation)
- [Running the Demo](#-running-the-demo)
- [License](#-license)

---

## 💡 The Inspiration & The Problem
**HomeCopilot was born out of lived experience.** As a remote working father juggling professional software engineering responsibilities while coordinating a complex household—including a 5-year-old son (Gerardo) with an active weekly schedule of swimming, chess, and karate twice a week, alongside a 2-year-old daughter (Isabella) in daycare—the invisible mental load became overwhelmingly real.

Modern families face a constant stream of micro-decisions: tracking expenses, avoiding budget overruns, coordinating overlapping kids' activities, and balancing household chores without neglecting professional work. Traditional tools are completely reactive—they only work when you manually trigger them, failing to anticipate conflicts or reduce cognitive fatigue.

---

## 👥 Target Audience
Busy parents, remote professionals, and households juggling multiple schedules who need an intelligent, proactive assistant to handle everyday logistics without demanding constant manual intervention.

---

## 🏗️ System Architecture

HomeCopilot is built on a robust, scalable agentic architecture:
1. **Input Layer:** Unstructured user voice notes or chat messages.
2. **Orchestration Layer:** **Strands Agents SDK** manages the reasoning loops, tool routing, and autonomous decision-making.
3. **Infrastructure & Runtime:** Deployed with **Amazon Bedrock AgentCore** for secure execution and persistent session memory.
4. **Action Layer:** Custom Python tools (`@tool`) that evaluate workload limits, kid schedules, and budget thresholds.

---

## ✨ Key Features
- **Proactive Kids' Schedule Management:** Cross-references complex weekly routines (swimming, chess, karate, daycare) to catch time conflicts instantly.
- **Home Office Workload Balancer:** Evaluates household chores and logistics against remote work hours to prevent burnout and mental fatigue.
- **Autonomous Reasoning:** Instead of following rigid workflows, the Strands agent chains multiple tools together to provide complete, actionable recommendations.

---

## 💻 Tech Stack
- **Python 3.10+**
- **Strands Agents SDK**
- **Amazon Bedrock & AgentCore (Claude Sonnet 4.6)**
- **Dotenv & Python standard libraries**

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.10 or higher installed on your machine.
- An active AWS Account with access to Amazon Bedrock models (Claude Sonnet enabled).
- AWS CLI configured on your local machine.

### Step 1: Clone the repository
```bash
git clone https://github.com/LucioD3v/HomeCopilot.git
cd HomeCopilot
```

### Step 2: Create and activate a virtual environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install dependencies
```bash
pip install strands-agents strands-agents-tools python-dotenv awscli boto3
```

### Step 4: Configure your AWS Credentials
Run the following command in your terminal and enter your AWS Access Key ID, Secret Access Key, and your preferred region (e.g., `us-east-1`):

```bash
aws configure
```

### Step 5: Create the environment file
Create a file named `.env` in the root directory of the project and add your region:

```env
AWS_REGION=us-east-1
```

---

## 🚀 Running the Demo
Once everything is installed and configured, execute the main script to see the agent process a complex, unstructured family request, invoke custom tools autonomously, and output a proactive decision alert:

```bash
python main.py
```

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).

---