#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VirtualBox Manager - VirtualBox virtual mashinalarini boshqarish
"""

import subprocess
import json
import os
import re
from typing import List, Dict, Optional

class VirtualBoxManager:
    def __init__(self):
        self.vboxmanage_path = self.find_vboxmanage()
        self.is_available_flag = self.check_availability()
        
    def find_vboxmanage(self) -> str:
        """VBoxManage yo'lini topish"""
        possible_paths = [
            "VBoxManage",
            r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe",
            r"C:\Program Files (x86)\Oracle\VirtualBox\VBoxManage.exe",
            "/usr/bin/VBoxManage",
            "/usr/local/bin/VBoxManage"
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return path
            except:
                continue
                
        return None
        
    def check_availability(self) -> bool:
        """VirtualBox mavjudligini tekshirish"""
        if not self.vboxmanage_path:
            return False
            
        try:
            result = subprocess.run([self.vboxmanage_path, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
            
    def is_available(self) -> bool:
        """VirtualBox mavjudligini tekshirish"""
        return self.is_available_flag
        
    def get_vms(self) -> List[Dict]:
        """Barcha virtual mashinalarni olish"""
        if not self.is_available():
            return []
            
        try:
            result = subprocess.run([self.vboxmanage_path, "list", "vms"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return []
                
            vms = []
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if line.strip():
                    # "VM Name" {uuid} formatini parse qilish
                    match = re.match(r'^"([^"]+)"\s+{([^}]+)}$', line.strip())
                    if match:
                        name, uuid = match.groups()
                        vm_info = self.get_vm_info(uuid)
                        vms.append({
                            'name': name,
                            'uuid': uuid,
                            'state': vm_info.get('state', 'Unknown'),
                            'memory': vm_info.get('memory', 'Unknown'),
                            'cpus': vm_info.get('cpus', 'Unknown')
                        })
                        
            return vms
            
        except Exception as e:
            print(f"VMlarni olishda xatolik: {str(e)}")
            return []
            
    def get_vm_info(self, uuid: str) -> Dict:
        """VM haqida batafsil ma'lumot olish"""
        if not self.is_available():
            return {}
            
        try:
            result = subprocess.run([self.vboxmanage_path, "showvminfo", uuid, "--machinereadable"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return {}
                
            info = {}
            for line in result.stdout.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"')
                    
                    if key == 'VMState':
                        info['state'] = value
                    elif key == 'memory':
                        info['memory'] = f"{value} MB"
                    elif key == 'cpus':
                        info['cpus'] = value
                        
            return info
            
        except Exception as e:
            print(f"VM ma'lumotlarini olishda xatolik: {str(e)}")
            return {}
            
    def start_vm(self, uuid: str) -> bool:
        """VMni ishga tushirish"""
        if not self.is_available():
            return False
            
        try:
            result = subprocess.run([self.vboxmanage_path, "startvm", uuid], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
            
        except Exception as e:
            print(f"VM ishga tushirishda xatolik: {str(e)}")
            return False
            
    def stop_vm(self, uuid: str) -> bool:
        """VMni to'xtatish"""
        if not self.is_available():
            return False
            
        try:
            result = subprocess.run([self.vboxmanage_path, "controlvm", uuid, "poweroff"], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
            
        except Exception as e:
            print(f"VM to'xtatishda xatolik: {str(e)}")
            return False
            
    def create_vm(self, name: str, memory: int = 1024, cpus: int = 1, 
                  os_type: str = "Ubuntu_64", iso_path: str = None, 
                  hard_disk_path: str = None, hard_disk_size_mb: int = 20480) -> bool:
        """Yangi VM yaratish"""
        if not self.is_available():
            return False
            
        try:
            # VM yaratish
            result = subprocess.run([self.vboxmanage_path, "createvm", 
                                   "--name", name, "--register"], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return False
                
            # UUID olish
            vm_info = subprocess.run([self.vboxmanage_path, "showvminfo", name, "--machinereadable"], 
                                   capture_output=True, text=True, timeout=10)
            
            uuid_match = re.search(r'UUID="([^"]+)"', vm_info.stdout)
            if not uuid_match:
                return False
                
            uuid = uuid_match.group(1)
            
            # Memory sozlash
            subprocess.run([self.vboxmanage_path, "modifyvm", uuid, "--memory", str(memory)], 
                         capture_output=True, text=True, timeout=10)
            
            # CPU sozlash
            subprocess.run([self.vboxmanage_path, "modifyvm", uuid, "--cpus", str(cpus)], 
                         capture_output=True, text=True, timeout=10)
            
            # OS type sozlash
            subprocess.run([self.vboxmanage_path, "modifyvm", uuid, "--ostype", os_type], 
                         capture_output=True, text=True, timeout=10)
            
            # SATA controller qo'shish
            subprocess.run([self.vboxmanage_path, "storagectl", uuid, "--name", "SATA Controller", 
                           "--add", "sata", "--controller", "IntelAHCI"], 
                         capture_output=True, text=True, timeout=10)
            
            # Hard disk yaratish va ulash
            if not hard_disk_path:
                hdd_path = os.path.join(os.path.expanduser("~"), "VirtualBox VMs", name, f"{name}.vdi")
            else:
                hdd_path = hard_disk_path
                
            subprocess.run([self.vboxmanage_path, "createhd", "--filename", hdd_path, 
                           "--size", str(hard_disk_size_mb)], capture_output=True, text=True, timeout=30)
            
            subprocess.run([self.vboxmanage_path, "storageattach", uuid, "--storagectl", "SATA Controller", 
                           "--port", "0", "--device", "0", "--type", "hdd", "--medium", hdd_path], 
                         capture_output=True, text=True, timeout=10)
            
            # ISO ulash (agar berilgan bo'lsa)
            if iso_path and os.path.exists(iso_path):
                self.attach_iso(uuid, iso_path)
            
            print(f"VM muvaffaqiyatli yaratildi: {name}")
            return True
            
        except Exception as e:
            print(f"VM yaratishda xatolik: {str(e)}")
            return False
            
    def attach_iso(self, uuid: str, iso_path: str) -> bool:
        """ISO fayl ulash"""
        if not self.is_available():
            return False
            
        try:
            # IDE controller qo'shish
            subprocess.run([self.vboxmanage_path, "storagectl", uuid, "--name", "IDE Controller", 
                           "--add", "ide"], capture_output=True, text=True, timeout=10)
            
            # ISO ulash
            result = subprocess.run([self.vboxmanage_path, "storageattach", uuid, 
                                   "--storagectl", "IDE Controller", "--port", "0", "--device", "0", 
                                   "--type", "dvddrive", "--medium", iso_path], 
                                  capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"ISO ulashda xatolik: {str(e)}")
            return False
            
    def detach_iso(self, uuid: str) -> bool:
        """ISO faylni olib tashlash"""
        if not self.is_available():
            return False
            
        try:
            result = subprocess.run([self.vboxmanage_path, "storageattach", uuid, 
                                   "--storagectl", "IDE Controller", "--port", "0", "--device", "0", 
                                   "--type", "dvddrive", "--medium", "none"], 
                                  capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"ISO olib tashlashda xatolik: {str(e)}")
            return False
            
    def pause_vm(self, uuid: str) -> bool:
        """VMni pauza qilish"""
        if not self.is_available():
            return False
            
        try:
            result = subprocess.run([self.vboxmanage_path, "controlvm", uuid, "pause"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            print(f"VM pauza qilishda xatolik: {str(e)}")
            return False
            
    def resume_vm(self, uuid: str) -> bool:
        """VMni davom ettirish"""
        if not self.is_available():
            return False
            
        try:
            result = subprocess.run([self.vboxmanage_path, "controlvm", uuid, "resume"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            print(f"VM davom ettirishda xatolik: {str(e)}")
            return False
            
    def reset_vm(self, uuid: str) -> bool:
        """VMni qayta ishga tushirish"""
        if not self.is_available():
            return False
            
        try:
            result = subprocess.run([self.vboxmanage_path, "controlvm", uuid, "reset"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            print(f"VM qayta ishga tushirishda xatolik: {str(e)}")
            return False
            
    def get_vm_hard_disks(self, uuid: str) -> List[Dict]:
        """VM hard disk ma'lumotlarini olish"""
        if not self.is_available():
            return []
            
        try:
            result = subprocess.run([self.vboxmanage_path, "showvminfo", uuid, "--machinereadable"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return []
                
            hard_disks = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'storagecontrollername' in line.lower():
                    controller_name = line.split('=')[1].strip().strip('"')
                elif 'storageattach' in line.lower():
                    parts = line.split('=')[1].strip().strip('"').split(',')
                    if len(parts) >= 4:
                        port = parts[0]
                        device = parts[1]
                        drive_type = parts[2]
                        medium_path = parts[3] if len(parts) > 3 else ""
                        
                        if drive_type == "hdd" and medium_path:
                            # Hard disk hajmini olish
                            disk_info = self.get_disk_info(medium_path)
                            hard_disks.append({
                                'controller': controller_name,
                                'port': port,
                                'device': device,
                                'path': medium_path,
                                'size': disk_info.get('size', 'Unknown'),
                                'format': disk_info.get('format', 'Unknown')
                            })
                            
            return hard_disks
            
        except Exception as e:
            print(f"Hard disk ma'lumotlarini olishda xatolik: {str(e)}")
            return []
            
    def get_disk_info(self, disk_path: str) -> Dict:
        """Disk haqida ma'lumot olish"""
        if not self.is_available():
            return {}
            
        try:
            result = subprocess.run([self.vboxmanage_path, "showhdinfo", disk_path], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return {}
                
            info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == "Capacity":
                        info['size'] = value
                    elif key == "Format":
                        info['format'] = value
                        
            return info
            
        except Exception as e:
            print(f"Disk ma'lumotlarini olishda xatolik: {str(e)}")
            return {}
            
    def resize_hard_disk(self, disk_path: str, new_size_mb: int) -> bool:
        """Hard disk hajmini o'zgartirish"""
        if not self.is_available():
            return False
            
        try:
            result = subprocess.run([self.vboxmanage_path, "modifyhd", disk_path, 
                                   "--resize", str(new_size_mb)], 
                                  capture_output=True, text=True, timeout=60)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Hard disk hajmini o'zgartirishda xatolik: {str(e)}")
            return False
            
    def add_hard_disk(self, uuid: str, disk_path: str, size_mb: int = 20480) -> bool:
        """Yangi hard disk qo'shish"""
        if not self.is_available():
            return False
            
        try:
            # Hard disk yaratish
            result = subprocess.run([self.vboxmanage_path, "createhd", "--filename", disk_path, 
                                   "--size", str(size_mb)], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                return False
                
            # VMga ulash
            result = subprocess.run([self.vboxmanage_path, "storageattach", uuid, 
                                   "--storagectl", "SATA Controller", "--port", "1", "--device", "0", 
                                   "--type", "hdd", "--medium", disk_path], 
                                  capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Hard disk qo'shishda xatolik: {str(e)}")
            return False
            
    def remove_hard_disk(self, uuid: str, port: str, device: str) -> bool:
        """Hard diskni olib tashlash"""
        if not self.is_available():
            return False
            
        try:
            result = subprocess.run([self.vboxmanage_path, "storageattach", uuid, 
                                   "--storagectl", "SATA Controller", "--port", port, "--device", device, 
                                   "--type", "hdd", "--medium", "none"], 
                                  capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Hard disk olib tashlashda xatolik: {str(e)}")
            return False
