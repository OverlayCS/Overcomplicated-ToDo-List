import tkinter as tk
from tkinter import messagebox, filedialog, ttk, simpledialog
import json
import random
import time

class OvercomplicatedToDo:
    def __init__(self, root):
        self.root = root
        self.root.title("ToDo List App")
        self.root.geometry("1000x900")
        
        self.dark_mode = False
        self.tasks = []
        self.history = []
        self.redo_stack = []
        self.auto_save_enabled = False
        self.create_widgets()

        # Automatically save every 10 seconds if auto-save is enabled
        self.auto_save_timer()

    def create_widgets(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.root.configure(bg="#282C34")
        
        self.header = tk.Label(self.root, text="ToDo List App", font=("Arial", 14, "bold"), fg="white", bg="#282C34")
        self.header.pack(pady=10)
        
        self.task_entry = tk.Entry(self.root, width=50)
        self.task_entry.pack(pady=5)
        
        self.priority = ttk.Combobox(self.root, values=["Low", "Medium", "High"], state="readonly")
        self.priority.set("Medium")
        self.priority.pack(pady=5)
        
        self.category_label = tk.Label(self.root, text="Category:", fg="white", bg="#282C34")
        self.category_label.pack()
        self.category_entry = tk.Entry(self.root, width=50)
        self.category_entry.pack(pady=5)
        
        self.undo_button = self.create_rounded_button("Undo", self.undo, state=tk.DISABLED)
        self.redo_button = self.create_rounded_button("Redo", self.redo, state=tk.DISABLED)
        self.create_rounded_button("Add Task", self.add_task)
        self.create_rounded_button("Delete Task", self.delete_task)
        self.create_rounded_button("Save Tasks", self.save_tasks)
        self.create_rounded_button("Load Tasks", self.load_tasks)
        self.create_rounded_button("Toggle Dark Mode", self.toggle_dark_mode)
        self.create_rounded_button("Toggle Auto Save", self.toggle_auto_save)
        self.create_rounded_button("Clear All", self.clear_all_tasks)
        
        self.search_entry = tk.Entry(self.root, width=50)
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", self.search_tasks)
        
        self.task_listbox = tk.Listbox(self.root, width=60, height=15, bg="#3A3F4B", fg="white")
        self.task_listbox.pack(pady=10)
        
        self.task_listbox.bind("<Double-Button-1>", self.edit_task)
    
    def create_rounded_button(self, text, command, state=tk.NORMAL):
        button = tk.Button(self.root, text=text, command=command, bg="#61AFEF", fg="white", relief="flat", bd=5, activebackground="#528BEB", state=state, padx=15, pady=5)
        button.pack(pady=2, ipadx=10, ipady=5)
        return button
    
    def edit_task(self, event):
        selected_index = self.task_listbox.curselection()
        if not selected_index:
            return
        
        index = selected_index[0]
        task_text = self.task_listbox.get(index)
        new_task = simpledialog.askstring("Edit Task", "Modify your task:", initialvalue=task_text)
        
        if new_task:
            self.task_listbox.delete(index)
            self.task_listbox.insert(index, new_task)
            self.tasks[index] = new_task
        
    def add_task(self):
        task = self.task_entry.get().strip()
        if not task:
            task = f"Task {random.randint(1000, 9999)}"
        
        priority = self.priority.get()
        category = self.category_entry.get()
        self.tasks.append((task, priority, category))
        self.task_listbox.insert(tk.END, f"[{priority}] {task} - ({category})")
        self.task_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.history.append(("add", (task, priority, category)))
        self.undo_button.config(state=tk.NORMAL)
        
        if self.auto_save_enabled:
            self.save_tasks()
        
    def delete_task(self):
        selected_index = self.task_listbox.curselection()
        if not selected_index:
            return
        index = selected_index[0]
        task = self.tasks.pop(index)
        self.task_listbox.delete(index)
        self.history.append(("delete", task))
        self.undo_button.config(state=tk.NORMAL)
    
    def save_tasks(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, "w") as file:
                json.dump(self.tasks, file)
            messagebox.showinfo("Save Tasks", "Tasks saved successfully!")
        
    def load_tasks(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, "r") as file:
                self.tasks = json.load(file)
            self.task_listbox.delete(0, tk.END)
            for task, priority, category in self.tasks:
                self.task_listbox.insert(tk.END, f"[{priority}] {task} - ({category})")
            messagebox.showinfo("Load Tasks", "Tasks loaded successfully!")
    
    def undo(self):
        if self.history:
            action, data = self.history.pop()
            if action == "add":
                self.tasks.remove(data)
                self.task_listbox.delete(tk.END)
                self.redo_stack.append(("remove", data))
                self.redo_button.config(state=tk.NORMAL)
        if not self.history:
            self.undo_button.config(state=tk.DISABLED)
    
    def redo(self):
        if self.redo_stack:
            action, data = self.redo_stack.pop()
            if action == "remove":
                self.tasks.append(data)
                self.task_listbox.insert(tk.END, f"[{data[1]}] {data[0]} - ({data[2]})")
                self.history.append(("add", data))
                self.undo_button.config(state=tk.NORMAL)
        if not self.redo_stack:
            self.redo_button.config(state=tk.DISABLED)
    
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        new_bg = "#282C34" if self.dark_mode else "#FFFFFF"
        new_fg = "white" if self.dark_mode else "black"
        self.root.configure(bg=new_bg)
        self.header.configure(bg=new_bg, fg=new_fg)
        self.category_label.configure(bg=new_bg, fg=new_fg)
    
    def toggle_auto_save(self):
        self.auto_save_enabled = not self.auto_save_enabled
        messagebox.showinfo("Auto Save", f"Auto Save {'Enabled' if self.auto_save_enabled else 'Disabled'}")
    
    def clear_all_tasks(self):
        self.tasks.clear()
        self.task_listbox.delete(0, tk.END)
        messagebox.showinfo("Clear Tasks", "All tasks cleared!")
    
    def search_tasks(self, event):
        query = self.search_entry.get().lower()
        self.task_listbox.delete(0, tk.END)
        for task, priority, category in self.tasks:
            if query in task.lower() or query in category.lower():
                self.task_listbox.insert(tk.END, f"[{priority}] {task} - ({category})")
    
    def auto_save_timer(self):
        if self.auto_save_enabled:
            self.save_tasks()
        self.root.after(10000, self.auto_save_timer)  # Save every 10 seconds

if __name__ == "__main__":
    root = tk.Tk()
    app = OvercomplicatedToDo(root)
    root.mainloop()
