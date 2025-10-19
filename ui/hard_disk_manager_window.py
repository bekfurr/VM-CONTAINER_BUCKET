#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hard Disk Manager Window - VM hard disk boshqaruvi
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import os
from typing import Dict, List

class HardDiskManagerWindow:
    def __init__(self, parent, vm_manager, vm_name, vm_type):
        self.parent = parent
        self.vm_manager = vm_manager
        self.vm_name = vm_name
        self.vm_type = vm_type
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Hard Disk Boshqaruvi - {vm_name}")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.load_hard_disks()
        
    def setup_ui(self):
        """UI ni sozlash"""
        # Asosiy frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Sarlavha
        title_label = ttk.Label(main_frame, text=f"Hard Disk Boshqaruvi - {self.vm_name}", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Hard disk ro'yxati
        self.setup_hard_disk_list(main_frame)
        
        # Tugmalar
        self.setup_buttons(main_frame)
        
    def setup_hard_disk_list(self, parent):
        """Hard disk ro'yxatini sozlash"""
        list_frame = ttk.LabelFrame(parent, text="Hard Disklar", padding="10")
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Treeview
        columns = ("Controller", "Port", "Device", "Path", "Size", "Format")
        self.hard_disk_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            self.hard_disk_tree.heading(col, text=col)
            self.hard_disk_tree.column(col, width=120)
            
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", 
                                command=self.hard_disk_tree.yview)
        self.hard_disk_tree.configure(yscrollcommand=scrollbar.set)
        
        self.hard_disk_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Context menu
        self.setup_context_menu()
        
    def setup_buttons(self, parent):
        """Tugmalarni sozlash"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="Yangi Hard Disk", 
                  command=self.add_hard_disk).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Hajmini o'zgartirish", 
                  command=self.resize_hard_disk).pack(side="left", padx=5)
        ttk.Button(button_frame, text="O'chirish", 
                  command=self.remove_hard_disk).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Yangilash", 
                  command=self.load_hard_disks).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Yopish", 
                  command=self.dialog.destroy).pack(side="right", padx=5)
        
    def setup_context_menu(self):
        """Context menu sozlash"""
        self.context_menu = tk.Menu(self.dialog, tearoff=0)
        self.context_menu.add_command(label="Hajmini o'zgartirish", 
                                     command=self.resize_hard_disk)
        self.context_menu.add_command(label="O'chirish", 
                                     command=self.remove_hard_disk)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Fayl joyini ochish", 
                                     command=self.open_disk_location)
        
        def show_context_menu(event):
            try:
                item = self.hard_disk_tree.selection()[0]
                self.context_menu.post(event.x_root, event.y_root)
            except IndexError:
                pass
                
        self.hard_disk_tree.bind("<Button-3>", show_context_menu)
        
    def load_hard_disks(self):
        """Hard disk ma'lumotlarini yuklash"""
        # Eski ma'lumotlarni tozalash
        for widget in self.hard_disk_tree.get_children():
            self.hard_disk_tree.delete(widget)
            
        try:
            if self.vm_type == "VirtualBox":
                # UUID olish kerak
                vms = self.vm_manager.get_vms()
                vm_uuid = None
                for vm in vms:
                    if vm.get('name') == self.vm_name:
                        vm_uuid = vm.get('uuid')
                        break
                        
                if vm_uuid:
                    hard_disks = self.vm_manager.get_vm_hard_disks(vm_uuid)
                else:
                    hard_disks = []
                    
            elif self.vm_type == "Hyper-V":
                hard_disks = self.vm_manager.get_vm_hard_disks(self.vm_name)
            else:
                hard_disks = []
                
            # Ma'lumotlarni ko'rsatish
            for disk in hard_disks:
                self.hard_disk_tree.insert("", "end", values=(
                    disk.get('controller', ''),
                    disk.get('port', ''),
                    disk.get('device', ''),
                    disk.get('path', ''),
                    disk.get('size', ''),
                    disk.get('format', '')
                ))
                
        except Exception as e:
            messagebox.showerror("Xatolik", f"Hard disk ma'lumotlarini yuklashda xatolik: {str(e)}")
            
    def add_hard_disk(self):
        """Yangi hard disk qo'shish"""
        dialog = AddHardDiskDialog(self.dialog, self.vm_manager, self.vm_name, self.vm_type)
        self.dialog.wait_window(dialog.dialog)
        self.load_hard_disks()
        
    def resize_hard_disk(self):
        """Hard disk hajmini o'zgartirish"""
        try:
            selected_item = self.hard_disk_tree.selection()[0]
            disk_data = self.hard_disk_tree.item(selected_item)['values']
            
            disk_path = disk_data[3]  # Path
            current_size = disk_data[4]  # Size
            
            # Yangi hajmni so'rash
            new_size = simpledialog.askstring(
                "Hajmni o'zgartirish",
                f"Joriy hajm: {current_size}\nYangi hajm (MB):",
                initialvalue="40960"
            )
            
            if not new_size:
                return
                
            try:
                new_size_int = int(new_size)
            except ValueError:
                messagebox.showerror("Xatolik", "Hajm raqam bo'lishi kerak")
                return
                
            # Hajmni o'zgartirish
            if self.vm_type == "VirtualBox":
                success = self.vm_manager.resize_hard_disk(disk_path, new_size_int)
            elif self.vm_type == "Hyper-V":
                success = self.vm_manager.resize_hard_disk(disk_path, new_size_int // 1024)  # GB ga o'tkazish
            else:
                success = False
                
            if success:
                messagebox.showinfo("Muvaffaqiyat", "Hard disk hajmi muvaffaqiyatli o'zgartirildi")
                self.load_hard_disks()
            else:
                messagebox.showerror("Xatolik", "Hard disk hajmini o'zgartirishda xatolik")
                
        except IndexError:
            messagebox.showwarning("Ogohlantirish", "Hard disk tanlang")
        except Exception as e:
            messagebox.showerror("Xatolik", f"Hajmni o'zgartirishda xatolik: {str(e)}")
            
    def remove_hard_disk(self):
        """Hard diskni olib tashlash"""
        try:
            selected_item = self.hard_disk_tree.selection()[0]
            disk_data = self.hard_disk_tree.item(selected_item)['values']
            
            # Tasdiqlash
            result = messagebox.askyesno(
                "Tasdiqlash",
                f"Hard diskni olib tashlashni xohlaysizmi?\n\nPath: {disk_data[3]}"
            )
            
            if not result:
                return
                
            success = False
            if self.vm_type == "VirtualBox":
                success = self.vm_manager.remove_hard_disk(
                    disk_data[1], disk_data[2]  # port, device
                )
            elif self.vm_type == "Hyper-V":
                success = self.vm_manager.remove_hard_disk(
                    self.vm_name, int(disk_data[2]), int(disk_data[1])  # vm_name, controller, location
                )
                
            if success:
                messagebox.showinfo("Muvaffaqiyat", "Hard disk muvaffaqiyatli olib tashlandi")
                self.load_hard_disks()
            else:
                messagebox.showerror("Xatolik", "Hard diskni olib tashlashda xatolik")
                
        except IndexError:
            messagebox.showwarning("Ogohlantirish", "Hard disk tanlang")
        except Exception as e:
            messagebox.showerror("Xatolik", f"Hard diskni olib tashlashda xatolik: {str(e)}")
            
    def open_disk_location(self):
        """Disk fayl joyini ochish"""
        try:
            selected_item = self.hard_disk_tree.selection()[0]
            disk_path = self.hard_disk_tree.item(selected_item)['values'][3]
            
            if os.path.exists(disk_path):
                os.startfile(os.path.dirname(disk_path))
            else:
                messagebox.showerror("Xatolik", "Disk fayl topilmadi")
                
        except IndexError:
            messagebox.showwarning("Ogohlantirish", "Hard disk tanlang")
        except Exception as e:
            messagebox.showerror("Xatolik", f"Papka ochishda xatolik: {str(e)}")


class AddHardDiskDialog:
    def __init__(self, parent, vm_manager, vm_name, vm_type):
        self.vm_manager = vm_manager
        self.vm_name = vm_name
        self.vm_type = vm_type
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Yangi Hard Disk")
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI ni sozlash"""
        frame = ttk.Frame(self.dialog, padding="10")
        frame.pack(fill="both", expand=True)
        
        # Disk yo'li
        ttk.Label(frame, text="Disk yo'li:").grid(row=0, column=0, sticky="w", pady=5)
        path_frame = ttk.Frame(frame)
        path_frame.grid(row=0, column=1, sticky="ew", pady=5)
        
        self.path_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.path_var, width=40).pack(side="left", padx=(0, 5))
        ttk.Button(path_frame, text="Tanlash", command=self.select_path).pack(side="left")
        
        # Disk hajmi
        ttk.Label(frame, text="Disk hajmi:").grid(row=1, column=0, sticky="w", pady=5)
        size_frame = ttk.Frame(frame)
        size_frame.grid(row=1, column=1, sticky="ew", pady=5)
        
        self.size_var = tk.StringVar(value="20")
        ttk.Entry(size_frame, textvariable=self.size_var, width=20).pack(side="left", padx=(0, 5))
        
        if self.vm_type == "VirtualBox":
            ttk.Label(size_frame, text="MB").pack(side="left")
        elif self.vm_type == "Hyper-V":
            ttk.Label(size_frame, text="GB").pack(side="left")
        
        # Tugmalar
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Yaratish", command=self.create_disk).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Bekor qilish", command=self.dialog.destroy).pack(side="left", padx=5)
        
    def select_path(self):
        """Disk yo'lini tanlash"""
        if self.vm_type == "VirtualBox":
            file_types = [("VDI files", "*.vdi"), ("VMDK files", "*.vmdk"), ("All files", "*.*")]
        elif self.vm_type == "Hyper-V":
            file_types = [("VHD files", "*.vhd"), ("VHDX files", "*.vhdx"), ("All files", "*.*")]
        else:
            file_types = [("All files", "*.*")]
            
        disk_path = filedialog.asksaveasfilename(
            title="Disk fayl joyini tanlash",
            defaultextension=".vdi" if self.vm_type == "VirtualBox" else ".vhdx",
            filetypes=file_types
        )
        
        if disk_path:
            self.path_var.set(disk_path)
            
    def create_disk(self):
        """Disk yaratish"""
        disk_path = self.path_var.get()
        size_str = self.size_var.get()
        
        if not disk_path:
            messagebox.showerror("Xatolik", "Disk yo'li kiritilishi shart")
            return
            
        try:
            size = int(size_str)
        except ValueError:
            messagebox.showerror("Xatolik", "Hajm raqam bo'lishi kerak")
            return
            
        try:
            if self.vm_type == "VirtualBox":
                # UUID olish kerak
                vms = self.vm_manager.get_vms()
                vm_uuid = None
                for vm in vms:
                    if vm.get('name') == self.vm_name:
                        vm_uuid = vm.get('uuid')
                        break
                        
                if vm_uuid:
                    success = self.vm_manager.add_hard_disk(vm_uuid, disk_path, size)
                else:
                    success = False
                    
            elif self.vm_type == "Hyper-V":
                success = self.vm_manager.add_hard_disk(self.vm_name, disk_path, size)
            else:
                success = False
                
            if success:
                messagebox.showinfo("Muvaffaqiyat", "Hard disk muvaffaqiyatli yaratildi")
                self.dialog.destroy()
            else:
                messagebox.showerror("Xatolik", "Hard disk yaratishda xatolik")
                
        except Exception as e:
            messagebox.showerror("Xatolik", f"Hard disk yaratishda xatolik: {str(e)}")
