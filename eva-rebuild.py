#!/usr/bin/env python3
# made by:    _    ____   ____    _    _   _  ____ _____ _     ___
# ▄████▄ █████▄  ▄█████ ▄████▄ ███  ██  ▄████  ██████ ██     ▄████▄
# ██▄▄██ ██▄▄██▄ ██     ██▄▄██ ██ ▀▄██ ██  ▄▄▄ ██▄▄   ██     ██  ██
# ██  ██ ██   ██ ▀█████ ██  ██ ██   ██  ▀███▀  ██▄▄▄▄ ██████ ▀████▀
# ---------------------------------------------------------------------
# OPTIMIZED by KL3FT3 FOR: WhiteRabbitNeo-V3-7B / Qwen2.5-Coder
# FEATURES: Robust JSON Parsing, Few-Shot Prompting, Stable Ollama Integration
# ---------------------------------------------------------------------
import os, sys, json, subprocess, signal, re, time, termios, tty
from pathlib import Path
import requests
import itertools
import threading

# ============ Check modules, and autoinstall if not present ============
try:
    from colorama import Fore, Style, init
    import openai
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "colorama", "--break-system-packages"])
    subprocess.run([sys.executable, "-m", "pip", "install", "openai", "--break-system-packages"])
    from colorama import Fore, Style, init
    import openai
init(autoreset=True)

# ================= CONFIG =================
API_ENDPOINT = "NOT_SET"  # <--- change to your desired endpoint if needed
G4F_MODEL = "qwen3-coder-plus"
G4F_URL = "https://api.gpt4free.workers.dev/api/openrouter/chat/completions"

# RECOMMENDED: whiterabbitneo-v3-7b is more stable for JSON than 13b on limited RAM
# Create a Modelfile for best results (see README instructions)
OLLAMA_MODEL = "eva-optimized"

CONFIG_DIR = Path.home() / ".config" / "eva"
SESSIONS_DIR = CONFIG_DIR / "sessions"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

username = os.getlogin()
ENV_PATH = Path(".env")
MAX_RETRIES = 10
RETRY_DELAY = 10

# ═══════════════════════════════════════════════════════════════
#  :: Utilities
# ═══════════════════════════════════════════════════════════════
def checkAPI():
    if API_ENDPOINT == "NOT_SET":
        print(Fore.RED + "\nNo custom API set. Please configure in source code at API_ENDPOINT")
        sys.exit(0)

def checkOpenAIKey():
    key = os.getenv("OPENAI_API_KEY")
    if key and key.strip():
        return key.strip()
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            if line.startswith("OPENAI_API_KEY="):
                key = line.split("=", 1)[1].strip()
                if key:
                    os.environ["OPENAI_API_KEY"] = key
                    return key
    os.system("clear")
    cyber("OpenAI key not found! :: Please insert it below", color=Fore.RED)
    print("\nYour OpenAI API key will be stored locally in .env\n")
    key = input("#key > ").strip()
    if not key:
        print(Fore.RED + "\nNo key provided. Aborting.")
        sys.exit(1)
    with open(ENV_PATH, "a") as f:
        f.write(f"\nOPENAI_API_KEY={key}\n")
    os.environ["OPENAI_API_KEY"] = key
    print(Fore.GREEN + "\n✔ OpenAI API key saved successfully.")
    time.sleep(1)
    return key

def ctrl_c_handler(signum, frame):
    print(Fore.RED + "\n// 🜂 Command interrupted ")
    signal.signal(signal.SIGINT, ctrl_c_handler)

def clear():
    os.system("clear")

# ════════════════════
#  :: UI FUNCTIONS
# ════════════════════
_spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
_spinner_text = " L o a d i n g "
_spinner_delay = 0.10
_spinner_running = False
_spinner_thread = None

def _spinner_animate():
    for i, frame in enumerate(itertools.cycle(_spinner_frames)):
        if not _spinner_running:
            break
        dot_count = (i // 3) % 4 + 1
        dots = "." * dot_count
        spaces = " " * (4 - dot_count)
        sys.stdout.write(f"\r  {frame}  {_spinner_text}{dots}{spaces}")
        sys.stdout.flush()
        time.sleep(_spinner_delay)

def spinner_start():
    global _spinner_running, _spinner_thread
    if _spinner_running:
        return
    _spinner_running = True
    sys.stdout.write("\n")
    _spinner_thread = threading.Thread(target=_spinner_animate)
    _spinner_thread.daemon = True
    _spinner_thread.start()

def spinner_stop():
    global _spinner_running
    _spinner_running = False
    if _spinner_thread:
        _spinner_thread.join()
    sys.stdout.write("\r" + " " * (len(_spinner_text) + 4) + "\r")
    sys.stdout.flush()

def cyber(msg="", width=50, color=Fore.GREEN):
    width = int(width)
    print(color + "╔" + "═" * width + "╗")
    if msg:
        msg_line = f"  {msg}  "
        padding = width - len(msg_line)
        left_pad = padding // 2
        right_pad = padding - left_pad
        print(color + "║" + " " * left_pad + msg_line + " " * right_pad + "║")
    print(color + "╚" + "═" * width + "╝")
    print(Style.RESET_ALL)

def banner():
    clear()
    print(Fore.CYAN + r"""
╔═════════════════════════════════════════════╗
║                                             ║
║  ░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░    ║
║  ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░   ║
║  ░▒▓█▓▒░       ░▒▓█▓▒▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░   ║
║  ░▒▓██████▓▒░  ░▒▓█▓▒▒▓█▓▒░░▒▓████████▓▒░   ║
║  ░▒▓█▓▒░        ░▒▓█▓▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░   ║
║  ░▒▓█▓▒░        ░▒▓█▓▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░   ║
║  ░▒▓████████▓▒░  ░▒▓██▓▒░  ░▒▓█▓▒░░▒▓█▓▒░   ║
║                       Exploit Vector Agent  ║
║                                             ║
║ ᴍᴀᴅᴇ ʙʏ: 𝝺𝗿𝗰𝗮𝗻𝗴𝗲𝗹𝗼                 ║
╚═════════════════════════════════════════════╝
""")

# ╔═════════░░░═════════╗
# ░░░   Query input   ░░░
# ╚═════════░░░═════════╝
def raw_input(prompt=""):
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    buf = ""
    try:
        tty.setcbreak(fd)
        print(prompt, end="", flush=True)
        while True:
            ch = sys.stdin.read(1)
            if ch in ("\n", "\r"):
                print()
                return buf
            elif ch in ("\x7f", "\x08"):
                if buf:
                    buf = buf[:-1]
                    print("\b \b", end="", flush=True)
            elif ch == "\x03":
                raise KeyboardInterrupt
            else:
                buf += ch
                print(ch, end="", flush=True)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

# ╔═════════░░░═════════╗
# ░░░ Control utilies ░░░
# ╚═════════░░░═════════╝
def menu(title, options):
    idx = 0
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while True:
            os.system("clear")
            cyber(title)
            for i, opt in enumerate(options):
                prefix = "→ " if i == idx else "  "
                print(prefix + opt)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                sys.stdin.read(1)
                arrow = sys.stdin.read(1)
                if arrow == "A":
                    idx = (idx - 1) % len(options)
                elif arrow == "B":
                    idx = (idx + 1) % len(options)
            elif ch in ("\n", "\r"):
                return idx
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

# ╔═════════░░░═════════╗
# ░░░ JSON utility func ░░░
# ──────────░░░─────────
# IMPROVED: Handles markdown, trailing commas, and noise
# ╚═════════░░░═════════╝
def extract_json_anywhere(raw_str):
    if not raw_str:
        return None
    
    # 1. Remove markdown code blocks
    cleaned = re.sub(r'```(?:json|python|bash)?\s*', '', raw_str)
    cleaned = re.sub(r'```', '', cleaned)
    
    # 2. Find JSON object boundaries
    start = cleaned.find('{')
    end = cleaned.rfind('}') + 1
    
    if start == -1 or end == 0:
        return None
    
    json_str = cleaned[start:end]
    
    # 3. Fix common JSON errors (trailing commas)
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    
    # 4. Fix escaped newlines in strings that might break parsing
    json_str = json_str.replace('\n', '\\n').replace('\r', '')
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        # Debug output for troubleshooting
        # print(Fore.YELLOW + f"[DEBUG] JSON Parse Error: {e}")
        return None

# ===========================================================================================
# ==== EVA PROMPT BUILDING: OPTIMIZED FOR 7B MODELS ================
# ===========================================================================================
def build_prompt(user_msg, last_output):
    return f"""
### SYSTEM INSTRUCTION
You are EVA, an autonomous offensive security engine for redteaming and penetration testing.
Goal: Analyze security scan output and generate executable exploitation commands.
Output Format: STRICT RAW JSON ONLY. No markdown, no conversational text outside JSON.

### OUTPUT FORMAT
{{
    "analysis": "String: Summary of findings, vulnerabilities, and risk assessment.",
    "commands": ["String: Shell command 1", "String: Shell command 2"]
}}

### CONSTRAINTS
1. NO markdown code blocks (do not use ```json).
2. NO introductory or concluding text.
3. Commands must be valid Linux shell commands suitable for Kali Linux.
4. Use actual IPs and ports from context, no placeholders.
5. Focus on vulnerability verification and authorized testing only.

### FEW-SHOT EXAMPLES
User: Found port 80 running Apache 2.4.49
Assistant: {{"analysis": "[!] CVE-2021-41773 DETECTED. Path traversal possible. [→] Strategy: Attempt directory traversal to read /etc/passwd.", "commands": ["curl -v --path-as-is 'http://target/icons/.%2e/%2e%2e/%2e%2e/etc/passwd'"]}}

User: SMB signing disabled on 192.168.1.50
Assistant: {{"analysis": "[!] RELAY ATTACK VECTOR. SMB signing disabled allows credential relay. [→] Strategy: Use ntlmrelayx to capture hash or execute command.", "commands": ["ntlmrelayx.py -t smb://192.168.1.50 -smb2support -c 'whoami'"]}}

### CONTEXT
Previous Output: {last_output if last_output else "None"}
User Input: {user_msg}

### RESPONSE (RAW JSON ONLY)
"""

def graceful_exit():
    cyber("EVA OFFLINE :: SESSION IS SAVED", color=Fore.RED)
    print(Fore.YELLOW + "🜂  E x i t i n g  E V A ...")
    time.sleep(2.5)
    clear()
    sys.exit(0)

def normalize_response(resp):
    if not isinstance(resp, dict):
        return {"analysis": "⚠️ Invalid LLM output.", "commands": []}
    return {
        "analysis": resp.get("analysis", "⚠️ Error with model response, please ask again."),
        "commands": resp.get("commands", [])
    }

# +-------------------------------------------+
# | LLM CLASS    -██                          |
# | AI handling logic goes here               |
# +-------------------------------------------+
class LLM:
    def __init__(self, backend):
        self.backend = backend
        self.history = []

    def query(self, user_msg, last_output=""):
        prompt = build_prompt(user_msg, last_output)
        self.history.append({
            "role": "user",
            "content": prompt
        })
        raw = ""
        
        # ================= OLLAMA =================
        if self.backend == "ollama":
            # Note: For best results, use a Modelfile with temperature 0.2
            p = subprocess.run(
                ["ollama", "run", OLLAMA_MODEL],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=120  # Add timeout to prevent hanging
            )
            raw = p.stdout
            if p.stderr:
                print(Fore.YELLOW + f"[Ollama Warning] {p.stderr[:100]}")
        
        # ================= G4F.DEV =================
        elif self.backend == "g4f":
            raw = ""
            headers = {"Content-Type": "application/json"}
            data = {
                "model": G4F_MODEL,
                "messages": self.history,
                "stream": False
            }
            for attempt in range(MAX_RETRIES):
                try:
                    r = requests.post(G4F_URL, headers=headers, json=data, timeout=60)
                    if r.status_code == 429:
                        time.sleep(RETRY_DELAY)
                        continue
                    response_data = r.json()
                    if 'error' in response_data:
                        error_msg = response_data['error'].get('message', '').lower()
                        if "most wanted" in error_msg or "rate limit" in error_msg:
                            time.sleep(RETRY_DELAY)
                            continue
                        else:
                            continue
                    choices = response_data.get('choices', [])
                    if choices:
                        choice = choices[0]
                        if 'message' in choice:
                            raw = choice['message'].get('content')
                        elif 'text' in choice:
                            raw = choice.get('text')
                        if not raw:
                            raw = "[ <!> No response detected ]"
                        if raw != "[ <!> No response detected ]":
                            break
                except (requests.RequestException, json.JSONDecodeError):
                    time.sleep(1)
                    continue
        
        # ================= CUSTOM API =================
        elif self.backend == "api":
            r = requests.post(
                API_ENDPOINT,
                json={"conversation": self.history},
                timeout=None
            )
            raw = r.text
        
        # ================= OPENAI GPT =================
        elif self.backend == "gpt":
            openai.api_key = os.environ["OPENAI_API_KEY"]
            try:
                completion = openai.chat.completions.create(
                    model="gpt-4o",  # Updated model name
                    messages=self.history
                )
                raw = completion.choices[0].message.content
            except Exception as e:
                try:
                    completion = openai.chat.completions.create(
                        model="gpt-4-turbo",
                        messages=self.history
                    )
                    raw = completion.choices[0].message.content
                except Exception:
                    print(Fore.RED + f"⚠️ Error querying OpenAI GPTX: {e}")
                    raw = ""
        
        # ================= JSON EXTRACTION =================
        data = extract_json_anywhere(raw)
        if not data:
            data = {
                "analysis": "⚠️ Error parsing model response. Please ask again.\n[Debug] Raw output was not valid JSON.",
                "commands": []
            }
            # Print raw for debugging if needed
            # print(Fore.YELLOW + f"[DEBUG] Raw Response: {raw[:500]}")
        
        data = normalize_response(data)
        self.history.append({
            "role": "assistant",
            "content": raw
        })
        return data

# +-------------------------------------------+
# | Main core  -██                            |
# | Handler for Eva utilities and             |
# | Initialization and session manag          |
# +-------------------------------------------+
class Eva:
    def __init__(self, session_path, backend):
        self.session_path = session_path
        self.last_output = ""
        self.backend = backend
        self.sessionName = self.session_path.stem
        self.memory = {
            "backend": backend,
            "timeline": []
        }
        if session_path.exists():
            self.memory = json.loads(session_path.read_text())
            self.backend = self.memory.get("backend", backend)
        self.model = LLM(self.backend)

    def save(self):
        self.session_path.write_text(json.dumps(self.memory, indent=2))

    def change_model_menu(self):
        options = [
            f"Use WhiteRabbit-Neo LLM locally {'::[SELECTED]' if self.backend=='ollama' else ''}",
            f"Use OpenAI GPT-4o {'::[SELECTED]' if self.backend=='gpt' else ''}",
            f"Use G4F.dev {'::[SELECTED]' if self.backend=='gpt' else ''}",
            f"Use Custom API endpoint [{API_ENDPOINT}] {'::[SELECTED]' if self.backend=='api' else ''}"
        ]
        sel = menu("CHANGE BACKEND", options)
        if sel == 0:
            self.backend = "ollama"
            self.memory["backend"] = self.backend
            self.save()
        elif sel == 1:
            self.backend = "gpt"
            checkOpenAIKey()
            self.memory["backend"] = self.backend
            self.save()
        elif sel == 2:
            self.backend = "g4f"
            self.memory["backend"] = self.backend
            self.save()
        elif sel == 3:
            self.backend = "api"
            checkAPI()
            self.memory["backend"] = self.backend
            self.save()
        self.model = LLM(self.backend)

    def rename_session(self):
        cyber("Type in the desired name for this session")
        new_name = raw_input("⯁⮞ ").strip()
        if not new_name:
            cyber("[!] Session name cannot be empty.", color=Fore.RED)
            return
        if new_name == self.sessionName:
            cyber("[!] New name is the same as current name.", color=Fore.YELLOW)
            return
        invalid_chars = '<>:"/\\|?*'
        if any(char in new_name for char in invalid_chars):
            cyber("[!] Invalid characters in name. Avoid < > : \" / \\ | ? *", color=Fore.RED)
            return
        new_path = SESSIONS_DIR / f"{new_name}.json"
        if new_path.exists():
            cyber("[!] A session with that name already exists.", color=Fore.YELLOW)
            return
        self.session_path.rename(new_path)
        self.session_path = new_path
        self.sessionName = new_name
        self.save()
        cyber(f" [ ✔ ] Session renamed to {new_name}", color=Fore.GREEN)

    def run_command(self, cmd):
        cyber(f"EXECUTING → {cmd}")
        proc = subprocess.Popen(
            cmd, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            preexec_fn=os.setsid
        )
        out = ""
        try:
            for line in proc.stdout:
                print(line, end="")
                out += line
        except KeyboardInterrupt:
            os.killpg(os.getpgid(proc.pid), signal.SIGINT)
            print(Fore.RED + "\n/// 🜂 Command stopped by user.")
        self.last_output = out
        self.memory["timeline"].append({
            "type": "command",
            "cmd": cmd,
            "output": out
        })
        self.save()

    def chat(self):
        os.system("clear")
        cyber(":: 🍎 EVA ONLINE :: ")
        print(Fore.GREEN + "⯁⮞ ˹E˼xploit ˹V˼ector ˹A˼gent\n⬢  Current Model: " + Fore.CYAN + self.backend + f"\n{Fore.GREEN}𖨠 Session Name: " + Fore.YELLOW + self.sessionName)
        print(Fore.RED + "/// type /exit to quit the program anytime")
        print(Fore.RED + "/// type /model to change current model")
        print(Fore.RED + "/// type /rename to change a session name")
        print(Fore.RED + "/// type /menu to go back to sessions menu\n")
        
        for item in self.memory["timeline"]:
            if item["type"] == "user":
                print(Fore.GREEN + f"{username.upper()} > {item['content']}\n")
            elif item["type"] == "analysis":
                cyber("ANALYSIS", color=Fore.MAGENTA)
                print(item["content"] + "\n")
            elif item["type"] == "command":
                cyber(f"EXECUTED → {item['cmd']}", color=Fore.CYAN)
                print(item["output"] + "\n")
        
        while True:
            user = raw_input(Fore.GREEN + f"\n{username.upper()} > ")
            if user.lower() in ("exit", "quit", "q"):
                self.save()
                graceful_exit()
            if user.lower() in ("menu", "/menu"):
                return main()
            if user.lower() in ("rename", "/rename"):
                self.rename_session()
                os.system("clear")
                cyber(":: 🍎 EVA ONLINE :: ")
                print(Fore.GREEN + "⯁⮞ ˹E˼xploit ˹V˼ector ˹A˼gent\n⬢  Current Model: " + Fore.CYAN + self.backend + f"\n{Fore.GREEN}𖨠 Session Name: " + Fore.YELLOW + self.sessionName)
                print(Fore.RED + "/// type /exit to quit the program anytime")
                print(Fore.RED + "/// type /model to change current model")
                print(Fore.RED + "/// type /rename to change a session name")
                print(Fore.RED + "/// type /menu to go back to sessions menu\n")
                for item in self.memory["timeline"]:
                    if item["type"] == "user":
                        print(Fore.GREEN + f"{username.upper()} > {item['content']}\n")
                    elif item["type"] == "analysis":
                        cyber("ANALYSIS", color=Fore.MAGENTA)
                        print(item["content"] + "\n")
                    elif item["type"] == "command":
                        cyber(f"EXECUTED → {item['cmd']}", color=Fore.CYAN)
                        print(item["output"] + "\n")
                continue
            if user.lower() in ("model", "/model"):
                self.change_model_menu()
                os.system("clear")
                cyber(":: 🍎 EVA ONLINE :: ")
                print(Fore.GREEN + "⯁⮞ ˹E˼xploit ˹V˼ector ˹A˼gent\n⬢  Current Model: " + Fore.CYAN + self.backend + f"\n{Fore.GREEN}𖨠 Session Name: " + Fore.YELLOW + self.sessionName)
                print(Fore.RED + "/// type /exit to quit the program anytime")
                print(Fore.RED + "/// type /model to change current model")
                print(Fore.RED + "/// type /rename to change a session name")
                print(Fore.RED + "/// type /menu to go back to sessions menu\n")
                for item in self.memory["timeline"]:
                    if item["type"] == "user":
                        print(Fore.GREEN + f"{username.upper()} > {item['content']}\n")
                    elif item["type"] == "analysis":
                        cyber("ANALYSIS", color=Fore.MAGENTA)
                        print(item["content"] + "\n")
                    elif item["type"] == "command":
                        cyber(f"EXECUTED → {item['cmd']}", color=Fore.CYAN)
                        print(item["output"] + "\n")
                continue
            
            self.memory["timeline"].append({
                "type": "user",
                "content": user
            })
            self.save()
            spinner_start()
            resp = self.model.query(user, self.last_output)
            self.memory["timeline"].append({
                "type": "analysis",
                "content": resp["analysis"]
            })
            self.save()
            spinner_stop()
            cyber("ANALYSIS", color=Fore.MAGENTA)
            print(resp["analysis"])
            
            break_outer = False
            for cmd in resp["commands"]:
                while True:
                    choice = raw_input(
                        f"\n> {cmd}\n[R]un | [S]kip | [A]sk | [Q]uit |\n> "
                    ).strip().lower()
                    if choice == "r":
                        self.run_command(cmd)
                        spinner_start()
                        resp = self.model.query(
                            "Analyze the previous command output and continue.",
                            self.last_output
                        )
                        spinner_stop()
                        cyber("ANALYSIS", color=Fore.MAGENTA)
                        print(resp["analysis"])
                        break
                    elif choice == "a":
                        break_outer = True
                        break
                    elif choice == "s":
                        break
                    elif choice == "q":
                        self.save()
                        graceful_exit()
                    else:
                        print("// 🜂 Not a valid input, please type R, S, A or Q.")
                if break_outer:
                    break
            self.save()

# ================= STARTUP OF EVA here =================
def command_exists(cmd):
    return subprocess.call(
        ["which", cmd],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ) == 0

def ollama_running():
    try:
        output = subprocess.check_output(['ollama', 'list'], stderr=subprocess.STDOUT, text=True)
        return True
    except subprocess.CalledProcessError as e:
        if "server not responding" in e.output.lower():
            return False
        return False

def start_ollama():
    clear()
    print("\n")
    print(Fore.YELLOW + "🜂 OLLAMA NOT RUNNING :: Starting for you...\n")
    with open(os.devnull, 'w') as DEVNULL:
        subprocess.Popen(
            ['ollama', 'serve'],
            stdout=DEVNULL,
            stderr=DEVNULL,
            stdin=DEVNULL,
            close_fds=True,
            start_new_session=True
        )
    time.sleep(3)

def model_exists():
    r = subprocess.run(
        ["ollama", "list"],
        capture_output=True,
        text=True
    )
    return OLLAMA_MODEL in r.stdout

def main():
    banner()
    print(Fore.RED + """
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯
➤ THIS TOOL IS FOR:
- CTFs
- LABS
- SYSTEMS YOU OWN
🜂 UNAUTHORIZED USE IS ILLEGAL
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯
""")
    if input("Do you have authorization to proceed with this tool? (yes/no): ").lower() != "yes":
        sys.exit()
    
    sessions = list(SESSIONS_DIR.glob("*.json"))
    opts = [f"[{i+1}] {s.stem}" for i, s in enumerate(sessions)]
    opts.append("[+] NEW SESSION")
    sel = menu("EVA SESSIONS", opts)
    
    # =========================
    # GETS EXISTING SESSION
    # =========================
    if sel < len(sessions):
        session = sessions[sel]
        data = json.loads(session.read_text())
        backend = data.get("backend", "ollama")
        Eva(session, backend).chat()
        return
    
    # =========================
    # NEW SESSION
    # =========================
    model = menu(
        "SELECT BACKEND",
        [
            "< GO BACK",
            "Use WhiteRabbit-Neo LLM locally (recommended)",
            "GPT-4o (Needs OpenAI ApiKey)",
            "G4F.dev (Free API endpoint)",
            "Use Custom API endpoint (Please check configs to set your own endpoint)"
        ]
    )
    
    if model == 0:
        return main()
    if model == 1:
        backend = "ollama"
        if not command_exists("ollama"):
            clear()
            cyber("// Ollama is not installed. Install it first.", color=Fore.RED)
            time.sleep(3)
            return main()
        if not ollama_running():
            start_ollama()
        if not model_exists():
            clear()
            pull = menu(f"Model {OLLAMA_MODEL} not found. Pull it?", ["Yes", "No"])
            if pull == 0:
                subprocess.run(["ollama", "pull", OLLAMA_MODEL])
            else:
                return main()
    elif model == 2:
        backend = "gpt"
        checkOpenAIKey()
    elif model == 3:
        backend = "g4f"
    elif model == 4:
        backend = "api"
        checkAPI()
    else:
        return main()
    
    session = SESSIONS_DIR / f"session{len(sessions) + 1}.json"
    Eva(session, backend).chat()

if __name__ == "__main__":
    main()
