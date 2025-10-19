#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asosiy oyna - Barcha VM va konteynerlarni boshqarish uchun GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import threading
from typing import Dict, List

class MainWindow:
    def __init__(self, root, docker_manager, vbox_manager, hyperv_manager, config_manager):
        self.root = root
        self.docker_manager = docker_manager
        self.vbox_manager = vbox_manager
        self.hyperv_manager = hyperv_manager
        self.config_manager = config_manager
        
        self.setup_ui()
        self.refresh_all()
        
    def setup_ui(self):
        """UI ni sozlash"""
        # Asosiy frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Root oynani sozlash
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Sarlavha
        title_label = ttk.Label(main_frame, text="VM-Container Bucket", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Chap panel - Navigation
        self.setup_navigation_panel(main_frame)
        
        # O'ng panel - Content
        self.setup_content_panel(main_frame)
        
        # Status bar
        self.setup_status_bar(main_frame)
        
    def setup_navigation_panel(self, parent):
        """Navigation panelini sozlash"""
        nav_frame = ttk.LabelFrame(parent, text="Boshqaruv", padding="10")
        nav_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Docker bo'limi
        docker_frame = ttk.LabelFrame(nav_frame, text="Docker", padding="5")
        docker_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(docker_frame, text="Konteynerlar", 
                  command=lambda: self.show_docker_containers()).pack(fill="x", pady=2)
        ttk.Button(docker_frame, text="Imagelar", 
                  command=lambda: self.show_docker_images()).pack(fill="x", pady=2)
        ttk.Button(docker_frame, text="Yangi Konteyner", 
                  command=self.create_docker_container).pack(fill="x", pady=2)
        
        # VirtualBox bo'limi
        vbox_frame = ttk.LabelFrame(nav_frame, text="VirtualBox", padding="5")
        vbox_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(vbox_frame, text="Virtual Mashinalar", 
                  command=lambda: self.show_vbox_vms()).pack(fill="x", pady=2)
        ttk.Button(vbox_frame, text="Yangi VM", 
                  command=self.create_vbox_vm).pack(fill="x", pady=2)
        
        # Hyper-V bo'limi
        hyperv_frame = ttk.LabelFrame(nav_frame, text="Hyper-V", padding="5")
        hyperv_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(hyperv_frame, text="Virtual Mashinalar", 
                  command=lambda: self.show_hyperv_vms()).pack(fill="x", pady=2)
        ttk.Button(hyperv_frame, text="Yangi VM", 
                  command=self.create_hyperv_vm).pack(fill="x", pady=2)
        
        # Umumiy tugmalar
        general_frame = ttk.LabelFrame(nav_frame, text="Umumiy", padding="5")
        general_frame.pack(fill="x")
        
        ttk.Button(general_frame, text="Yangilash", 
                  command=self.refresh_all).pack(fill="x", pady=2)
        ttk.Button(general_frame, text="ISO Boshqaruv", 
                  command=self.show_iso_manager).pack(fill="x", pady=2)
        ttk.Button(general_frame, text="Sozlamalar", 
                  command=self.show_settings).pack(fill="x", pady=2)
        
    def setup_content_panel(self, parent):
        """Content panelini sozlash"""
        content_frame = ttk.Frame(parent)
        content_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Notebook (tablar uchun)
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tablarni yaratish
        self.setup_tabs()
        
    def setup_tabs(self):
        """Tablar yaratish"""
        # Docker tab
        self.docker_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.docker_frame, text="Docker")
        
        # VirtualBox tab
        self.vbox_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.vbox_frame, text="VirtualBox")
        
        # Hyper-V tab
        self.hyperv_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.hyperv_frame, text="Hyper-V")
        
        # Umumiy tab
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="Umumiy Ko'rinish")
        
    def setup_status_bar(self, parent):
        """Status bar yaratish"""
        self.status_var = tk.StringVar()
        self.status_var.set("Tayyor")
        
        status_bar = ttk.Label(parent, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def refresh_all(self):
        """Barcha ma'lumotlarni yangilash"""
        self.status_var.set("Ma'lumotlar yangilanmoqda...")
        
        # Thread orqali yangilash
        def refresh_thread():
            try:
                self.show_docker_containers()
                self.show_vbox_vms()
                self.show_hyperv_vms()
                self.show_overview()
                self.status_var.set("Ma'lumotlar yangilandi")
            except Exception as e:
                self.status_var.set(f"Xatolik: {str(e)}")
                
        threading.Thread(target=refresh_thread, daemon=True).start()
        
    def show_docker_containers(self):
        """Docker konteynerlarini ko'rsatish"""
        # Eski widgetlarni tozalash
        for widget in self.docker_frame.winfo_children():
            widget.destroy()
            
        if not self.docker_manager.is_available():
            ttk.Label(self.docker_frame, text="Docker mavjud emas yoki ishlamayapti").pack(pady=20)
            return
            
        # Treeview yaratish
        columns = ("Name", "Image", "Status", "Created")
        tree = ttk.Treeview(self.docker_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
            
        # Scrollbar qo'shish
        scrollbar = ttk.Scrollbar(self.docker_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Ma'lumotlarni yuklash
        containers = self.docker_manager.get_containers()
        for container in containers:
            tree.insert("", "end", values=(
                container.get('name', ''),
                container.get('image', ''),
                container.get('status', ''),
                container.get('created', '')[:19] if container.get('created') else ''
            ))
            
    def show_docker_images(self):
        """Docker imagelarini ko'rsatish"""
        # Docker tabga o'tish
        self.notebook.select(self.docker_frame)
        
        # Eski widgetlarni tozalash
        for widget in self.docker_frame.winfo_children():
            widget.destroy()
            
        if not self.docker_manager.is_available():
            ttk.Label(self.docker_frame, text="Docker mavjud emas yoki ishlamayapti").pack(pady=20)
            return
            
        # Treeview yaratish
        columns = ("Tags", "Size", "Created")
        tree = ttk.Treeview(self.docker_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)
            
        # Scrollbar qo'shish
        scrollbar = ttk.Scrollbar(self.docker_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Ma'lumotlarni yuklash
        images = self.docker_manager.get_images()
        for image in images:
            tags = ', '.join(image.get('tags', [])) if image.get('tags') else 'None'
            size_mb = image.get('size', 0) // (1024 * 1024)
            tree.insert("", "end", values=(
                tags,
                f"{size_mb} MB",
                image.get('created', '')[:19] if image.get('created') else ''
            ))
            
    def show_vbox_vms(self):
        """VirtualBox VMlarini ko'rsatish"""
        # Eski widgetlarni tozalash
        for widget in self.vbox_frame.winfo_children():
            widget.destroy()
            
        if not self.vbox_manager.is_available():
            ttk.Label(self.vbox_frame, text="VirtualBox mavjud emas yoki ishlamayapti").pack(pady=20)
            return
            
        # Treeview yaratish
        columns = ("Name", "State", "Memory", "CPUs")
        tree = ttk.Treeview(self.vbox_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
            
        # Scrollbar qo'shish
        scrollbar = ttk.Scrollbar(self.vbox_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Ma'lumotlarni yuklash
        vms = self.vbox_manager.get_vms()
        for vm in vms:
            tree.insert("", "end", values=(
                vm.get('name', ''),
                vm.get('state', ''),
                vm.get('memory', ''),
                vm.get('cpus', '')
            ))
            
        # Context menu qo'shish
        self.setup_vm_context_menu(tree, "VirtualBox")
            
    def show_hyperv_vms(self):
        """Hyper-V VMlarini ko'rsatish"""
        # Eski widgetlarni tozalash
        for widget in self.hyperv_frame.winfo_children():
            widget.destroy()
            
        if not self.hyperv_manager.is_available():
            ttk.Label(self.hyperv_frame, text="Hyper-V mavjud emas yoki ishlamayapti").pack(pady=20)
            return
            
        # Treeview yaratish
        columns = ("Name", "State", "Memory", "CPUs")
        tree = ttk.Treeview(self.hyperv_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
            
        # Scrollbar qo'shish
        scrollbar = ttk.Scrollbar(self.hyperv_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Ma'lumotlarni yuklash
        vms = self.hyperv_manager.get_vms()
        for vm in vms:
            tree.insert("", "end", values=(
                vm.get('name', ''),
                vm.get('state', ''),
                vm.get('memory', ''),
                vm.get('cpus', '')
            ))
            
        # Context menu qo'shish
        self.setup_vm_context_menu(tree, "Hyper-V")
            
    def show_overview(self):
        """Umumiy ko'rinish"""
        # Eski widgetlarni tozalash
        for widget in self.overview_frame.winfo_children():
            widget.destroy()
            
        # Statistikalar
        stats_frame = ttk.LabelFrame(self.overview_frame, text="Statistika", padding="10")
        stats_frame.pack(fill="x", pady=(0, 10))
        
        # Docker statistikasi
        docker_containers = len(self.docker_manager.get_containers()) if self.docker_manager.is_available() else 0
        docker_images = len(self.docker_manager.get_images()) if self.docker_manager.is_available() else 0
        
        # VirtualBox statistikasi
        vbox_vms = len(self.vbox_manager.get_vms()) if self.vbox_manager.is_available() else 0
        
        # Hyper-V statistikasi
        hyperv_vms = len(self.hyperv_manager.get_vms()) if self.hyperv_manager.is_available() else 0
        
        # Statistikalar ko'rsatish
        ttk.Label(stats_frame, text=f"Docker Konteynerlar: {docker_containers}").pack(anchor="w")
        ttk.Label(stats_frame, text=f"Docker Imagelar: {docker_images}").pack(anchor="w")
        ttk.Label(stats_frame, text=f"VirtualBox VMlar: {vbox_vms}").pack(anchor="w")
        ttk.Label(stats_frame, text=f"Hyper-V VMlar: {hyperv_vms}").pack(anchor="w")
        
    def create_docker_container(self):
        """Yangi Docker konteyner yaratish"""
        dialog = ContainerCreateDialog(self.root, self.docker_manager)
        self.root.wait_window(dialog.dialog)
        self.show_docker_containers()
        
    def create_vbox_vm(self):
        """Yangi VirtualBox VM yaratish"""
        dialog = VMCreateDialog(self.root, self.vbox_manager, "VirtualBox")
        self.root.wait_window(dialog.dialog)
        self.show_vbox_vms()
        
    def create_hyperv_vm(self):
        """Yangi Hyper-V VM yaratish"""
        dialog = VMCreateDialog(self.root, self.hyperv_manager, "Hyper-V")
        self.root.wait_window(dialog.dialog)
        self.show_hyperv_vms()
        
    def show_iso_manager(self):
        """ISO boshqaruv oynasini ko'rsatish"""
        from ui.iso_manager_window import ISOManagerWindow
        ISOManagerWindow(self.root)
        
    def show_settings(self):
        """Sozlamalar oynasini ko'rsatish"""
        from ui.settings_window import SettingsWindow
        SettingsWindow(self.root, self.config_manager)
        
    def setup_vm_context_menu(self, tree, vm_type):
        """VM uchun context menu yaratish"""
        context_menu = tk.Menu(self.root, tearoff=0)
        
        context_menu.add_command(label="Ishga tushirish", 
                               command=lambda: self.vm_action(tree, "start", vm_type))
        context_menu.add_command(label="To'xtatish", 
                               command=lambda: self.vm_action(tree, "stop", vm_type))
        context_menu.add_command(label="Pauza", 
                               command=lambda: self.vm_action(tree, "pause", vm_type))
        context_menu.add_command(label="Davom ettirish", 
                               command=lambda: self.vm_action(tree, "resume", vm_type))
        context_menu.add_command(label="Qayta ishga tushirish", 
                               command=lambda: self.vm_action(tree, "reset", vm_type))
        context_menu.add_separator()
        context_menu.add_command(label="ISO ulash", 
                               command=lambda: self.attach_iso(tree, vm_type))
        context_menu.add_command(label="ISO olib tashlash", 
                               command=lambda: self.detach_iso(tree, vm_type))
        context_menu.add_separator()
        context_menu.add_command(label="Hard Disk Boshqaruvi", 
                               command=lambda: self.manage_hard_disks(tree, vm_type))
        
        def show_context_menu(event):
            try:
                item = tree.selection()[0]
                context_menu.post(event.x_root, event.y_root)
            except IndexError:
                pass
                
        tree.bind("<Button-3>", show_context_menu)  # Right click
        
    def vm_action(self, tree, action, vm_type):
        """VM boshqaruv amallarini bajarish"""
        try:
            selected_item = tree.selection()[0]
            vm_name = tree.item(selected_item)['values'][0]
            
            if vm_type == "VirtualBox":
                # UUID olish kerak VirtualBox uchun
                vms = self.vbox_manager.get_vms()
                vm_uuid = None
                for vm in vms:
                    if vm.get('name') == vm_name:
                        vm_uuid = vm.get('uuid')
                        break
                        
                if not vm_uuid:
                    messagebox.showerror("Xatolik", "VM UUID topilmadi")
                    return
                    
                success = False
                if action == "start":
                    success = self.vbox_manager.start_vm(vm_uuid)
                elif action == "stop":
                    success = self.vbox_manager.stop_vm(vm_uuid)
                elif action == "pause":
                    success = self.vbox_manager.pause_vm(vm_uuid)
                elif action == "resume":
                    success = self.vbox_manager.resume_vm(vm_uuid)
                elif action == "reset":
                    success = self.vbox_manager.reset_vm(vm_uuid)
                    
            elif vm_type == "Hyper-V":
                success = False
                if action == "start":
                    success = self.hyperv_manager.start_vm(vm_name)
                elif action == "stop":
                    success = self.hyperv_manager.stop_vm(vm_name)
                elif action == "pause":
                    success = self.hyperv_manager.pause_vm(vm_name)
                elif action == "resume":
                    success = self.hyperv_manager.resume_vm(vm_name)
                elif action == "reset":
                    success = self.hyperv_manager.reset_vm(vm_name)
                    
            if success:
                messagebox.showinfo("Muvaffaqiyat", f"VM {action} amali muvaffaqiyatli bajarildi")
                # Ma'lumotlarni yangilash
                if vm_type == "VirtualBox":
                    self.show_vbox_vms()
                elif vm_type == "Hyper-V":
                    self.show_hyperv_vms()
            else:
                messagebox.showerror("Xatolik", f"VM {action} amalida xatolik")
                
        except IndexError:
            messagebox.showwarning("Ogohlantirish", "VM tanlang")
        except Exception as e:
            messagebox.showerror("Xatolik", f"Amal bajarishda xatolik: {str(e)}")
            
    def attach_iso(self, tree, vm_type):
        """ISO fayl ulash"""
        try:
            selected_item = tree.selection()[0]
            vm_name = tree.item(selected_item)['values'][0]
            
            # ISO fayl tanlash
            iso_path = filedialog.askopenfilename(
                title="ISO fayl tanlash",
                filetypes=[("ISO files", "*.iso"), ("All files", "*.*")]
            )
            
            if not iso_path:
                return
                
            success = False
            if vm_type == "VirtualBox":
                vms = self.vbox_manager.get_vms()
                vm_uuid = None
                for vm in vms:
                    if vm.get('name') == vm_name:
                        vm_uuid = vm.get('uuid')
                        break
                        
                if vm_uuid:
                    success = self.vbox_manager.attach_iso(vm_uuid, iso_path)
                    
            elif vm_type == "Hyper-V":
                success = self.hyperv_manager.attach_iso(vm_name, iso_path)
                
            if success:
                messagebox.showinfo("Muvaffaqiyat", "ISO fayl muvaffaqiyatli ulandi")
            else:
                messagebox.showerror("Xatolik", "ISO fayl ulashda xatolik")
                
        except IndexError:
            messagebox.showwarning("Ogohlantirish", "VM tanlang")
        except Exception as e:
            messagebox.showerror("Xatolik", f"ISO ulashda xatolik: {str(e)}")
            
    def detach_iso(self, tree, vm_type):
        """ISO faylni olib tashlash"""
        try:
            selected_item = tree.selection()[0]
            vm_name = tree.item(selected_item)['values'][0]
            
            success = False
            if vm_type == "VirtualBox":
                vms = self.vbox_manager.get_vms()
                vm_uuid = None
                for vm in vms:
                    if vm.get('name') == vm_name:
                        vm_uuid = vm.get('uuid')
                        break
                        
                if vm_uuid:
                    success = self.vbox_manager.detach_iso(vm_uuid)
                    
            elif vm_type == "Hyper-V":
                success = self.hyperv_manager.detach_iso(vm_name)
                
            if success:
                messagebox.showinfo("Muvaffaqiyat", "ISO fayl muvaffaqiyatli olib tashlandi")
            else:
                messagebox.showerror("Xatolik", "ISO fayl olib tashlashda xatolik")
                
        except IndexError:
            messagebox.showwarning("Ogohlantirish", "VM tanlang")
        except Exception as e:
            messagebox.showerror("Xatolik", f"ISO olib tashlashda xatolik: {str(e)}")
            
    def manage_hard_disks(self, tree, vm_type):
        """Hard disk boshqaruv oynasini ochish"""
        try:
            selected_item = tree.selection()[0]
            vm_name = tree.item(selected_item)['values'][0]
            
            from ui.hard_disk_manager_window import HardDiskManagerWindow
            
            if vm_type == "VirtualBox":
                HardDiskManagerWindow(self.root, self.vbox_manager, vm_name, vm_type)
            elif vm_type == "Hyper-V":
                HardDiskManagerWindow(self.root, self.hyperv_manager, vm_name, vm_type)
            else:
                messagebox.showerror("Xatolik", "Hard disk boshqaruvi bu VM turi uchun qo'llab-quvvatlanmaydi")
                
        except IndexError:
            messagebox.showwarning("Ogohlantirish", "VM tanlang")
        except Exception as e:
            messagebox.showerror("Xatolik", f"Hard disk boshqaruv oynasini ochishda xatolik: {str(e)}")


class ContainerCreateDialog:
    def __init__(self, parent, docker_manager):
        self.docker_manager = docker_manager
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Yangi Docker Konteyner")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="10")
        frame.pack(fill="both", expand=True)
        
        # Image name
        ttk.Label(frame, text="Image nomi:").grid(row=0, column=0, sticky="w", pady=5)
        self.image_var = tk.StringVar(value="ubuntu:latest")
        ttk.Entry(frame, textvariable=self.image_var, width=30).grid(row=0, column=1, pady=5)
        
        # Container name
        ttk.Label(frame, text="Konteyner nomi:").grid(row=1, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=1, column=1, pady=5)
        
        # Ports
        ttk.Label(frame, text="Portlar (masalan: 8080:80):").grid(row=2, column=0, sticky="w", pady=5)
        self.ports_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.ports_var, width=30).grid(row=2, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Yaratish", command=self.create_container).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Bekor qilish", command=self.dialog.destroy).pack(side="left", padx=5)
        
    def create_container(self):
        image_name = self.image_var.get()
        container_name = self.name_var.get()
        ports_str = self.ports_var.get()
        
        if not image_name:
            messagebox.showerror("Xatolik", "Image nomi kiritilishi shart")
            return
            
        # Portlarni parse qilish
        ports = {}
        if ports_str:
            try:
                for port_mapping in ports_str.split(','):
                    host_port, container_port = port_mapping.strip().split(':')
                    ports[container_port] = int(host_port)
            except:
                messagebox.showerror("Xatolik", "Port format noto'g'ri. Masalan: 8080:80")
                return
                
        success = self.docker_manager.run_container(
            image_name, 
            name=container_name if container_name else None,
            ports=ports if ports else None
        )
        
        if success:
            messagebox.showinfo("Muvaffaqiyat", "Konteyner muvaffaqiyatli yaratildi")
            self.dialog.destroy()
        else:
            messagebox.showerror("Xatolik", "Konteyner yaratishda xatolik")


class VMCreateDialog:
    def __init__(self, parent, vm_manager, vm_type):
        self.vm_manager = vm_manager
        self.vm_type = vm_type
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Yangi {vm_type} VM")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="10")
        frame.pack(fill="both", expand=True)
        
        # VM name
        ttk.Label(frame, text="VM nomi:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=40).grid(row=0, column=1, pady=5)
        
        # Memory
        ttk.Label(frame, text="Xotira (MB):").grid(row=1, column=0, sticky="w", pady=5)
        self.memory_var = tk.StringVar(value="1024")
        ttk.Entry(frame, textvariable=self.memory_var, width=40).grid(row=1, column=1, pady=5)
        
        # CPUs
        ttk.Label(frame, text="CPU soni:").grid(row=2, column=0, sticky="w", pady=5)
        self.cpus_var = tk.StringVar(value="1")
        ttk.Entry(frame, textvariable=self.cpus_var, width=40).grid(row=2, column=1, pady=5)
        
        # OS Type (VirtualBox uchun)
        if self.vm_type == "VirtualBox":
            ttk.Label(frame, text="OS turi:").grid(row=3, column=0, sticky="w", pady=5)
            self.os_type_var = tk.StringVar(value="Ubuntu_64")
            os_combo = ttk.Combobox(frame, textvariable=self.os_type_var, width=37)
            os_combo['values'] = [
                "Ubuntu_64", "Windows10_64", "Windows11_64", "RedHat_64", 
                "Debian_64", "CentOS_64", "Fedora_64", "OpenSUSE_64"
            ]
            os_combo.grid(row=3, column=1, pady=5)
        
        # ISO fayl
        ttk.Label(frame, text="ISO fayl (ixtiyoriy):").grid(row=4, column=0, sticky="w", pady=5)
        iso_frame = ttk.Frame(frame)
        iso_frame.grid(row=4, column=1, sticky="ew", pady=5)
        
        self.iso_var = tk.StringVar()
        ttk.Entry(iso_frame, textvariable=self.iso_var, width=30).pack(side="left", padx=(0, 5))
        ttk.Button(iso_frame, text="Tanlash", command=self.select_iso).pack(side="left")
        
        # Hard disk (Barcha VM turlari uchun)
        ttk.Label(frame, text="Hard disk hajmi:").grid(row=5, column=0, sticky="w", pady=5)
        hdd_size_frame = ttk.Frame(frame)
        hdd_size_frame.grid(row=5, column=1, sticky="ew", pady=5)
        
        self.hdd_size_var = tk.StringVar(value="20")
        ttk.Entry(hdd_size_frame, textvariable=self.hdd_size_var, width=20).pack(side="left", padx=(0, 5))
        
        if self.vm_type == "VirtualBox":
            ttk.Label(hdd_size_frame, text="MB").pack(side="left")
        elif self.vm_type == "Hyper-V":
            ttk.Label(hdd_size_frame, text="GB").pack(side="left")
        
        ttk.Label(frame, text="Hard disk saqlash joyi:").grid(row=6, column=0, sticky="w", pady=5)
        hdd_frame = ttk.Frame(frame)
        hdd_frame.grid(row=6, column=1, sticky="ew", pady=5)
        
        self.hdd_path_var = tk.StringVar()
        ttk.Entry(hdd_frame, textvariable=self.hdd_path_var, width=30).pack(side="left", padx=(0, 5))
        ttk.Button(hdd_frame, text="Tanlash", command=self.select_hdd_path).pack(side="left")
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Yaratish", command=self.create_vm).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Bekor qilish", command=self.dialog.destroy).pack(side="left", padx=5)
        
    def select_iso(self):
        """ISO fayl tanlash"""
        iso_path = filedialog.askopenfilename(
            title="ISO fayl tanlash",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")]
        )
        if iso_path:
            self.iso_var.set(iso_path)
            
    def select_hdd_path(self):
        """Hard disk saqlash joyini tanlash"""
        if self.vm_type == "VirtualBox":
            file_types = [("VDI files", "*.vdi"), ("VMDK files", "*.vmdk"), ("All files", "*.*")]
            default_ext = ".vdi"
        elif self.vm_type == "Hyper-V":
            file_types = [("VHDX files", "*.vhdx"), ("VHD files", "*.vhd"), ("All files", "*.*")]
            default_ext = ".vhdx"
        else:
            file_types = [("All files", "*.*")]
            default_ext = ".vdi"
            
        hdd_path = filedialog.asksaveasfilename(
            title="Hard disk saqlash joyini tanlash",
            defaultextension=default_ext,
            filetypes=file_types,
            initialfile=f"{self.name_var.get()}{default_ext}"
        )
        if hdd_path:
            self.hdd_path_var.set(hdd_path)
        
    def create_vm(self):
        name = self.name_var.get()
        memory = self.memory_var.get()
        cpus = self.cpus_var.get()
        iso_path = self.iso_var.get() if self.iso_var.get() else None
        
        if not name:
            messagebox.showerror("Xatolik", "VM nomi kiritilishi shart")
            return
            
        try:
            memory = int(memory)
            cpus = int(cpus)
        except ValueError:
            messagebox.showerror("Xatolik", "Memory va CPU soni raqam bo'lishi kerak")
            return
            
        # VM yaratish
        if self.vm_type == "VirtualBox":
            os_type = self.os_type_var.get()
            hdd_path = self.hdd_path_var.get() if hasattr(self, 'hdd_path_var') and self.hdd_path_var.get() else None
            hdd_size = int(self.hdd_size_var.get()) if hasattr(self, 'hdd_size_var') and self.hdd_size_var.get() else 20480  # MB
            success = self.vm_manager.create_vm(name, memory, cpus, os_type, iso_path, hdd_path, hdd_size)
        elif self.vm_type == "Hyper-V":
            hdd_path = self.hdd_path_var.get() if hasattr(self, 'hdd_path_var') and self.hdd_path_var.get() else None
            hdd_size = int(self.hdd_size_var.get()) if hasattr(self, 'hdd_size_var') and self.hdd_size_var.get() else 20  # GB
            success = self.vm_manager.create_vm(name, memory, cpus, hdd_path, iso_path, hdd_size)
        else:
            success = self.vm_manager.create_vm(name, memory, cpus)
        
        if success:
            messagebox.showinfo("Muvaffaqiyat", f"{self.vm_type} VM muvaffaqiyatli yaratildi")
            self.dialog.destroy()
        else:
            messagebox.showerror("Xatolik", f"{self.vm_type} VM yaratishda xatolik")
