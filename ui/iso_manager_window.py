#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISO Manager Window - ISO fayllarini boshqarish oynasi
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from utils.iso_manager import ISOManager

class ISOManagerWindow:
    def __init__(self, parent):
        self.parent = parent
        self.iso_manager = ISOManager()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("ISO Boshqaruv")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.load_isos()
        
    def setup_ui(self):
        """UI ni sozlash"""
        # Asosiy frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Sarlavha
        title_label = ttk.Label(main_frame, text="ISO Fayllar Boshqaruvi", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Tab notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Mashhur ISO'lar tab
        self.setup_popular_tab()
        
        # Mahalliy ISO'lar tab
        self.setup_local_tab()
        
        # Yuklab olish tab
        self.setup_download_tab()
        
        # Tugmalar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="Yangi ISO qo'shish", 
                  command=self.add_local_iso).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Papkadan skan qilish", 
                  command=self.scan_directory).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Yopish", 
                  command=self.dialog.destroy).pack(side="right", padx=5)
        
    def setup_popular_tab(self):
        """Mashhur ISO'lar tabini sozlash"""
        self.popular_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.popular_frame, text="Mashhur ISO'lar")
        
        # Treeview
        columns = ("Name", "Description", "Size", "OS Type")
        self.popular_tree = ttk.Treeview(self.popular_frame, columns=columns, show="headings")
        
        for col in columns:
            self.popular_tree.heading(col, text=col)
            self.popular_tree.column(col, width=150)
            
        # Scrollbar
        popular_scrollbar = ttk.Scrollbar(self.popular_frame, orient="vertical", 
                                        command=self.popular_tree.yview)
        self.popular_tree.configure(yscrollcommand=popular_scrollbar.set)
        
        self.popular_tree.pack(side="left", fill="both", expand=True)
        popular_scrollbar.pack(side="right", fill="y")
        
        # Context menu
        self.setup_popular_context_menu()
        
    def setup_local_tab(self):
        """Mahalliy ISO'lar tabini sozlash"""
        self.local_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.local_frame, text="Mahalliy ISO'lar")
        
        # Treeview
        columns = ("Name", "Path", "Size", "Status")
        self.local_tree = ttk.Treeview(self.local_frame, columns=columns, show="headings")
        
        for col in columns:
            self.local_tree.heading(col, text=col)
            self.local_tree.column(col, width=150)
            
        # Scrollbar
        local_scrollbar = ttk.Scrollbar(self.local_frame, orient="vertical", 
                                      command=self.local_tree.yview)
        self.local_tree.configure(yscrollcommand=local_scrollbar.set)
        
        self.local_tree.pack(side="left", fill="both", expand=True)
        local_scrollbar.pack(side="right", fill="y")
        
        # Context menu
        self.setup_local_context_menu()
        
    def setup_download_tab(self):
        """Yuklab olish tabini sozlash"""
        self.download_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.download_frame, text="Yuklab olish")
        
        # Yuklab olish sozlamalari
        settings_frame = ttk.LabelFrame(self.download_frame, text="Yuklab olish sozlamalari", padding="10")
        settings_frame.pack(fill="x", pady=(0, 10))
        
        # Saqlash joyi
        ttk.Label(settings_frame, text="Saqlash joyi:").grid(row=0, column=0, sticky="w", pady=5)
        self.save_path_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        path_frame = ttk.Frame(settings_frame)
        path_frame.grid(row=0, column=1, sticky="ew", pady=5)
        
        ttk.Entry(path_frame, textvariable=self.save_path_var, width=50).pack(side="left", padx=(0, 5))
        ttk.Button(path_frame, text="Tanlash", command=self.select_save_path).pack(side="left")
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.download_frame, variable=self.progress_var, 
                                          maximum=100)
        self.progress_bar.pack(fill="x", pady=10)
        
        # Status
        self.status_var = tk.StringVar(value="Tayyor")
        ttk.Label(self.download_frame, textvariable=self.status_var).pack(pady=5)
        
    def setup_popular_context_menu(self):
        """Mashhur ISO'lar uchun context menu"""
        self.popular_context_menu = tk.Menu(self.dialog, tearoff=0)
        self.popular_context_menu.add_command(label="Yuklab olish", 
                                             command=self.download_selected_iso)
        
        def show_context_menu(event):
            try:
                item = self.popular_tree.selection()[0]
                self.popular_context_menu.post(event.x_root, event.y_root)
            except IndexError:
                pass
                
        self.popular_tree.bind("<Button-3>", show_context_menu)
        
    def setup_local_context_menu(self):
        """Mahalliy ISO'lar uchun context menu"""
        self.local_context_menu = tk.Menu(self.dialog, tearoff=0)
        self.local_context_menu.add_command(label="O'chirish", 
                                           command=self.remove_local_iso)
        self.local_context_menu.add_command(label="Fayl joyini ochish", 
                                           command=self.open_iso_location)
        
        def show_context_menu(event):
            try:
                item = self.local_tree.selection()[0]
                self.local_context_menu.post(event.x_root, event.y_root)
            except IndexError:
                pass
                
        self.local_tree.bind("<Button-3>", show_context_menu)
        
    def load_isos(self):
        """ISO'larni yuklash"""
        # Mashhur ISO'lar
        for widget in self.popular_tree.get_children():
            self.popular_tree.delete(widget)
            
        popular_isos = self.iso_manager.get_popular_isos()
        for iso in popular_isos:
            self.popular_tree.insert("", "end", values=(
                iso.get("name", ""),
                iso.get("description", ""),
                iso.get("size", ""),
                iso.get("os_type", "")
            ))
            
        # Mahalliy ISO'lar
        for widget in self.local_tree.get_children():
            self.local_tree.delete(widget)
            
        local_isos = self.iso_manager.get_local_isos()
        for iso in local_isos:
            path = iso.get("path", "")
            if path and os.path.exists(path):
                iso_info = self.iso_manager.get_iso_info(path)
                status = "Mavjud"
            else:
                iso_info = {"size": "N/A"}
                status = "Topilmadi"
                
            self.local_tree.insert("", "end", values=(
                iso.get("name", ""),
                path,
                iso_info.get("size", "N/A"),
                status
            ))
            
    def add_local_iso(self):
        """Mahalliy ISO qo'shish"""
        iso_path = filedialog.askopenfilename(
            title="ISO fayl tanlash",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")]
        )
        
        if not iso_path:
            return
            
        name = os.path.basename(iso_path)
        description = f"Mahalliy ISO: {name}"
        
        self.iso_manager.add_local_iso(name, iso_path, description)
        self.load_isos()
        messagebox.showinfo("Muvaffaqiyat", "ISO fayl qo'shildi")
        
    def remove_local_iso(self):
        """Mahalliy ISO'ni olib tashlash"""
        try:
            selected_item = self.local_tree.selection()[0]
            iso_name = self.local_tree.item(selected_item)['values'][0]
            
            self.iso_manager.remove_local_iso(iso_name)
            self.load_isos()
            messagebox.showinfo("Muvaffaqiyat", "ISO fayl olib tashlandi")
            
        except IndexError:
            messagebox.showwarning("Ogohlantirish", "ISO tanlang")
            
    def open_iso_location(self):
        """ISO fayl joyini ochish"""
        try:
            selected_item = self.local_tree.selection()[0]
            iso_path = self.local_tree.item(selected_item)['values'][1]
            
            if os.path.exists(iso_path):
                os.startfile(os.path.dirname(iso_path))
            else:
                messagebox.showerror("Xatolik", "ISO fayl topilmadi")
                
        except IndexError:
            messagebox.showwarning("Ogohlantirish", "ISO tanlang")
        except Exception as e:
            messagebox.showerror("Xatolik", f"Papka ochishda xatolik: {str(e)}")
            
    def scan_directory(self):
        """Papkadan ISO'larni skan qilish"""
        directory = filedialog.askdirectory(title="ISO fayllar papkasini tanlash")
        
        if not directory:
            return
            
        def scan_thread():
            self.status_var.set("Skan qilinmoqda...")
            iso_files = self.iso_manager.scan_local_isos(directory)
            
            for iso_info in iso_files:
                name = iso_info.get("name", "")
                path = iso_info.get("path", "")
                description = f"Skan qilingan: {name}"
                
                self.iso_manager.add_local_iso(name, path, description)
                
            self.dialog.after(0, lambda: self.load_isos())
            self.dialog.after(0, lambda: self.status_var.set("Skan tugadi"))
            
        threading.Thread(target=scan_thread, daemon=True).start()
        
    def download_selected_iso(self):
        """Tanlangan ISO'ni yuklab olish"""
        try:
            selected_item = self.popular_tree.selection()[0]
            iso_data = self.popular_tree.item(selected_item)['values']
            
            iso_name = iso_data[0]
            download_url = None
            
            # URL ni topish
            popular_isos = self.iso_manager.get_popular_isos()
            for iso in popular_isos:
                if iso.get("name") == iso_name:
                    download_url = iso.get("download_url")
                    break
                    
            if not download_url:
                messagebox.showerror("Xatolik", "Yuklab olish URL topilmadi")
                return
                
            # Saqlash joyini tanlash
            save_path = filedialog.asksaveasfilename(
                title="ISO faylni saqlash",
                defaultextension=".iso",
                filetypes=[("ISO files", "*.iso"), ("All files", "*.*")],
                initialvalue=iso_name.replace(" ", "_") + ".iso"
            )
            
            if not save_path:
                return
                
            # Yuklab olish
            def download_thread():
                self.status_var.set("Yuklab olinmoqda...")
                
                def progress_callback(progress):
                    self.dialog.after(0, lambda: self.progress_var.set(progress))
                    
                success = self.iso_manager.download_iso(download_url, save_path, progress_callback)
                
                if success:
                    self.dialog.after(0, lambda: self.status_var.set("Yuklab olish tugadi"))
                    self.dialog.after(0, lambda: messagebox.showinfo("Muvaffaqiyat", "ISO muvaffaqiyatli yuklab olindi"))
                    self.dialog.after(0, lambda: self.load_isos())
                else:
                    self.dialog.after(0, lambda: self.status_var.set("Yuklab olishda xatolik"))
                    self.dialog.after(0, lambda: messagebox.showerror("Xatolik", "Yuklab olishda xatolik"))
                    
            threading.Thread(target=download_thread, daemon=True).start()
            
        except IndexError:
            messagebox.showwarning("Ogohlantirish", "ISO tanlang")
            
    def select_save_path(self):
        """Saqlash joyini tanlash"""
        directory = filedialog.askdirectory(title="Saqlash papkasini tanlash")
        if directory:
            self.save_path_var.set(directory)
