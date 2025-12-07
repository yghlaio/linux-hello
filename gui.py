#!/usr/bin/env python3
"""
GUI Application for Face Authentication System
Simple Tkinter-based interface for user and sample management
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from pathlib import Path
from datetime import datetime
import logging

from models import Database
from face_auth import FaceAuthenticator
from sample_manager import SampleManager
from config import get_config, Config

logger = logging.getLogger(__name__)


class FaceAuthGUI:
    """Main GUI application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Face Authentication System")
        self.root.geometry("900x600")
        
        # Initialize components
        self.config = get_config()
        self.db = Database(self.config.get('database.path'))
        self.authenticator = FaceAuthenticator(self.db)
        self.sample_mgr = SampleManager(self.db)
        
        # Create UI
        self.create_menu()
        self.create_notebook()
        
        # Refresh data
        self.refresh_users()
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh", command=self.refresh_all)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_notebook(self):
        """Create tabbed interface"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_users_tab()
        self.create_samples_tab()
        self.create_settings_tab()
        self.create_logs_tab()
    
    def create_dashboard_tab(self):
        """Dashboard tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Dashboard")
        
        # Status frame
        status_frame = ttk.LabelFrame(frame, text="System Status", padding=10)
        status_frame.pack(fill='x', padx=10, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="Loading...", font=('Arial', 12))
        self.status_label.pack()
        
        # Quick actions
        actions_frame = ttk.LabelFrame(frame, text="Quick Actions", padding=10)
        actions_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(actions_frame, text="Test Authentication", 
                  command=self.test_auth).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="Enroll New User", 
                  command=self.enroll_user).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="Refresh", 
                  command=self.refresh_all).pack(side='left', padx=5)
        
        # Update status
        self.update_dashboard()
    
    def create_users_tab(self):
        """Users management tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Users")
        
        # Toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(toolbar, text="Add User", command=self.enroll_user).pack(side='left', padx=2)
        ttk.Button(toolbar, text="Remove User", command=self.remove_user).pack(side='left', padx=2)
        ttk.Button(toolbar, text="Refresh", command=self.refresh_users).pack(side='left', padx=2)
        
        # Users list
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Listbox
        self.users_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                        font=('Arial', 11))
        self.users_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.users_listbox.yview)
        
        # Bind selection
        self.users_listbox.bind('<<ListboxSelect>>', self.on_user_select)
        
        # Info frame
        self.user_info_frame = ttk.LabelFrame(frame, text="User Information", padding=10)
        self.user_info_frame.pack(fill='x', padx=5, pady=5)
        
        self.user_info_label = ttk.Label(self.user_info_frame, text="Select a user to view details")
        self.user_info_label.pack()
    
    def create_samples_tab(self):
        """Samples management tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Samples")
        
        # User selection
        select_frame = ttk.Frame(frame)
        select_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(select_frame, text="User:").pack(side='left', padx=5)
        self.sample_user_var = tk.StringVar()
        self.sample_user_combo = ttk.Combobox(select_frame, textvariable=self.sample_user_var, 
                                              state='readonly')
        self.sample_user_combo.pack(side='left', fill='x', expand=True, padx=5)
        self.sample_user_combo.bind('<<ComboboxSelected>>', self.on_sample_user_select)
        
        # Toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(toolbar, text="Add Sample", command=self.add_sample).pack(side='left', padx=2)
        ttk.Button(toolbar, text="Remove Sample", command=self.remove_sample).pack(side='left', padx=2)
        
        # Samples list
        self.samples_text = scrolledtext.ScrolledText(frame, height=15, font=('Courier', 10))
        self.samples_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_settings_tab(self):
        """Settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Settings")
        
        # Settings display
        self.settings_text = scrolledtext.ScrolledText(frame, height=20, font=('Courier', 10))
        self.settings_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Reload Settings", 
                  command=self.load_settings).pack(side='left', padx=5)
        ttk.Label(btn_frame, text="(Edit config.yaml file to change settings)").pack(side='left', padx=5)
        
        self.load_settings()
    
    def create_logs_tab(self):
        """Logs tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Logs")
        
        # Toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(toolbar, text="Refresh Logs", command=self.refresh_logs).pack(side='left', padx=2)
        
        # Logs display
        self.logs_text = scrolledtext.ScrolledText(frame, height=20, font=('Courier', 9))
        self.logs_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.refresh_logs()
    
    # Event handlers
    def update_dashboard(self):
        """Update dashboard status"""
        users = self.db.get_all_users()
        status = f"✅ System Active | {len(users)} users enrolled"
        self.status_label.config(text=status)
    
    def refresh_all(self):
        """Refresh all data"""
        self.refresh_users()
        self.refresh_logs()
        self.update_dashboard()
        messagebox.showinfo("Refresh", "Data refreshed successfully")
    
    def refresh_users(self):
        """Refresh users list"""
        self.users_listbox.delete(0, tk.END)
        users = self.db.get_all_users()
        
        for user in users:
            sample_count = self.db.get_sample_count(user.username)
            self.users_listbox.insert(tk.END, f"{user.username} ({sample_count} samples)")
        
        # Update combo box
        usernames = [u.username for u in users]
        if hasattr(self, 'sample_user_combo'):
            self.sample_user_combo['values'] = usernames
        
        self.update_dashboard()
    
    def on_user_select(self, event):
        """Handle user selection"""
        selection = self.users_listbox.curselection()
        if not selection:
            return
        
        username = self.users_listbox.get(selection[0]).split(' (')[0]
        user = self.db.get_user(username)
        
        if user:
            info = f"Username: {user.username}\n"
            info += f"Enrolled: {user.enrolled_at}\n"
            info += f"Last Seen: {user.last_seen or 'Never'}\n"
            info += f"Samples: {self.db.get_sample_count(username)}"
            self.user_info_label.config(text=info)
    
    def on_sample_user_select(self, event):
        """Handle sample user selection"""
        username = self.sample_user_var.get()
        if not username:
            return
        
        samples = self.db.get_user_samples(username)
        self.samples_text.delete('1.0', tk.END)
        
        if samples:
            self.samples_text.insert('1.0', f"User: {username}\n")
            self.samples_text.insert(tk.END, f"Total Samples: {len(samples)}\n\n")
            for i, sample in enumerate(samples):
                self.samples_text.insert(tk.END, f"Sample {i}: {len(sample)} features\n")
        else:
            self.samples_text.insert('1.0', "No samples found")
    
    def enroll_user(self):
        """Enroll new user"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Enroll User")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="Username:").pack(pady=10)
        username_entry = ttk.Entry(dialog, width=30)
        username_entry.pack(pady=5)
        username_entry.focus()
        
        def do_enroll():
            username = username_entry.get().strip()
            if not username:
                messagebox.showerror("Error", "Username cannot be empty")
                return
            
            dialog.destroy()
            self.root.withdraw()  # Hide main window
            
            # Run enrollment
            success = self.authenticator.enroll_user(username, show_preview=True)
            
            self.root.deiconify()  # Show main window
            
            if success:
                messagebox.showinfo("Success", f"User {username} enrolled successfully!")
                self.refresh_users()
            else:
                messagebox.showerror("Error", "Enrollment failed")
        
        ttk.Button(dialog, text="Start Enrollment", command=do_enroll).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack()
    
    def remove_user(self):
        """Remove selected user"""
        selection = self.users_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        username = self.users_listbox.get(selection[0]).split(' (')[0]
        
        if messagebox.askyesno("Confirm", f"Remove user '{username}'?"):
            if self.db.remove_user(username):
                messagebox.showinfo("Success", f"User {username} removed")
                self.refresh_users()
            else:
                messagebox.showerror("Error", "Failed to remove user")
    
    def add_sample(self):
        """Add sample to user"""
        username = self.sample_user_var.get()
        if not username:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        self.root.withdraw()
        success = self.sample_mgr.add_sample_from_camera(username)
        self.root.deiconify()
        
        if success:
            messagebox.showinfo("Success", "Sample added successfully!")
            self.on_sample_user_select(None)
        else:
            messagebox.showerror("Error", "Failed to add sample")
    
    def remove_sample(self):
        """Remove sample from user"""
        username = self.sample_user_var.get()
        if not username:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        # Ask for index
        dialog = tk.Toplevel(self.root)
        dialog.title("Remove Sample")
        dialog.geometry("300x120")
        
        ttk.Label(dialog, text=f"Sample index to remove (0-{self.db.get_sample_count(username)-1}):").pack(pady=10)
        index_entry = ttk.Entry(dialog, width=10)
        index_entry.pack(pady=5)
        
        def do_remove():
            try:
                index = int(index_entry.get())
                dialog.destroy()
                
                if self.db.remove_sample(username, index):
                    messagebox.showinfo("Success", f"Sample {index} removed")
                    self.on_sample_user_select(None)
                else:
                    messagebox.showerror("Error", "Failed to remove sample")
            except ValueError:
                messagebox.showerror("Error", "Invalid index")
        
        ttk.Button(dialog, text="Remove", command=do_remove).pack(pady=5)
    
    def test_auth(self):
        """Test authentication"""
        self.root.withdraw()
        
        success, username, confidence = self.authenticator.authenticate(timeout=10, show_preview=True)
        
        self.root.deiconify()
        
        if success:
            messagebox.showinfo("Success", f"Authenticated as {username}\nConfidence: {confidence:.2f}")
        else:
            messagebox.showwarning("Failed", "Authentication failed")
    
    def load_settings(self):
        """Load and display settings"""
        self.settings_text.delete('1.0', tk.END)
        
        # Read config file
        config_path = Path(__file__).parent / 'config.yaml'
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.settings_text.insert('1.0', f.read())
    
    def refresh_logs(self):
        """Refresh logs display"""
        self.logs_text.delete('1.0', tk.END)
        
        # Get recent logs
        auth_logs = self.db.get_auth_logs(50)
        
        self.logs_text.insert('1.0', "=== Authentication Logs ===\n\n")
        for log in auth_logs:
            status = "✅" if log.success else "❌"
            self.logs_text.insert(tk.END, 
                f"{status} {log.timestamp} | {log.username or 'Unknown'} | {log.event_type}\n")
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", 
            "Face Authentication System\n\n"
            "A Linux face recognition authentication system\n"
            "similar to Windows Hello\n\n"
            "Version 1.0")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = FaceAuthGUI(root)
    root.mainloop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
