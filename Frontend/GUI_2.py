import os
import sys
import tkinter as tk
from tkinter import scrolledtext, filedialog
import json
from PIL import Image, ImageTk, ImageSequence
from dotenv import dotenv_values

# ────────────────────────────────────────────────────────────────
#  Using standard tkinter.ttk for consistent styling
# ────────────────────────────────────────────────────────────────
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog

# ────────────────────────────────────────────────────────────────
#  Environment + shared helpers — keep identical public API so the
#  rest of your stack does not break. You asked to maintain the
#  function names; done ✔️
# ────────────────────────────────────────────────────────────────
# ────────────────────────────────────────────────────────────────
#  Modern Design System & Styling Constants
# ────────────────────────────────────────────────────────────────

# High-end color palette
BG_DARK      = "#131313"  # Deep black/grey
BG_GLASS     = "#1c1c1c"  # Semi-transparent feel
BG_HIGHLIGHT = "#2d2d2d"  # Hover/Select
ACCENT_BLUE  = "#3b82f6"  # Premium Blue
ACCENT_RED   = "#ef4444"  # Alert/Mic ON
TEXT_PRIMARY = "#ececf1"  # Soft White
TEXT_SEC     = "#9ca3af"  # Dim Grey

env_vars        = dotenv_values(".env")
Assistantname   = env_vars.get("Assistantname", "OmniAgent")
BASE_DIR        = os.getcwd()
TempDirPath     = rf"{BASE_DIR}\Frontend\Files"
GraphicsDirPath = rf"{BASE_DIR}\Frontend\Graphics"
old_chat_message = ""

def GraphicsDirectoryPath(name): return rf"{GraphicsDirPath}\{name}"
def TempDirectoryPath(name):      return rf"{TempDirPath}\{name}"

def AnswerModifier(ans):
    ans = ans.strip()
    return "\n".join(l.strip() for l in ans.splitlines() if l.strip())

def QueryModifier(q):
    q = q.lower().strip()
    if any(w+" " in q for w in ("how","what","who","where","when","why","which", "whose","whom","can you","what's","where's","how's")):
        q = q.rstrip(".?!") + "?"
    else:
        q = q.rstrip(".?!") + "."
    return q.capitalize()

# Data Access Helpers
def SetMicrophoneStatus(cmd): open(TempDirectoryPath("Mic.data"),"w",encoding="utf-8").write(cmd)
def GetMicrophoneStatus():    return open(TempDirectoryPath("Mic.data"),encoding="utf-8").read()
def SetAssistantStatus(s):    open(TempDirectoryPath("Status.data"),"w",encoding="utf-8").write(s)
def GetAssistantStatus():     return open(TempDirectoryPath("Status.data"),encoding="utf-8").read()
def SetInputMode(mode):       open(TempDirectoryPath("InputMode.data"),"w",encoding="utf-8").write(mode)
def GetInputMode():           return open(TempDirectoryPath("InputMode.data"),encoding="utf-8").read() if os.path.exists(TempDirectoryPath("InputMode.data")) else "voice"
def SetSpeakerStatus(s):      open(TempDirectoryPath("Speaker.data"),"w",encoding="utf-8").write(s)
def GetSpeakerStatus():       return open(TempDirectoryPath("Speaker.data"),encoding="utf-8").read() if os.path.exists(TempDirectoryPath("Speaker.data")) else "on"
def ShowTextToScreen(t):      open(TempDirectoryPath("Responses.data"),"w",encoding="utf-8").write(t)
def SetTextQuery(q):          open(TempDirectoryPath("TextQuery.data"),"w",encoding="utf-8").write(q)
def GetTextQuery():           return open(TempDirectoryPath("TextQuery.data"),encoding="utf-8").read() if os.path.exists(TempDirectoryPath("TextQuery.data")) else ""

def SetBgColor(color):   
    try: open(TempDirectoryPath("BgColor.data"),"w",encoding="utf-8").write(color)
    except: pass
def SetUserColor(color): 
    try: open(TempDirectoryPath("UserColor.data"),"w",encoding="utf-8").write(color)
    except: pass
def SetAssistantColor(color): 
    try: open(TempDirectoryPath("AssistantColor.data"),"w",encoding="utf-8").write(color)
    except: pass
def SetFontSize(size):   
    try: open(TempDirectoryPath("FontSize.data"),"w",encoding="utf-8").write(str(size))
    except: pass
def SetTheme(t):
    try: open(TempDirectoryPath("Theme.data"),"w",encoding="utf-8").write(t)
    except: pass

def MicButtonInitialed(): SetMicrophoneStatus("False")
def MicButtonClosed():    SetMicrophoneStatus("True")

def GetTheme():          
    try: return open(TempDirectoryPath("Theme.data"),encoding="utf-8").read().strip()
    except: return "dark"
def GetBgColor():        
    try: return open(TempDirectoryPath("BgColor.data"),encoding="utf-8").read().strip()
    except: return "#131313"
def GetUserColor():      
    try: return open(TempDirectoryPath("UserColor.data"),encoding="utf-8").read().strip()
    except: return "#3b82f6"
def GetAssistantColor(): 
    try: return open(TempDirectoryPath("AssistantColor.data"),encoding="utf-8").read().strip()
    except: return "#10b981"
def GetFontSize():       
    try: return int(open(TempDirectoryPath("FontSize.data"),encoding="utf-8").read().strip())
    except: return 12

# Chat log management
def LoadChatLog():
    chat_log_path = os.path.join(BASE_DIR, "Data", "ChatLog.json")
    if os.path.exists(chat_log_path):
        with open(chat_log_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def SaveChatLog(chat_log):
    chat_log_path = os.path.join(BASE_DIR, "Data", "ChatLog.json")
    with open(chat_log_path, "w", encoding="utf-8") as f:
        json.dump(chat_log, f, indent=2, ensure_ascii=False)

# ────────────────────────────────────────────────────────────────
#  Sidebar for navigation and settings
# ────────────────────────────────────────────────────────────────
class Sidebar(ttk.Frame):
    def __init__(self, master, main_chat):
        super().__init__(master, style="Sidebar.TFrame", width=260)
        self.main_chat = main_chat
        self.chat_log = LoadChatLog()
        self.current_chat_id = None

        # Floating New Chat button
        self.new_chat_btn = ttk.Button(self, text="+ New Chat", command=self._new_chat, style="Premium.TButton")
        self.new_chat_btn.pack(fill=tk.X, padx=15, pady=(20, 15))

        # Conversations Frame
        self.conv_container = tk.Frame(self, bg=BG_DARK)
        self.conv_container.pack(fill=tk.BOTH, expand=True, padx=5)

        self.canvas = tk.Canvas(self.conv_container, bg=BG_DARK, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.conv_container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=BG_DARK)

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=240)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        # Scrollbar is hidden for a cleaner look, it works via mousewheel
        # self.scrollbar.pack(side="right", fill="y") 

        # Footer Settings
        self.footer = tk.Frame(self, bg=BG_DARK, height=60)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        self.settings_btn = ttk.Button(self.footer, text="⚙️ Settings", command=self._open_settings, style="Ghost.TButton")
        self.settings_btn.pack(fill=tk.X, padx=15)

        self._load_conversations()

        if self.chat_log:
            self._select_chat(self.chat_log[0])
        else:
            self._new_chat() # Start a new chat if none exist

    def _get_bg_color(self):
        # This method is now largely superseded by global BG_DARK, but kept for compatibility
        themes = {"dark": BG_DARK, "light": "#ffffff", "day": "#e3f2fd"}
        return themes.get(GetTheme(), BG_DARK)

    def _load_conversations(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        for conv in self.chat_log:
            # Use a custom frame for each conversation item for better styling
            conv_item_frame = tk.Frame(self.scroll_frame, bg=BG_DARK, bd=0, relief=tk.FLAT)
            conv_item_frame.pack(fill=tk.X, pady=2, padx=5)
            
            # Highlight selected chat
            if self.current_chat_id == conv["id"]:
                conv_item_frame.configure(bg=BG_HIGHLIGHT)

            name_label = tk.Label(conv_item_frame, text=conv["name"], 
                                  bg=conv_item_frame.cget("bg"), fg=TEXT_PRIMARY,
                                  font=("Inter", 10), anchor="w", padx=5)
            name_label.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)

            # Rename button (smaller, subtle)
            rename_btn = tk.Button(conv_item_frame, text="✎", 
                                   bg=conv_item_frame.cget("bg"), fg=TEXT_SEC,
                                   activebackground=BG_HIGHLIGHT, activeforeground=ACCENT_BLUE,
                                   bd=0, font=("Segoe UI", 9), cursor="hand2",
                                   command=lambda c=conv: self._rename_chat(c))
            rename_btn.pack(side=tk.RIGHT, padx=(0, 2))

            # Delete button (smaller, subtle)
            delete_btn = tk.Button(conv_item_frame, text="✕", 
                                   bg=conv_item_frame.cget("bg"), fg=TEXT_SEC,
                                   activebackground=BG_HIGHLIGHT, activeforeground=ACCENT_RED,
                                   bd=0, font=("Segoe UI", 9), cursor="hand2",
                                   command=lambda c=conv: self._delete_chat(c))
            delete_btn.pack(side=tk.RIGHT)

            # Bind click to select chat
            name_label.bind("<Button-1>", lambda e, c=conv: self._select_chat(c))
            conv_item_frame.bind("<Button-1>", lambda e, c=conv: self._select_chat(c))
            
            # Change background on hover
            conv_item_frame.bind("<Enter>", lambda e, f=conv_item_frame: f.config(bg=BG_HIGHLIGHT))
            conv_item_frame.bind("<Leave>", lambda e, f=conv_item_frame, c=conv: f.config(bg=BG_HIGHLIGHT if self.current_chat_id == c["id"] else BG_DARK))
            name_label.bind("<Enter>", lambda e, f=conv_item_frame: f.config(bg=BG_HIGHLIGHT))
            name_label.bind("<Leave>", lambda e, f=conv_item_frame, c=conv: f.config(bg=BG_HIGHLIGHT if self.current_chat_id == c["id"] else BG_DARK))


    def _new_chat(self):
        new_id = max([c.get("id", 0) for c in self.chat_log], default=0) + 1
        new_conv = {"id": new_id, "name": f"Chat {new_id}", "messages": []}
        self.chat_log.insert(0, new_conv) # Insert at the beginning
        SaveChatLog(self.chat_log)
        self._load_conversations()
        self._select_chat(new_conv)

    def _select_chat(self, conv):
        # Reload from disk to get backend's updates
        self.chat_log = LoadChatLog()
        # Find the matching conversation in the new log
        target_conv = next((c for c in self.chat_log if c["id"] == conv["id"]), conv)
        self.current_chat_id = target_conv["id"]
        if self.main_chat:
            self.main_chat.load_chat(target_conv.get("messages", []))
        with open(TempDirectoryPath("CurrentChat.data"), "w", encoding="utf-8") as f:
            f.write(str(conv["id"]))
        # Trigger backend reload
        SetAssistantStatus("Loading Chat...")
        self._load_conversations() # Reload to highlight selected chat

    def _rename_chat(self, conv):
        new_name = simpledialog.askstring("Rename Chat", "Enter new name:", initialvalue=conv["name"],
                                          parent=self.master)
        if new_name and new_name.strip():
            conv["name"] = new_name.strip()
            SaveChatLog(self.chat_log)
            self._load_conversations()

    def _delete_chat(self, conv):
        if messagebox.askyesno("Delete Chat", f"Delete '{conv['name']}'?", parent=self.master):
            self.chat_log.remove(conv)
            SaveChatLog(self.chat_log)
            self._load_conversations()
            if self.chat_log:
                self._select_chat(self.chat_log[0])
            else:
                if self.main_chat:
                    self.main_chat.load_chat([])
                self.current_chat_id = None # No chat selected
                self._new_chat() # Create a new empty chat

    def _open_settings(self):
        # Open a settings window with more options
        settings_win = tk.Toplevel(self)
        settings_win.title("Settings")
        settings_win.geometry("400x400")
        settings_win.configure(bg=BG_DARK)
        settings_win.transient(self.master) # Make it appear on top of the main window
        settings_win.grab_set() # Make it modal

        # Apply a style to the settings window
        s = ttk.Style()
        s.configure("Settings.TFrame", background=BG_DARK)
        s.configure("Settings.TLabel", background=BG_DARK, foreground=TEXT_PRIMARY, font=("Inter", 10))
        s.configure("Settings.TButton", background=ACCENT_BLUE, foreground="white", font=("Inter", 10, "bold"), relief="flat")
        s.map("Settings.TButton", background=[('active', BG_HIGHLIGHT)])
        s.configure("Settings.TCombobox", fieldbackground=BG_GLASS, background=BG_DARK, foreground=TEXT_PRIMARY, selectbackground=ACCENT_BLUE, selectforeground="white")
        s.configure("Settings.TSpinbox", fieldbackground=BG_GLASS, background=BG_DARK, foreground=TEXT_PRIMARY)


        settings_frame = ttk.Frame(settings_win, style="Settings.TFrame", padding=15)
        settings_frame.pack(fill=tk.BOTH, expand=True)

        # Theme (simplified as GetTheme is hardcoded for now)
        ttk.Label(settings_frame, text="Theme:", style="Settings.TLabel").pack(pady=5, anchor="w")
        theme_var = tk.StringVar(value=GetTheme())
        theme_combo = ttk.Combobox(settings_frame, textvariable=theme_var, values=["dark"], state="readonly", style="Settings.TCombobox")
        theme_combo.pack(fill=tk.X, pady=5)
        # theme_combo.bind("<<ComboboxSelected>>", lambda e: self._change_theme(theme_var.get()))

        # Background Color (simplified)
        ttk.Label(settings_frame, text="Background Color:", style="Settings.TLabel").pack(pady=5, anchor="w")
        bg_color_var = tk.StringVar(value=GetBgColor())
        bg_color_combo = ttk.Combobox(settings_frame, textvariable=bg_color_var, values=[BG_DARK], state="readonly", style="Settings.TCombobox")
        bg_color_combo.pack(fill=tk.X, pady=5)
        # bg_color_combo.bind("<<ComboboxSelected>>", lambda e: self._change_bg_color(bg_color_var.get()))

        # User Text Color (simplified)
        ttk.Label(settings_frame, text="User Text Color:", style="Settings.TLabel").pack(pady=5, anchor="w")
        user_color_var = tk.StringVar(value=GetUserColor())
        user_color_combo = ttk.Combobox(settings_frame, textvariable=user_color_var, values=[ACCENT_BLUE], state="readonly", style="Settings.TCombobox")
        user_color_combo.pack(fill=tk.X, pady=5)
        # user_color_combo.bind("<<ComboboxSelected>>", lambda e: self._change_user_color(user_color_var.get()))

        # Assistant Text Color (simplified)
        ttk.Label(settings_frame, text="Assistant Text Color:", style="Settings.TLabel").pack(pady=5, anchor="w")
        assistant_color_var = tk.StringVar(value=GetAssistantColor())
        assistant_color_combo = ttk.Combobox(settings_frame, textvariable=assistant_color_var, values=["#10b981"], state="readonly", style="Settings.TCombobox")
        assistant_color_combo.pack(fill=tk.X, pady=5)
        # assistant_color_combo.bind("<<ComboboxSelected>>", lambda e: self._change_assistant_color(assistant_color_var.get()))

        # Font Size (still functional)
        ttk.Label(settings_frame, text="Font Size:", style="Settings.TLabel").pack(pady=5, anchor="w")
        font_size_var = tk.IntVar(value=GetFontSize())
        font_size_spin = tk.Spinbox(settings_frame, from_=8, to=24, textvariable=font_size_var, 
                                    bg=BG_GLASS, fg=TEXT_PRIMARY, insertbackground=ACCENT_BLUE,
                                    buttonbackground=BG_HIGHLIGHT, highlightthickness=0, bd=0,
                                    font=("Inter", 10))
        font_size_spin.pack(fill=tk.X, pady=5)
        font_size_spin.bind("<FocusOut>", lambda e: self._change_font_size(font_size_var.get()))
        font_size_spin.bind("<<Increment>>", lambda e: self._change_font_size(font_size_var.get()))
        font_size_spin.bind("<<Decrement>>", lambda e: self._change_font_size(font_size_var.get()))

        ttk.Button(settings_frame, text="Clear Current Chat", command=self.main_chat.clear_chat, style="Settings.TButton").pack(pady=10)
        
        settings_win.wait_window() # Wait for settings window to close

    def _change_theme(self, theme):
        SetTheme(theme)
        # Set default background color for the theme
        theme_bgs = {"dark": BG_DARK, "light": "#ffffff", "day": "#e3f2fd"}
        # SetBgColor(theme_bgs.get(theme, BG_DARK)) # This is now hardcoded in GetBgColor
        # Apply theme to main window (assuming main_chat has access)
        if hasattr(self.main_chat, 'master') and hasattr(self.main_chat.master, 'apply_theme'):
            self.main_chat.master.apply_theme(theme)

    def _change_bg_color(self, color):
        # SetBgColor(color) # This is now hardcoded in GetBgColor
        if hasattr(self.main_chat, 'master') and hasattr(self.main_chat.master, 'apply_theme'):
            self.main_chat.master.apply_theme(GetTheme())

    def _change_user_color(self, color):
        # SetUserColor(color) # This is now hardcoded in GetUserColor
        if self.main_chat:
            self.main_chat._update_tags()

    def _change_assistant_color(self, color):
        # SetAssistantColor(color) # This is now hardcoded in GetAssistantColor
        if self.main_chat:
            self.main_chat._update_tags()

    def _change_font_size(self, size):
        SetFontSize(size)
        if self.main_chat:
            self.main_chat._update_tags()

# Sidebar.add_message was removed in favor of Backend-driven persistence (Main.py)

# ────────────────────────────────────────────────────────────────
#  Main Chat Area with rich text support
# ────────────────────────────────────────────────────────────────
class MainChat(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_DARK)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Chat display area - Using a canvas for bubble-like rendering would be ideal, 
        # but for text reliability we use Text with heavy padding
        self.chat_text = tk.Text(self, wrap=tk.WORD, state=tk.DISABLED, 
                                 bg=BG_DARK, fg=TEXT_PRIMARY,
                                 font=("Inter", 12), relief=tk.FLAT, 
                                 padx=40, pady=20, borderwidth=0, highlightthickness=0)
        
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.chat_text.yview)
        self.chat_text.configure(yscrollcommand=self.scrollbar.set)

        self.chat_text.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns") # Keep scrollbar visible

        # Floating Input Bar
        self.input_container = tk.Frame(self, bg=BG_DARK, pady=20)
        self.input_container.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.input_glass = tk.Frame(self.input_container, bg=BG_GLASS, bd=1, relief=tk.FLAT, highlightbackground=BG_HIGHLIGHT, highlightthickness=1,
                                    # Add rounded corners effect
                                    # This is a visual trick, actual rounded corners require canvas or custom drawing
                                    # For simplicity, we'll just use a slightly rounded border effect if possible with ttk/tk
                                    )
        self.input_glass.pack(fill=tk.X, padx=60, ipady=5)

        self.input_text = tk.Text(self.input_glass, height=1, wrap=tk.WORD, 
                                  bg=BG_GLASS, fg=TEXT_PRIMARY, 
                                  insertbackground=ACCENT_BLUE,
                                  font=("Inter", 13), relief=tk.FLAT, 
                                  padx=15, pady=10, borderwidth=0)
        self.input_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Toggles Row
        self.ctrl_frame = tk.Frame(self.input_glass, bg=BG_GLASS)
        self.ctrl_frame.pack(side=tk.RIGHT, padx=5)

        self.mic_btn = tk.Button(self.ctrl_frame, text="🎙️", bg=BG_GLASS, fg=TEXT_PRIMARY, 
                                 activebackground=BG_HIGHLIGHT, activeforeground=ACCENT_RED,
                                 bd=0, command=self._toggle_mic, font=("Segoe UI", 14), cursor="hand2")
        self.mic_btn.pack(side=tk.LEFT, padx=5)

        self.speaker_btn = tk.Button(self.ctrl_frame, text="🔊", bg=BG_GLASS, fg=TEXT_PRIMARY,
                                     activebackground=BG_HIGHLIGHT, activeforeground=ACCENT_BLUE,
                                     bd=0, command=self._toggle_speaker, font=("Segoe UI", 12), cursor="hand2")
        self.speaker_btn.pack(side=tk.LEFT, padx=5)

        self.send_btn = tk.Button(self.ctrl_frame, text="↑", bg=ACCENT_BLUE, fg="white", 
                                  width=3, height=1, bd=0, command=self._send_message, 
                                  font=("Segoe UI", 12, "bold"), cursor="hand2",
                                  activebackground=BG_HIGHLIGHT, activeforeground=ACCENT_BLUE)
        self.send_btn.pack(side=tk.LEFT, padx=10)

        # Bind keys
        self.input_text.bind('<Return>', self._on_enter)
        self.input_text.bind('<Shift-Return>', self._on_shift_enter)
        self.input_text.bind('<KeyRelease>', self._adjust_input_height)

        self.sidebar = None  # Will be set later
        self.old_chat_message = ""
        self.last_status = ""
        self.mic_state = False
        self.speaker_state = GetSpeakerStatus() == "on"

        self._poll()

    def set_sidebar(self, sidebar):
        self.sidebar = sidebar

    def load_chat(self, messages):
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.delete(1.0, tk.END)
        for msg in messages:
            self._insert_message(msg["role"], msg["content"])
        self.chat_text.configure(state=tk.DISABLED)
        self.chat_text.see(tk.END)

    def _insert_message(self, role, content):
        self.chat_text.configure(state=tk.NORMAL)
        
        # Determine tag (user or assistant)
        tag = "user" if role.lower() == "user" else "assistant"
        
        # Display name with appropriate styling
        name = "You" if tag == "user" else Assistantname
        self.chat_text.insert(tk.END, f"{name}\n", (tag, "bold"))
        
        # Message body
        lines = content.split('\n')
        for line in lines:
            if line.startswith('```'):
                self.chat_text.insert(tk.END, line + '\n', "code")
            else:
                self.chat_text.insert(tk.END, line + '\n', tag)
        
        self.chat_text.insert(tk.END, '\n' + '─'*40 + '\n\n', "sep")
        self.chat_text.configure(state=tk.DISABLED)
        self.chat_text.see(tk.END)
        self._update_tags()

    def _send_message(self):
        content = self.input_text.get("1.0", tk.END).strip()
        if content:
            # We don't insert here because we want the backend's MainExecution 
            # to process it and then it will appear via polling.
            # However, for immediate user feedback, we can insert:
            # self._insert_message("user", content)
            
            SetTextQuery(content)
            self.input_text.delete("1.0", tk.END)
            self._adjust_input_height()
            # We don't call sidebar.add_message here because Main.py 
            # will save it to JSON and we will see it via polling.

    def _add_assistant_response(self, content):
        self._insert_message("assistant", content)
        self.chat_text.see(tk.END)

    def _poll(self):
        # Poll for responses from the backend
        try:
            with open(TempDirectoryPath("Responses.data"), "r", encoding="utf-8") as f:
                txt = f.read().strip()
        except FileNotFoundError:
            txt = ""

        if txt and txt != self.old_chat_message:
            # Main.py sends query as "User : Query" or response as "Assistant : Answer"
            if " : " in txt:
                parts = txt.split(" : ", 1)
                role = parts[0].strip().lower()
                content = parts[1].strip()
                # Only insert if it's new (simple heuristic)
                self._insert_message(role, content)
            else:
                # Fallback if no delimiter
                self._insert_message("assistant", txt)
            
            self.old_chat_message = txt

        # Poll for status updates
        try:
            with open(TempDirectoryPath("Status.data"), "r", encoding="utf-8") as f:
                status = f.read().strip()
        except FileNotFoundError:
            status = ""
        
        if status != self.last_status:
            # You might want to display status somewhere in MainChat if needed
            self.last_status = status

        self.after(200, self._poll)

    def _on_enter(self, event):
        self._send_message()
        return 'break'

    def _on_shift_enter(self, event):
        # Allow newline
        pass

    def _adjust_input_height(self, event=None):
        # Adjust height based on content
        content = self.input_text.get("1.0", tk.END)
        lines = content.count('\n') + 1
        self.input_text.configure(height=min(max(lines, 3), 10))  # Min 3, max 10 lines

    def _attach_file(self):
        file_path = filedialog.askopenfilename(title="Select file", filetypes=[("All files", "*.*")])
        if file_path:
            # For simplicity, just insert file path as message
            self.input_text.insert(tk.END, f"[Attachment: {os.path.basename(file_path)}] ")

    def _toggle_mic(self):
        self.mic_state = not self.mic_state
        if self.mic_state:
            SetMicrophoneStatus("False") # False means LISTENING in Main.py logic check
            self.mic_btn.configure(text="🔴")
        else:
            SetMicrophoneStatus("True") # True means MUTED
            self.mic_btn.configure(text="🎙️")

    def _toggle_speaker(self):
        self.speaker_state = not self.speaker_state
        status = "on" if self.speaker_state else "off"
        SetSpeakerStatus(status)
        self.speaker_btn.configure(text="🔊" if self.speaker_state else "🔇")

    def _update_tags(self):
        sz = GetFontSize()
        # Use simple string names for fonts to be safer with tk
        self.chat_text.tag_configure("user", foreground=GetUserColor(), font=("Inter", sz), spacing1=5)
        self.chat_text.tag_configure("assistant", foreground=GetAssistantColor(), font=("Inter", sz), spacing1=5)
        self.chat_text.tag_configure("code", font=("Consolas", sz), background="#1e1e1e", foreground="#d4d4d4", relief="flat")
        self.chat_text.tag_configure("bold", font=("Inter", sz, "bold"))
        self.chat_text.tag_configure("sep", foreground=BG_HIGHLIGHT, justify="center")

    def clear_chat(self):
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.delete(1.0, tk.END)
        self.chat_text.configure(state=tk.DISABLED)
        if self.sidebar and self.sidebar.current_chat_id:
            for conv in self.sidebar.chat_log:
                if conv["id"] == self.sidebar.current_chat_id:
                    conv["messages"] = []
                    SaveChatLog(self.sidebar.chat_log)
                    break

# Note: Tab-based classes (ChatTab, HomeTab, SettingsTab) have been removed 
# in favor of the new Sidebar-based Premium Interface.

# ────────────────────────────────────────────────────────────────
#  Main window – either ttkbootstrap.Window or classic tk.Tk
# ────────────────────────────────────────────────────────────────
_BaseWindow = tk.Tk

class MainWindow(_BaseWindow):
    def __init__(self):
        super().__init__()

        self.title(f"{Assistantname.capitalize()} AI")
        self.state("zoomed")  # maximised
        self.current_theme = GetTheme()

        # ttk styles --------------------------------------------------
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.apply_theme(self.current_theme)

        # PanedWindow for sidebar and main chat -------------------------
        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RAISED)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Sidebar (collapsible)
        self.sidebar = Sidebar(self.paned, None)  # main_chat will be set later
        self.paned.add(self.sidebar, width=200, minsize=150)

        # Main Chat Area
        self.main_chat = MainChat(self.paned)
        self.main_chat.set_sidebar(self.sidebar)
        self.sidebar.main_chat = self.main_chat  # Set reference
        self.paned.add(self.main_chat, width=600)

        # Load initial chat
        if self.sidebar.chat_log:
            self.main_chat.load_chat(self.sidebar.chat_log[0]["messages"])

    def _update_styles(self):
        t = {
            "bg": BG_DARK,
            "sidebar": "#171717",
            "accent": ACCENT_BLUE,
            "text": TEXT_PRIMARY,
            "sub": TEXT_SEC
        }
        self.configure(bg=t["bg"])
        self.style.configure("Sidebar.TFrame", background=t["sidebar"])
        self.style.configure("Sidebar.TLabel", background=t["sidebar"], foreground=t["text"], font=("Segoe UI", 10))
        self.style.configure("Premium.TButton", background=t["accent"], foreground="white", font=("Segoe UI", 10, "bold"))
        self.style.configure("Ghost.TButton", background=t["sidebar"], foreground=t["sub"], font=("Segoe UI", 10))
        
        if hasattr(self, 'main_chat') and self.main_chat:
            self.main_chat.chat_text.configure(bg=BG_DARK, fg=TEXT_PRIMARY)
            self.main_chat.input_glass.configure(bg=BG_GLASS)
            self.main_chat.input_text.configure(bg=BG_GLASS, fg=TEXT_PRIMARY)

    def apply_theme(self, theme):
        self.current_theme = theme
        self._update_styles()
        if hasattr(self, 'sidebar'):
            self.sidebar.canvas.configure(bg=BG_DARK)
            self.sidebar._load_conversations()
        if hasattr(self, 'main_chat'):
            self.main_chat.chat_text.configure(bg=BG_DARK, fg=TEXT_PRIMARY)
            self.main_chat._update_tags()

# ────────────────────────────────────────────────────────────────
#  Public entry point
# ────────────────────────────────────────────────────────────────

def GraphicalUserInterface():
    MainWindow().mainloop()

if __name__ == "__main__":
    GraphicalUserInterface()


