# 🛡️ FamilyPulse (Strands Agents SDK + AgentCore)

> An autonomous household logistics agent designed to eliminate family mental load by proactively managing daily tasks, grocery budgets, and schedule conflicts.

[![Track: Everyday Agents](https://img.shields.io/badge/Track-Everyday_Agents-blue.svg)](https://agentsforhumans.devpost.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Powered by Strands](https://img.shields.io/badge/Powered%20by-Strands%20Agents%20SDK-purple.svg)](https://github.com/strands-agents)

---

## 📋 Table of Contents
- [The Problem We're Solving](#-the-problem-were-solving)
- [Target Audience](#-target-audience)
- [System Architecture](#-system-architecture)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Setup & Installation](#-setup--installation)
- [Running the Demo](#-running-the-demo)

---

## 🎯 The Problem We're Solving
Modern families face a constant stream of micro-decisions and invisible mental load: tracking grocery expenses, avoiding budget overruns, coordinating school calendars, and planning weekly meals. Traditional tools are completely reactive—they only work when you manually trigger them, failing to anticipate conflicts or reduce cognitive fatigue.

## 👥 Target Audience
Busy parents, working professionals, and households juggling multiple schedules who need an intelligent, proactive assistant to handle everyday logistics without demanding constant manual intervention.

---

## 🏗️ System Architecture
FamilyPulse is built on a robust, scalable agentic architecture:
1. **Input Layer:** Unstructured user voice notes or chat messages.
2. **Orchestration Layer:** **Strands Agents SDK** manages the reasoning loops, tool routing, and autonomous decision-making.
3. **Infrastructure & Runtime:** Deployed with **Amazon Bedrock AgentCore** for secure execution and persistent session memory.
4. **Action Layer:** Custom Python tools `@tool` that evaluate budget thresholds and check calendar conflicts.

---

## ✨ Key Features
- **Proactive Budget Monitoring:** Automatically tracks weekly grocery spending against predefined limits and alerts users *only* when budgets are at risk.
- **Schedule Conflict Detection:** Cross-references family activities with busy calendars to prevent double-booking.
- **Autonomous Reasoning:** Instead of following rigid workflows, the Strands agent chains multiple tools together to provide complete, actionable recommendations.

---

## 💻 Tech Stack
- **Python 3.10+**
- **Strands Agents SDK**
- **Amazon Bedrock & AgentCore**
- **Dotenv & Python standard libraries**

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10 or higher installed on your machine.
- AWS credentials configured (`aws configure`) with access to Amazon Bedrock models.

### Step-by-Step Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/tu-usuario/familypulse-agent.git](https://github.com/tu-usuario/familypulse-agent.git)
   cd familypulse-agent
