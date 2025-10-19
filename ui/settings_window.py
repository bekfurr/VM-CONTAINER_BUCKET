#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Settings Window - Dastur sozlamalari
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from utils.config_manager import ConfigManager

class SettingsWindow:
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config_manager = config_manager
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Sozlamalar")
        self.dialog.geometry("600x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """UI ni sozlash"""
        # Asosiy frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Sarlavha
        title_label = ttk.Label(main_frame, text="Dastur Sozlamalari", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Notebook (tablar)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Tablarni yaratish
        self.setup_general_tab()
        self.setup_docker_tab()
        self.setup_virtualbox_tab()
        self.setup_hyperv_tab()
        
        # Tugmalar
        self.setup_buttons(main_frame)
        
    def setup_general_tab(self):
        """Umumiy sozlamalar tabini sozlash"""
        self.general_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.general_frame, text="Umumiy")
        
        # Til sozlamalari
        language_frame = ttk.LabelFrame(self.general_frame, text="Til sozlamalari", padding="10")
        language_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(language_frame, text="Til:").grid(row=0, column=0, sticky="w", pady=5)
        self.language_var = tk.StringVar()
        language_combo = ttk.Combobox(language_frame, textvariable=self.language_var, width=20)
        language_combo['values'] = ["uz", "en", "ru"]
        language_combo.grid(row=0, column=1, sticky="w", pady=5)
        
        # Mavzu sozlamalari
        theme_frame = ttk.LabelFrame(self.general_frame, text="Mavzu sozlamalari", padding="10")
        theme_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(theme_frame, text="Mavzu:").grid(row=0, column=0, sticky="w", pady=5)
        self.theme_var = tk.StringVar()
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, width=20)
        theme_combo['values'] = ["light", "dark"]
        theme_combo.grid(row=0, column=1, sticky="w", pady=5)
        
        # Yangilash sozlamalari
        refresh_frame = ttk.LabelFrame(self.general_frame, text="Yangilash sozlamalari", padding="10")
        refresh_frame.pack(fill="x", pady=(0, 10))
        
        self.auto_refresh_var = tk.BooleanVar()
        ttk.Checkbutton(refresh_frame, text="Avtomatik yangilash", 
                       variable=self.auto_refresh_var).grid(row=0, column=0, sticky="w", pady=5)
        
        ttk.Label(refresh_frame, text="Yangilash intervali (soniya):").grid(row=1, column=0, sticky="w", pady=5)
        self.refresh_interval_var = tk.StringVar()
        ttk.Entry(refresh_frame, textvariable=self.refresh_interval_var, width=10).grid(row=1, column=1, sticky="w", pady=5)
        
        # Log sozlamalari
        log_frame = ttk.LabelFrame(self.general_frame, text="Log sozlamalari", padding="10")
        log_frame.pack(fill="x", pady=(0, 10))
        
        self.enable_logging_var = tk.BooleanVar()
        ttk.Checkbutton(log_frame, text="Loglarni yoqish", 
                       variable=self.enable_logging_var).grid(row=0, column=0, sticky="w", pady=5)
        
        ttk.Label(log_frame, text="Log fayl yo'li:").grid(row=1, column=0, sticky="w", pady=5)
        self.log_path_var = tk.StringVar()
        log_path_frame = ttk.Frame(log_frame)
        log_path_frame.grid(row=1, column=1, sticky="ew", pady=5)
        ttk.Entry(log_path_frame, textvariable=self.log_path_var, width=30).pack(side="left", padx=(0, 5))
        ttk.Button(log_path_frame, text="Tanlash", command=self.select_log_path).pack(side="left")
        
        # Dastur haqida
        about_frame = ttk.LabelFrame(self.general_frame, text="Dastur haqida", padding="10")
        about_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(about_frame, text="VM-Container Bucket v1.0", font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Label(about_frame, text="Virtual mashina va konteyner boshqaruv dasturi").pack(anchor="w")
        ttk.Label(about_frame, text="Python 3.7+ | Tkinter GUI").pack(anchor="w")
        
    def setup_docker_tab(self):
        """Docker sozlamalari tabini sozlash"""
        self.docker_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.docker_frame, text="Docker")
        
        # Docker ulanish sozlamalari
        connection_frame = ttk.LabelFrame(self.docker_frame, text="Ulanish sozlamalari", padding="10")
        connection_frame.pack(fill="x", pady=(0, 10))
        
        self.docker_auto_connect_var = tk.BooleanVar()
        ttk.Checkbutton(connection_frame, text="Avtomatik ulanish", 
                       variable=self.docker_auto_connect_var).pack(anchor="w", pady=5)
        
        # Docker default sozlamalari
        defaults_frame = ttk.LabelFrame(self.docker_frame, text="Default sozlamalar", padding="10")
        defaults_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(defaults_frame, text="Default portlar:").grid(row=0, column=0, sticky="w", pady=5)
        self.docker_ports_var = tk.StringVar()
        ttk.Entry(defaults_frame, textvariable=self.docker_ports_var, width=30).grid(row=0, column=1, pady=5)
        
    def setup_virtualbox_tab(self):
        """VirtualBox sozlamalari tabini sozlash"""
        self.virtualbox_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.virtualbox_frame, text="VirtualBox")
        
        # VirtualBox ulanish sozlamalari
        connection_frame = ttk.LabelFrame(self.virtualbox_frame, text="Ulanish sozlamalari", padding="10")
        connection_frame.pack(fill="x", pady=(0, 10))
        
        self.vbox_auto_connect_var = tk.BooleanVar()
        ttk.Checkbutton(connection_frame, text="Avtomatik ulanish", 
                       variable=self.vbox_auto_connect_var).pack(anchor="w", pady=5)
        
        # VirtualBox default sozlamalari
        defaults_frame = ttk.LabelFrame(self.virtualbox_frame, text="Default sozlamalar", padding="10")
        defaults_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(defaults_frame, text="Default xotira (MB):").grid(row=0, column=0, sticky="w", pady=5)
        self.vbox_memory_var = tk.StringVar()
        ttk.Entry(defaults_frame, textvariable=self.vbox_memory_var, width=20).grid(row=0, column=1, pady=5)
        
        ttk.Label(defaults_frame, text="Default CPU soni:").grid(row=1, column=0, sticky="w", pady=5)
        self.vbox_cpus_var = tk.StringVar()
        ttk.Entry(defaults_frame, textvariable=self.vbox_cpus_var, width=20).grid(row=1, column=1, pady=5)
        
    def setup_hyperv_tab(self):
        """Hyper-V sozlamalari tabini sozlash"""
        self.hyperv_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.hyperv_frame, text="Hyper-V")
        
        # Hyper-V ulanish sozlamalari
        connection_frame = ttk.LabelFrame(self.hyperv_frame, text="Ulanish sozlamalari", padding="10")
        connection_frame.pack(fill="x", pady=(0, 10))
        
        self.hyperv_auto_connect_var = tk.BooleanVar()
        ttk.Checkbutton(connection_frame, text="Avtomatik ulanish", 
                       variable=self.hyperv_auto_connect_var).pack(anchor="w", pady=5)
        
        # Hyper-V default sozlamalari
        defaults_frame = ttk.LabelFrame(self.hyperv_frame, text="Default sozlamalar", padding="10")
        defaults_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(defaults_frame, text="Default xotira (MB):").grid(row=0, column=0, sticky="w", pady=5)
        self.hyperv_memory_var = tk.StringVar()
        ttk.Entry(defaults_frame, textvariable=self.hyperv_memory_var, width=20).grid(row=0, column=1, pady=5)
        
        ttk.Label(defaults_frame, text="Default CPU soni:").grid(row=1, column=0, sticky="w", pady=5)
        self.hyperv_cpus_var = tk.StringVar()
        ttk.Entry(defaults_frame, textvariable=self.hyperv_cpus_var, width=20).grid(row=1, column=1, pady=5)
        
    def setup_buttons(self, parent):
        """Tugmalarni sozlash"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="Saqlash", 
                  command=self.save_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Qayta tiklash", 
                  command=self.reset_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Eksport qilish", 
                  command=self.export_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Import qilish", 
                  command=self.import_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Yopish", 
                  command=self.dialog.destroy).pack(side="right", padx=5)
        
    def load_settings(self):
        """Sozlamalarni yuklash"""
        # Umumiy sozlamalar
        self.language_var.set(self.config_manager.get("language", "uz"))
        self.theme_var.set(self.config_manager.get("theme", "light"))
        self.auto_refresh_var.set(self.config_manager.get("auto_refresh", True))
        self.refresh_interval_var.set(str(self.config_manager.get("refresh_interval", 30)))
        self.enable_logging_var.set(self.config_manager.get("enable_logging", False))
        self.log_path_var.set(self.config_manager.get("log_path", "logs/vm-container-bucket.log"))
        
        # Docker sozlamalari
        docker_config = self.config_manager.get_docker_config()
        self.docker_auto_connect_var.set(docker_config.get("auto_connect", True))
        self.docker_ports_var.set(docker_config.get("default_ports", "8080:80"))
        
        # VirtualBox sozlamalari
        vbox_config = self.config_manager.get_virtualbox_config()
        self.vbox_auto_connect_var.set(vbox_config.get("auto_connect", True))
        self.vbox_memory_var.set(str(vbox_config.get("default_memory", 1024)))
        self.vbox_cpus_var.set(str(vbox_config.get("default_cpus", 1)))
        
        # Hyper-V sozlamalari
        hyperv_config = self.config_manager.get_hyperv_config()
        self.hyperv_auto_connect_var.set(hyperv_config.get("auto_connect", True))
        self.hyperv_memory_var.set(str(hyperv_config.get("default_memory", 1024)))
        self.hyperv_cpus_var.set(str(hyperv_config.get("default_cpus", 1)))
        
    def save_settings(self):
        """Sozlamalarni saqlash"""
        try:
            # Umumiy sozlamalar
            self.config_manager.set("language", self.language_var.get())
            self.config_manager.set("theme", self.theme_var.get())
            self.config_manager.set("auto_refresh", self.auto_refresh_var.get())
            self.config_manager.set("refresh_interval", int(self.refresh_interval_var.get()))
            self.config_manager.set("enable_logging", self.enable_logging_var.get())
            self.config_manager.set("log_path", self.log_path_var.get())
            
            # Docker sozlamalari
            self.config_manager.set("docker.auto_connect", self.docker_auto_connect_var.get())
            self.config_manager.set("docker.default_ports", self.docker_ports_var.get())
            
            # VirtualBox sozlamalari
            self.config_manager.set("virtualbox.auto_connect", self.vbox_auto_connect_var.get())
            self.config_manager.set("virtualbox.default_memory", int(self.vbox_memory_var.get()))
            self.config_manager.set("virtualbox.default_cpus", int(self.vbox_cpus_var.get()))
            
            # Hyper-V sozlamalari
            self.config_manager.set("hyperv.auto_connect", self.hyperv_auto_connect_var.get())
            self.config_manager.set("hyperv.default_memory", int(self.hyperv_memory_var.get()))
            self.config_manager.set("hyperv.default_cpus", int(self.hyperv_cpus_var.get()))
            
            messagebox.showinfo("Muvaffaqiyat", "Sozlamalar muvaffaqiyatli saqlandi")
            
        except ValueError as e:
            messagebox.showerror("Xatolik", f"Noto'g'ri qiymat: {str(e)}")
        except Exception as e:
            messagebox.showerror("Xatolik", f"Sozlamalarni saqlashda xatolik: {str(e)}")
            
    def reset_settings(self):
        """Sozlamalarni qayta tiklash"""
        result = messagebox.askyesno("Tasdiqlash", 
                                   "Barcha sozlamalarni default qiymatlarga qaytarishni xohlaysizmi?")
        if result:
            # Default sozlamalarni yuklash
            self.config_manager.config = {
                "theme": "light",
                "language": "uz",
                "auto_refresh": True,
                "refresh_interval": 30,
                "docker": {
                    "auto_connect": True,
                    "default_ports": "8080:80"
                },
                "virtualbox": {
                    "auto_connect": True,
                    "default_memory": 1024,
                    "default_cpus": 1
                },
                "hyperv": {
                    "auto_connect": True,
                    "default_memory": 1024,
                    "default_cpus": 1
                }
            }
            self.config_manager.save_config()
            self.load_settings()
            messagebox.showinfo("Muvaffaqiyat", "Sozlamalar default qiymatlarga qaytarildi")
            
    def select_log_path(self):
        """Log fayl yo'lini tanlash"""
        from tkinter import filedialog
        log_path = filedialog.asksaveasfilename(
            title="Log fayl yo'lini tanlash",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="vm-container-bucket.log"
        )
        if log_path:
            self.log_path_var.set(log_path)
            
    def export_settings(self):
        """Sozlamalarni eksport qilish"""
        from tkinter import filedialog
        import json
        
        file_path = filedialog.asksaveasfilename(
            title="Sozlamalarni eksport qilish",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="vm-container-settings.json"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config_manager.config, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Muvaffaqiyat", f"Sozlamalar eksport qilindi: {file_path}")
            except Exception as e:
                messagebox.showerror("Xatolik", f"Eksport qilishda xatolik: {str(e)}")
                
    def import_settings(self):
        """Sozlamalarni import qilish"""
        from tkinter import filedialog
        import json
        
        file_path = filedialog.askopenfilename(
            title="Sozlamalarni import qilish",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_config = json.load(f)
                
                # Sozlamalarni yangilash
                self.config_manager.config.update(imported_config)
                self.config_manager.save_config()
                self.load_settings()
                
                messagebox.showinfo("Muvaffaqiyat", f"Sozlamalar import qilindi: {file_path}")
            except Exception as e:
                messagebox.showerror("Xatolik", f"Import qilishda xatolik: {str(e)}")
