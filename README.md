![EVA Banner](eva.jpeg)

<div align="center">
</div>

⫻ 𝝣.𝗩.𝝠
⮡ Exploit Vector Agent
Autonomous offensive security AI for guiding pentest processes

[![Stars](https://img.shields.io/github/stars/ARCANGEL0/EVA?style=for-the-badge&color=353535)](https://github.com/ARCANGEL0/EVA)
[![Watchers](https://img.shields.io/github/watchers/ARCANGEL0/EVA?style=for-the-badge&color=353535)](https://github.com/ARCANGEL0/EVA)
[![Forks](https://img.shields.io/github/forks/ARCANGEL0/EVA?style=for-the-badge&color=353535)](https://github.com/ARCANGEL0/EVA)
[![Views](https://komarev.com/ghpvc/?username=eva&color=353535&style=for-the-badge&label=REPO%20VIEWS)](https://github.com/ARCANGEL0/EVA)
[![License](https://img.shields.io/badge/License-MIT-223355.svg?style=for-the-badge)](LICENSE)
[![For](https://img.shields.io/badge/For-Offensive%20Security-8B0000.svg?style=for-the-badge)](#)
[![AI](https://img.shields.io/badge/AI-Powered-cyan.svg?style=for-the-badge)](#)

> 🔄 **This is a community-maintained fork** with critical fixes for Ollama integration, improved model compatibility, and enhanced stability for local deployments.

---

## 𝝺 Overview

EVA is an AI penetration testing agent that guides users through complete pentest engagements with AI-powered attack strategy, autonomous command generation, and real-time vulnerability analysis based on outputs. The goal is not to replace the pentest professional but to guide, assist, and provide faster results.

### ✨ Improvements in This Fork

| Feature | Description |
|---------|-------------|
| 🔧 **Ollama Parsing Fix** | Resolved `"⚠️ Error parsing model response"` issue with custom Modelfile configuration and temperature tuning |
| 🤖 **Alternative Model Support** | Added tested configurations for Qwen2.5-Coder, Llama-3.1, and other models optimized for instruction-following |
| ⚙️ **Configuration Templates** | Pre-configured `Modelfile` examples for stable JSON output and reduced conversational noise |
| 💾 **Memory Optimization** | Guidelines for running 13B models on systems with 16-20GB RAM, including context window tuning |
| 🐛 **Troubleshooting Guide** | Step-by-step solutions for common Ollama + EVA integration issues |

---

## Main Functionalities

🜂 **Intelligent Reasoning**: Advanced AI-driven analysis and attack path identification depending on query.  
ⵢ **Automated Enumeration**: Systematic target reconnaissance and information gathering based on provided target.  
ꎈ **Vulnerability Assessment**: AI-powered vulnerability identification and exploitation strategies.  
⑇ **Multiple AI Backends**: Support for Ollama, OpenAI GPT, G4F.dev and custom API endpoints.  
ㄖ **Session Management**: Persistent sessions and chats with improved error handling.  
⑅ **Interactive Interface**: Real-time command execution and analysis of output in multi-stage.  

---

## 🖴 Quick Start

### 🍎 Installation

```bash
# Ollama for local endpoint (required for local AI)
curl -fsSL https://ollama.ai/install.sh | sh

# EVA installation (this fork)
git clone https://github.com/toxy4ny/EVA.git
cd EVA
chmod +x eva.py
./eva.py 

# Optional: Add to PATH for global access
sudo mv eva.py /usr/local/bin/eva
```

### ⬢ First-Time Configuration

On first launch, EVA will automatically:
✅ Prompt for OpenAI API key (if using GPT backend)  
✅ Download default Ollama model (`jimscard/whiterabbit-neo:latest`)  
✅ Create session directory at `~/.config/eva/`  
✅ Install Python dependencies  

> 💡 **Pro Tip**: For better stability with local models, review the [Ollama Configuration](#-ollama-configuration--troubleshooting) section below before starting your first engagement.

---

## 🤖 Recommended AI Models for Local Deployment

| Model | Size | RAM Required | Best For | Notes |
|-------|------|--------------|----------|-------|
| `qwen2.5-coder:14b` | 14B | ~10 GB | Code generation, structured output | ✅ Best instruction-following, recommended default |
| `llama3.1:8b` | 8B | ~6 GB | Fast responses, JSON compliance | ✅ Lightweight, great for automation |
| `whiterabbit-neo:13b` | 13B | ~9 GB | Uncensored offensive security tasks | ⚠️ Requires Modelfile tuning (see below) |
| `dolphin-mixtral:8x7b` | ~12GB effective | ~16 GB | Complex reasoning, uncensored | ⚠️ Heavy, may swap on 20GB systems |

### How to Change Model in EVA

Edit `eva.py` and modify:
```python
OLLAMA_MODEL = "qwen2.5-coder:14b"  # Change to your preferred model
```

Or pull additional models:
```bash
ollama pull qwen2.5-coder:14b
ollama pull llama3.1
```

---

## ⚙️ Ollama Configuration & Troubleshooting

### 🔧 Fix: "⚠️ Error parsing model response"

This error occurs when the model output doesn't match EVA's expected format (usually JSON or clean code blocks). WhiteRabbit-Neo and other "uncensored" models often add conversational text that breaks parsing.

#### Solution 1: Use a Custom Modelfile (Recommended for WRN)

Create a file named `Modelfile` (no extension):

```dockerfile
FROM jimscard/whiterabbit-neo:13b

# Reduce randomness for deterministic output
PARAMETER temperature 0.1
PARAMETER top_p 0.5
PARAMETER num_ctx 4096

# Force structured output
SYSTEM """
You are a security assistant integrated into an automated penetration testing framework.
You must output ONLY valid JSON or clean code blocks when requested.
Do NOT add markdown fences like ```json unless explicitly asked.
Do NOT add conversational text before or after the structured output.
If you cannot complete the task, return a minimal error object: {"error": "description"}
"""
```

Build and run the custom model:
```bash
ollama create eva-wrn-fixed -f Modelfile
ollama run eva-wrn-fixed
```

Then update EVA config:
```python
OLLAMA_MODEL = "eva-wrn-fixed"
```

#### Solution 2: Switch to a More Instruction-Following Model

If Modelfile tuning doesn't resolve the issue, switch to `qwen2.5-coder:14b` or `llama3.1:8b`, which have superior instruction-following capabilities out-of-the-box.

#### Solution 3: Adjust EVA Runtime Parameters

In `eva.py`, ensure these settings are optimized:
```python
# Reduce temperature for more predictable output
# If the variable exists in your version:
temperature = 0.1
top_p = 0.5

# Disable streaming if parser has issues with chunks
stream_responses = False
```

### 💾 Memory & Performance Tips for VMs

If running EVA inside VMware/VirtualBox with limited RAM:

1. **Monitor memory usage** during operation:
   ```bash
   htop
   free -h
   ```

2. **Limit context window** to reduce RAM consumption (add to Modelfile):
   ```dockerfile
   PARAMETER num_ctx 2048  # Default is often 4096 or higher
   ```

3. **Close unnecessary applications** in the VM — a 13B model + EVA + browser can easily exceed 20GB.

4. **Use q4_k_m quantization** models (default in Ollama) — avoid q2/q3 for quality, q8 for size.

---

## 📁 Directory Structure

```
~/EVA/
├── eva.py              # Main executable
└── Modelfile           # [FORK] Custom Ollama model definitions

```

---

## 🎮 Usage Guide

### Initialization
```bash
python3 eva.py
```

### Workflow
1. **Select Session**: Choose existing or create new  
2. **Choose AI Backend**:
   - 🦙 **Ollama** (Recommended): Local AI, privacy-focused
   - ⬡ **OpenAI GPT**: Faster, requires API key
   - ᛃ **G4F.dev**: Free tier, may be unstable
   - ⟅ **Custom API**: Your own endpoint
3. **Define Target**: IP, scope, engagement type
4. **Follow AI Guidance**: Execute, analyze, iterate

### Chat Commands Reference

| Command | Description |
|---------|-------------|
| `/exit` or `/quit` | Exit EVA and save session |
| `/model` | Change AI backend on-the-fly |
| `/rename` | Rename current session |
| `/menu` | Return to session selection |
| `R` | Run suggested command |
| `S` | Skip command, ask for alternative |
| `A` | Ask AI for clarification/next step |
| `Q` | Quit current session without saving |

### Example Session
```
USER > I'm on a Windows target at IP 10.10.11.95, what should I enumerate first?

[ANALYSIS] 
Based on the Windows environment, I need to perform comprehensive 
enumeration focusing on:
1. System Information (OS version, patches, architecture)
2. Network Services (ports, services, listening processes)  
3. User Context (current user, groups, privileges)
...

> execute: nmap -sC -sV -O 10.10.11.95
| [R]un | [S]kip | [A]sk | [Q]uit | 
> R
```

🎬 [Watch Demo](demo.gif)

---

## 🛠️ Development & Contributing

This fork follows the original single-file design for portability. If you prefer modular architecture:

```bash
# Fork and restructure
git clone https://github.com/toxy4ny/EVA.git
# Split eva.py into modules: core/, backends/, utils/, etc.
# Submit PR with modular option as feature flag
```

### Reporting Issues
When reporting Ollama-related bugs, please include:
- Model name and tag (`ollama list`)
- Ollama version (`ollama --version`)
- System RAM and whether you're in a VM
- Exact error message and the prompt that triggered it

---

## ⑇ Roadmap (Fork-Specific)

### ✅ Completed
- [x] Ollama parsing error fix via Modelfile configuration
- [x] Alternative model testing and documentation (Qwen2.5, Llama3.1)
- [x] Memory optimization guidelines for low-RAM systems
- [x] Enhanced troubleshooting section

### 🔄 In Progress
- [ ] Automated Modelfile generator via CLI flag
- [ ] Model benchmarking suite (accuracy vs. speed vs. RAM)
- [ ] Dockerfile for one-command deployment with pre-tuned models

### 🗓️ Planned
- [ ] CVE database integration with local/offline fallback
- [ ] Exportable attack graphs (Mermaid.js / Graphviz)
- [ ] Web UI toggle for headless/server deployments

*(Original roadmap items remain in priority queue)*

---

## ⨹ Legal Notice

> 🚨 **IMPORTANT**: This tool is for authorized environments only!

✅ **APPROVED USE CASES**  
- CTF (Capture The Flag) competitions  
- Authorized penetration testing engagements  
- Security research in isolated lab environments  
- Systems you own or have explicit written permission to test  

🚫 **PROHIBITED USE**  
- Unauthorized access to any system or network  
- Illegal or malicious activities  
- Production systems without explicit authorization  
- Any activity violating local, national, or international law  

⚠️ **DISCLAIMER**  
The original author and fork maintainers take no responsibility for misuse, illegal activity, or unauthorized use. Any and all consequences are the sole responsibility of the user.

---

## ⫻ License

MIT License — Same as original. See [LICENSE](LICENSE) for details.

---

## ❤️ Support & Acknowledgments

If you find this fork useful:
- ⭐ Star the original repo: [ARCANGEL0/EVA](https://github.com/ARCANGEL0/EVA)
- 🍵 Support development: [Ko-fi](https://ko-fi.com)
- 🐛 Report issues or contribute fixes via PRs

> *"Hack the world. Byte by Byte."*  
> ⛛ 𝝺𝗿𝗰𝗮𝗻𝗴𝗲𝗹𝗼 @ 2026 | Fork maintained by [KL3FT3Z]

[[ꋧ]](#-𝝣𝗩𝝠)  
⚠️ *Remember: With great power comes great responsibility. Use this tool ethically and legally.*
```
