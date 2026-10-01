import os
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# ---------- settings ----------
DB = dict(host="localhost", user="root",
          password=os.environ.get("DB_PASSWORD", ""), database="mydb")

# Expected table:
# CREATE TABLE user (id VARCHAR(20) PRIMARY KEY, name VARCHAR(50), password VARCHAR(100));

FONT = "Segoe UI"
SIDE = "#0b3c49"        # left panel
SIDE_TEXT = "#bfd8de"
PRIMARY = "#0b3c49"
PRIMARY_HOVER = "#082c36"
LINK = "#0b7285"
INK = "#1b2a30"
MUTED = "#5f7278"
FIELD = "#eef3f4"
LINE = "#d5e0e2"
PAPER = "#ffffff"


def get_connection():
    return mysql.connector.connect(**DB)


class HoverButton(tk.Button):
    def __init__(self, master, bg=PRIMARY, hover=PRIMARY_HOVER, **kw):
        super().__init__(master, bg=bg, activebackground=hover, fg="white",
                         activeforeground="white", relief="flat", bd=0,
                         cursor="hand2", font=(FONT, 11, "bold"), **kw)
        self.bind("<Enter>", lambda e: self.config(bg=hover))
        self.bind("<Leave>", lambda e: self.config(bg=bg))


def make_field(parent, label, secret=False):
    tk.Label(parent, text=label, font=(FONT, 10, "bold"), fg=MUTED,
             bg=PAPER).pack(anchor="w", pady=(14, 4))
    box = tk.Frame(parent, bg=FIELD, highlightthickness=1,
                   highlightbackground=LINE, highlightcolor=LINK)
    box.pack(fill="x")
    entry = tk.Entry(box, font=(FONT, 12), bg=FIELD, fg=INK, relief="flat",
                     bd=0, insertbackground=INK, show="•" if secret else "")
    entry.pack(fill="x", padx=12, pady=9)
    return entry


def make_link(parent, text, command):
    lbl = tk.Label(parent, text=text, font=(FONT, 10, "underline"), fg=LINK,
                   bg=PAPER, cursor="hand2")
    lbl.bind("<Button-1>", lambda e: command())
    return lbl


class App:
    def __init__(self, root):
        self.root = root
        root.title("Account Portal")
        w, h = 900, 620
        x = (root.winfo_screenwidth() - w) // 2
        y = (root.winfo_screenheight() - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")
        root.resizable(False, False)
        root.configure(bg=PAPER)
        self.show_login()

    # ---------- helpers ----------
    def clear(self):
        self.root.unbind("<Return>")
        for w in self.root.winfo_children():
            w.destroy()

    def shell(self, heading, tagline):
        """Left colour panel + empty right-hand form area (returned)."""
        self.clear()
        left = tk.Frame(self.root, bg=SIDE, width=340)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Label(left, text=heading, font=(FONT, 28, "bold"), fg="white",
                 bg=SIDE, justify="left").pack(anchor="w", padx=40, pady=(190, 10))
        tk.Label(left, text=tagline, font=(FONT, 12), fg=SIDE_TEXT, bg=SIDE,
                 justify="left", wraplength=260).pack(anchor="w", padx=40)

        form = tk.Frame(self.root, bg=PAPER)
        form.pack(side="right", fill="both", expand=True, padx=70, pady=50)
        return form

    @staticmethod
    def title(form, text, sub):
        tk.Label(form, text=text, font=(FONT, 24, "bold"), fg=INK,
                 bg=PAPER).pack(anchor="w")
        tk.Label(form, text=sub, font=(FONT, 11), fg=MUTED,
                 bg=PAPER).pack(anchor="w", pady=(2, 6))

    @staticmethod
    def password_toggle(form, entries):
        var = tk.BooleanVar()

        def toggle():
            for e in entries:
                e.config(show="" if var.get() else "•")

        tk.Checkbutton(form, text="Show password", variable=var, command=toggle,
                       font=(FONT, 10), fg=MUTED, bg=PAPER, activebackground=PAPER,
                       selectcolor=PAPER, bd=0, cursor="hand2").pack(anchor="w", pady=(10, 0))

    # ---------- login ----------
    def show_login(self):
        form = self.shell("Welcome\nback", "Sign in to see your account and pick up where you left off.")
        self.title(form, "Sign in", "Enter your username and password.")
        self.user_entry = make_field(form, "Username")
        self.pass_entry = make_field(form, "Password", secret=True)
        self.password_toggle(form, [self.pass_entry])

        HoverButton(form, text="Sign in", command=self.do_login).pack(fill="x", pady=(24, 0), ipady=8)

        row = tk.Frame(form, bg=PAPER)
        row.pack(pady=18)
        tk.Label(row, text="New here?", font=(FONT, 10), fg=MUTED, bg=PAPER).pack(side="left")
        make_link(row, " Create an account", self.show_register).pack(side="left")

        self.root.bind("<Return>", lambda e: self.do_login())
        self.user_entry.focus()

    def do_login(self):
        name, pwd = self.user_entry.get().strip(), self.pass_entry.get()
        if not name or not pwd:
            messagebox.showwarning("Missing details", "Enter both username and password.", parent=self.root)
            return
        con = None
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("SELECT id FROM user WHERE name=%s AND password=%s", (name, pwd))
            if cur.fetchone() is None:
                messagebox.showerror("Sign in failed", "Username or password is incorrect.", parent=self.root)
            else:
                self.show_app(name)
        except Exception as es:
            messagebox.showerror("Database error", str(es), parent=self.root)
        finally:
            if con:
                con.close()

    # ---------- register ----------
    def show_register(self):
        form = self.shell("Join us", "Create an account in under a minute.")
        self.title(form, "Create account", "Fill in the details below.")
        self.r_name = make_field(form, "Username")
        self.r_id = make_field(form, "User ID")
        self.r_pass = make_field(form, "Password", secret=True)
        self.r_conf = make_field(form, "Confirm password", secret=True)
        self.password_toggle(form, [self.r_pass, self.r_conf])

        HoverButton(form, text="Create account", command=self.do_register).pack(fill="x", pady=(20, 0), ipady=8)

        row = tk.Frame(form, bg=PAPER)
        row.pack(pady=14)
        tk.Label(row, text="Already registered?", font=(FONT, 10), fg=MUTED, bg=PAPER).pack(side="left")
        make_link(row, " Sign in", self.show_login).pack(side="left")

        self.root.bind("<Return>", lambda e: self.do_register())
        self.r_name.focus()

    def do_register(self):
        name, uid = self.r_name.get().strip(), self.r_id.get().strip()
        pwd, conf = self.r_pass.get(), self.r_conf.get()
        if not (name and uid and pwd and conf):
            messagebox.showwarning("Missing details", "All fields are required.", parent=self.root)
            return
        if pwd != conf:
            messagebox.showwarning("Passwords differ", "Password and confirmation must match.", parent=self.root)
            return
        con = None
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("SELECT id FROM user WHERE name=%s OR id=%s", (name, uid))
            if cur.fetchone():
                messagebox.showerror("Already taken", "That username or ID is already in use.", parent=self.root)
                return
            cur.execute("INSERT INTO user (id, name, password) VALUES (%s, %s, %s)", (uid, name, pwd))
            con.commit()
            messagebox.showinfo("Account created", "You can sign in now.", parent=self.root)
            self.show_login()
        except Exception as es:
            messagebox.showerror("Database error", str(es), parent=self.root)
        finally:
            if con:
                con.close()

    # ---------- after login ----------
    def show_app(self, username):
        self.clear()
        bar = tk.Frame(self.root, bg=SIDE, height=76)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Label(bar, text=f"Hello, {username}", font=(FONT, 18, "bold"),
                 fg="white", bg=SIDE).pack(side="left", padx=34)
        HoverButton(bar, text="Sign out", bg="#145466", hover="#1b6a80",
                    command=self.show_login, width=12).pack(side="right", padx=34, ipady=4)

        body = tk.Frame(self.root, bg=PAPER)
        body.pack(fill="both", expand=True, padx=34, pady=26)
        tk.Label(body, text="Registered users", font=(FONT, 14, "bold"),
                 fg=INK, bg=PAPER).pack(anchor="w", pady=(0, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=(FONT, 11), rowheight=34, background=PAPER,
                        fieldbackground=PAPER, foreground=INK, borderwidth=0)
        style.configure("Treeview.Heading", font=(FONT, 10, "bold"), background=FIELD,
                        foreground=INK, relief="flat", padding=8)
        style.map("Treeview", background=[("selected", LINK)],
                  foreground=[("selected", "white")])

        wrap = tk.Frame(body, bg=PAPER, highlightthickness=1, highlightbackground=LINE)
        wrap.pack(fill="both", expand=True)
        tree = ttk.Treeview(wrap, columns=("id", "name"), show="headings")
        tree.heading("id", text="ID", anchor="w")
        tree.heading("name", text="Username", anchor="w")
        tree.column("id", width=160, anchor="w")
        tree.column("name", width=400, anchor="w")
        scroll = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        con = None
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("SELECT id, name FROM user")
            for row in cur.fetchall():
                tree.insert("", "end", values=row)
        except Exception as es:
            messagebox.showerror("Database error", str(es), parent=self.root)
        finally:
            if con:
                con.close()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
