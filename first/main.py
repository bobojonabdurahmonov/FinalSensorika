import tkinter as tk
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
from datetime import datetime
import sqlite3
import json
import os
from tkinter import scrolledtext

DB_FILE = "journal.db"

class JournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kundalik - Shaxsiy Jurnal")
        self.root.geometry("1400x850")
        self.root.configure(bg="#0f172a")
        
        self.is_logged_in = False
        self.current_user = None
        self.current_entry_id = None
        self.users = []
        self.entries = []
        
        self.init_database()
        self.load_users()
        
        self.show_login_screen()
    
    def init_database(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS entries
                     (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, 
                      content TEXT, mood TEXT, tags TEXT)''')
        conn.commit()
        conn.close()
    
    def load_users(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT id, username, password FROM users')
        self.users = c.fetchall()
        conn.close()
    
    def load_user_entries(self, user_id):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT id, date, content, mood, tags FROM entries WHERE user_id=? ORDER BY date DESC', (user_id,))
        self.entries = c.fetchall()
        conn.close()
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        self.clear_window()
        
        # Main container - Dark background
        main_frame = tk.Frame(self.root, bg="#0f172a")
        main_frame.pack(fill=BOTH, expand=True)
        
        # Left side - Branding
        left_frame = tk.Frame(main_frame, bg="#1e293b")
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        brand_frame = tk.Frame(left_frame, bg="#1e293b")
        brand_frame.pack(fill=BOTH, expand=True, padx=40, pady=100)
        
        title = tk.Label(brand_frame, text="📔", font=("Arial", 100), bg="#1e293b")
        title.pack(pady=20)
        
        tk.Label(brand_frame, text="KUNDALIK", font=("Arial", 56, "bold"), 
                fg="#e0f2fe", bg="#1e293b").pack()
        tk.Label(brand_frame, text="Sizning shaxsiy daftaringiz", font=("Arial", 18), 
                fg="#94a3b8", bg="#1e293b").pack(pady=20)
        tk.Label(brand_frame, text="🔐 Xavfsiz • 💾 Shifrlangan • ⚡ Tezkor", 
                font=("Arial", 13), fg="#64748b", bg="#1e293b").pack(pady=10)
        
        # Right side - Login form
        right_frame = tk.Frame(main_frame, bg="#0f172a")
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=60, pady=60)
        
        tk.Label(right_frame, text="Hush Kelibsiz", font=("Arial", 42, "bold"), 
                fg="white", bg="#0f172a").pack(pady=(0, 10), anchor=W)
        tk.Label(right_frame, text="Kundalikka kirish", font=("Arial", 16), 
                fg="#94a3b8", bg="#0f172a").pack(pady=(0, 40), anchor=W)
        
        # Username
        tk.Label(right_frame, text="Foydalanuvchi nomi", font=("Arial", 12, "bold"), 
                fg="#e0f2fe", bg="#0f172a").pack(anchor=W, pady=(20, 8))
        username_var = tk.StringVar()
        username_entry = tk.Entry(right_frame, textvariable=username_var, 
                                 width=32, font=("Arial", 12),
                                 bg="#1e293b", fg="white", 
                                 insertbackground="white",
                                 relief="flat", bd=1)
        username_entry.pack(fill=X, pady=(0, 20), ipady=12)
        
        # Password
        tk.Label(right_frame, text="Parol", font=("Arial", 12, "bold"), 
                fg="#e0f2fe", bg="#0f172a").pack(anchor=W, pady=(0, 8))
        password_var = tk.StringVar()
        password_entry = tk.Entry(right_frame, textvariable=password_var, 
                                 width=32, font=("Arial", 12),
                                 bg="#1e293b", fg="white", 
                                 insertbackground="white",
                                 show="●", relief="flat", bd=1)
        password_entry.pack(fill=X, pady=(0, 30), ipady=12)
        
        # Message
        message = tk.Label(right_frame, text="", font=("Arial", 11), bg="#0f172a")
        message.pack(anchor=W, pady=(0, 20))
        
        def login():
            username = username_var.get()
            password = password_var.get()
            
            user = next((u for u in self.users if u[1] == username and u[2] == password), None)
            if user:
                self.is_logged_in = True
                self.current_user = user[0]
                self.load_user_entries(self.current_user)
                self.show_main_screen()
            else:
                message.config(text="❌ Noto'g'ri foydalanuvchi nomi yoki parol!", fg="#f87171")
        
        def register():
            username = username_var.get()
            password = password_var.get()
            
            if not username or not password:
                message.config(text="❌ Hammasini to'ldiring!", fg="#f87171")
                return
            
            if any(u[1] == username for u in self.users):
                message.config(text="❌ Bu foydalanuvchi nomi allaqachon mavjud!", fg="#f87171")
                return
            
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            
            self.load_users()
            message.config(text="✅ Ro'yxatdan o'tdingiz! Endi kiring.", fg="#4ade80")
            username_var.set("")
            password_var.set("")
        
        # Buttons
        btn_frame = tk.Frame(right_frame, bg="#0f172a")
        btn_frame.pack(fill=X, pady=(20, 0))
        
        login_btn = tk.Button(btn_frame, text="🔓 KIRISH", command=login,
                             font=("Arial", 12, "bold"), fg="white", bg="#0ea5e9",
                             activebackground="#06b6d4", activeforeground="white",
                             relief="flat", bd=0, cursor="hand2", padx=20, pady=12)
        login_btn.pack(side=LEFT, padx=(0, 10), fill=X, expand=True)
        
        register_btn = tk.Button(btn_frame, text="📝 O'TISH", command=register,
                                font=("Arial", 12, "bold"), fg="#e0f2fe", bg="#1e293b",
                                activebackground="#0ea5e9", activeforeground="white",
                                relief="flat", bd=0, cursor="hand2", padx=20, pady=12)
        register_btn.pack(side=LEFT, fill=X, expand=True)
    
    def show_main_screen(self):
        self.clear_window()
        
        self.root.configure(bg="#0f172a")
        
        # Top Header
        header = tk.Frame(self.root, bg="#1e293b", height=70)
        header.pack(fill=X, padx=0, pady=0)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg="#1e293b")
        header_content.pack(fill=BOTH, expand=True, padx=25, pady=15)
        
        tk.Label(header_content, text="❤️  KUNDALIK", font=("Arial", 22, "bold"), 
                fg="white", bg="#1e293b").pack(side=LEFT)
        
        logout_btn = tk.Button(header_content, text="🚪 CHIQISH", command=self.logout,
                              font=("Arial", 11, "bold"), fg="white", bg="#ef4444",
                              activebackground="#dc2626", activeforeground="white",
                              relief="flat", bd=0, cursor="hand2", padx=15, pady=8)
        logout_btn.pack(side=RIGHT)
        
        # Main content
        main_content = tk.Frame(self.root, bg="#0f172a")
        main_content.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Left Sidebar - Entries List
        left_panel = tk.Frame(main_content, bg="#1e293b", relief="flat")
        left_panel.pack(side=LEFT, fill=BOTH, expand=False, padx=(0, 20), ipady=0)
        left_panel.configure(highlightthickness=0)
        
        # Header in left panel
        left_header = tk.Frame(left_panel, bg="#1e293b")
        left_header.pack(fill=X, padx=20, pady=20)
        
        tk.Label(left_header, text="🔍 QIDIRUV", font=("Arial", 11, "bold"), 
                fg="#e0f2fe", bg="#1e293b").pack(anchor=W, pady=(0, 10))
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(left_header, textvariable=search_var, 
                               width=22, font=("Arial", 11),
                               bg="#0f172a", fg="white",
                               insertbackground="#0ea5e9",
                               relief="flat", bd=1)
        search_entry.pack(fill=X, ipady=10)
        
        # Entries list title
        tk.Label(left_panel, text="📅 YOZUVLAR", font=("Arial", 11, "bold"), 
                fg="#e0f2fe", bg="#1e293b").pack(anchor=W, padx=20, pady=(20, 10))
        
        # Listbox frame
        listbox_frame = tk.Frame(left_panel, bg="#1e293b")
        listbox_frame.pack(fill=BOTH, expand=True, padx=15, pady=(0, 15))
        
        scrollbar = ttk.Scrollbar(listbox_frame, bootstyle="info-round")
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.entries_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, 
                                          font=("Arial", 9), height=20, width=28,
                                          bg="#0f172a", fg="#e0f2fe", relief="flat", 
                                          bd=0, selectmode=SINGLE, 
                                          selectbackground="#0ea5e9",
                                          selectforeground="white",
                                          highlightthickness=0)
        self.entries_listbox.pack(fill=BOTH, expand=True, side=LEFT)
        scrollbar.config(command=self.entries_listbox.yview)
        
        self.entries_listbox.bind('<<ListboxSelect>>', self.load_entry)
        
        def filter_entries(*args):
            self.refresh_entries_list(search_var.get())
        
        search_var.trace('w', filter_entries)
        self.refresh_entries_list()
        
        # Right Panel - Editor
        right_panel = tk.Frame(main_content, bg="#1e293b", relief="flat")
        right_panel.pack(side=RIGHT, fill=BOTH, expand=True)
        right_panel.configure(highlightthickness=0)
        
        # Padding frame
        padding = tk.Frame(right_panel, bg="#1e293b")
        padding.pack(fill=BOTH, expand=True, padx=25, pady=20)
        
        tk.Label(padding, text="✏️  YOZUV TAHRIRLASH", font=("Arial", 16, "bold"), 
                fg="white", bg="#1e293b").pack(anchor=W, pady=(0, 25))
        
        # Date and mood in one row
        top_row = tk.Frame(padding, bg="#1e293b")
        top_row.pack(fill=X, pady=(0, 20))
        
        # Date frame
        date_col = tk.Frame(top_row, bg="#1e293b")
        date_col.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 15))
        
        tk.Label(date_col, text="📅 SANA", font=("Arial", 10, "bold"), 
                fg="#e0f2fe", bg="#1e293b").pack(anchor=W, pady=(0, 5))
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.date_entry = tk.Entry(date_col, textvariable=self.date_var, 
                                   width=15, font=("Arial", 10),
                                   bg="#0f172a", fg="white",
                                   insertbackground="#0ea5e9",
                                   relief="flat", bd=1)
        self.date_entry.pack(fill=X, ipady=8)
        
        # Mood selector
        mood_label = tk.Label(padding, text="😊 KAYFIYAT", font=("Arial", 10, "bold"), 
                             fg="#e0f2fe", bg="#1e293b")
        mood_label.pack(anchor=W, pady=(0, 10))
        
        mood_frame = tk.Frame(padding, bg="#1e293b")
        mood_frame.pack(fill=X, pady=(0, 20))
        
        self.mood_var = tk.StringVar(value="😐 Oddiy")
        moods = [("😊 Xursand", "😊 Xursand"), ("😐 Oddiy", "😐 Oddiy"), 
                ("😢 Xafa", "😢 Xafa"), ("😔 Jahlidor", "😔 Jahlidor")]
        
        for mood_emoji, mood_text in moods:
            mood_btn = tk.Radiobutton(mood_frame, text=mood_emoji, variable=self.mood_var, 
                                     value=mood_text, font=("Arial", 9, "bold"),
                                     bg="#1e293b", fg="#e0f2fe", 
                                     activebackground="#1e293b",
                                     activeforeground="#0ea5e9",
                                     selectcolor="#0f172a", bd=0)
            mood_btn.pack(side=LEFT, padx=8)
        
        # Tags
        tk.Label(padding, text="#️⃣ TEGLAR", font=("Arial", 10, "bold"), 
                fg="#e0f2fe", bg="#1e293b").pack(anchor=W, pady=(0, 5))
        self.tags_var = tk.StringVar()
        tags_entry = tk.Entry(padding, textvariable=self.tags_var, 
                             font=("Arial", 10),
                             bg="#0f172a", fg="white",
                             insertbackground="#0ea5e9",
                             relief="flat", bd=1)
        tags_entry.pack(fill=X, pady=(0, 20), ipady=8)
        
        # Content
        tk.Label(padding, text="📝 MATN", font=("Arial", 10, "bold"), 
                fg="#e0f2fe", bg="#1e293b").pack(anchor=W, pady=(0, 8))
        self.content_text = scrolledtext.ScrolledText(padding, height=16, width=55, 
                                                      font=("Arial", 10), wrap=WORD,
                                                      bg="#0f172a", fg="#e0f2fe", 
                                                      relief="flat", bd=1,
                                                      insertbackground="#0ea5e9")
        self.content_text.pack(fill=BOTH, expand=True, pady=(0, 20))
        
        # Buttons
        btn_frame = tk.Frame(padding, bg="#1e293b")
        btn_frame.pack(fill=X)
        
        save_btn = tk.Button(btn_frame, text="💾 SAQLASH", command=self.save_entry,
                            font=("Arial", 11, "bold"), fg="white", bg="#22c55e",
                            activebackground="#16a34a", activeforeground="white",
                            relief="flat", bd=0, cursor="hand2", padx=15, pady=10)
        save_btn.pack(side=LEFT, padx=(0, 10), fill=X, expand=True)
        
        delete_btn = tk.Button(btn_frame, text="🗑️ O'CHIRISH", command=self.delete_entry,
                              font=("Arial", 11, "bold"), fg="white", bg="#ef4444",
                              activebackground="#dc2626", activeforeground="white",
                              relief="flat", bd=0, cursor="hand2", padx=15, pady=10)
        delete_btn.pack(side=LEFT, padx=(0, 10), fill=X, expand=True)
        
        new_btn = tk.Button(btn_frame, text="🆕 YANGI", command=self.new_entry,
                           font=("Arial", 11, "bold"), fg="white", bg="#0ea5e9",
                           activebackground="#06b6d4", activeforeground="white",
                           relief="flat", bd=0, cursor="hand2", padx=15, pady=10)
        new_btn.pack(side=LEFT, fill=X, expand=True)
    
    def refresh_entries_list(self, search_query=""):
        self.entries_listbox.delete(0, END)
        
        for entry_id, date, content, mood, tags in self.entries:
            if search_query.lower() in content.lower() or search_query.lower() in (tags or "").lower():
                preview = content.replace('\n', ' ')[:35]
                display_text = f"{mood} {date}\n{preview}..."
                self.entries_listbox.insert(END, display_text)
    
    def load_entry(self, event):
        selection = self.entries_listbox.curselection()
        if selection:
            idx = selection[0]
            entry_id, date, content, mood, tags = self.entries[idx]
            
            self.current_entry_id = entry_id
            self.date_var.set(date)
            self.mood_var.set(mood)
            self.tags_var.set(tags or "")
            self.content_text.delete(1.0, END)
            self.content_text.insert(1.0, content)
    
    def save_entry(self):
        content = self.content_text.get(1.0, END).strip()
        if not content:
            return
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        try:
            if self.current_entry_id:
                c.execute('''UPDATE entries SET content=?, mood=?, tags=?, date=? WHERE id=?''',
                         (content, self.mood_var.get(), self.tags_var.get(), 
                          self.date_var.get(), self.current_entry_id))
            else:
                c.execute('''INSERT INTO entries (user_id, date, content, mood, tags) 
                           VALUES (?, ?, ?, ?, ?)''',
                         (self.current_user, self.date_var.get(), content, 
                          self.mood_var.get(), self.tags_var.get()))
            conn.commit()
        finally:
            conn.close()
        
        self.load_user_entries(self.current_user)
        self.refresh_entries_list()
        self.new_entry()
    
    def delete_entry(self):
        if not self.current_entry_id:
            return
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('DELETE FROM entries WHERE id=?', (self.current_entry_id,))
        conn.commit()
        conn.close()
        
        self.load_user_entries(self.current_user)
        self.refresh_entries_list()
        self.new_entry()
    
    def new_entry(self):
        self.current_entry_id = None
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.mood_var.set("😐 Oddiy")
        self.tags_var.set("")
        self.content_text.delete(1.0, END)
    
    def logout(self):
        self.is_logged_in = False
        self.current_user = None
        self.entries = []
        self.show_login_screen()

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="#0f172a")
    app = JournalApp(root)
    root.mainloop()