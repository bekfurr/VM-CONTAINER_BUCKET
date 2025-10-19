#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VM-Container Bucket - Virtual Mashina va Konteyner Boshqaruv Dasturi
Barcha VM va konteyner turlarini bitta interfeysda boshqarish
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import sys
from datetime import datetime

# O'z modullarimizni import qilamiz
from managers.docker_manager import DockerManager
from managers.virtualbox_manager import VirtualBoxManager
from managers.hyperv_manager import HyperVManager
from ui.main_window import MainWindow
from utils.config_manager import ConfigManager

class VMContainerBucket:
    def __init__(self):
        self.root = tk.Tk()
        self.config_manager = ConfigManager()
        self.docker_manager = DockerManager()
        self.vbox_manager = VirtualBoxManager()
        self.hyperv_manager = HyperVManager()
        
        # Asosiy oynani sozlash
        self.setup_main_window()
        
    def setup_main_window(self):
        """Asosiy oynani sozlash"""
        self.root.title("VM-Container Bucket")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Icon qo'shish (agar mavjud bo'lsa)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
            
        # Stil sozlash
        style = ttk.Style()
        style.theme_use('clam')
        
    def run(self):
        """Dasturni ishga tushirish"""
        try:
            # Barcha managerlarni tekshirish
            self.check_managers()
            
            # Asosiy oynani ko'rsatish
            main_window = MainWindow(
                self.root, 
                self.docker_manager,
                self.vbox_manager, 
                self.hyperv_manager,
                self.config_manager
            )
            
            self.root.mainloop()
            
        except Exception as e:
            messagebox.showerror("Xatolik", f"Dastur ishga tushirishda xatolik: {str(e)}")
            
    def check_managers(self):
        """Barcha managerlarning ishlashini tekshirish"""
        managers = [
            ("Docker", self.docker_manager),
            ("VirtualBox", self.vbox_manager),
            ("Hyper-V", self.hyperv_manager)
        ]
        
        for name, manager in managers:
            try:
                if not manager.is_available():
                    print(f"Ogohlantirish: {name} mavjud emas yoki sozlanmagan")
            except Exception as e:
                print(f"Xatolik: {name} tekshirishda xatolik - {str(e)}")

def main():
    """Asosiy funksiya"""
    print("VM-Container Bucket ishga tushmoqda...")
    
    # Kerakli papkalarni yaratish
    os.makedirs("configs", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    
    # Dasturni ishga tushirish
    app = VMContainerBucket()
    app.run()

if __name__ == "__main__":
    main()
