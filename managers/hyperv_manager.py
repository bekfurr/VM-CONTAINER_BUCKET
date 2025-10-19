#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyper-V Manager - Hyper-V virtual mashinalarini boshqarish
"""

import subprocess
import json
import os
import re
from typing import List, Dict, Optional

class HyperVManager:
    def __init__(self):
        self.is_available_flag = self.check_availability()
        
    def check_availability(self) -> bool:
        """Hyper-V mavjudligini tekshirish"""
        try:
            # PowerShell orqali Hyper-V modulini tekshirish
            result = subprocess.run([
                "powershell", "-Command", 
                "Get-Module -ListAvailable -Name Hyper-V"
            ], capture_output=True, text=True, timeout=10)
            
            return "Hyper-V" in result.stdout
            
        except:
            return False
            
    def is_available(self) -> bool:
        """Hyper-V mavjudligini tekshirish"""
        return self.is_available_flag
        
    def get_vms(self) -> List[Dict]:
        """Barcha virtual mashinalarni olish"""
        if not self.is_available():
            return []
            
        try:
            # PowerShell orqali VMlarni olish
            ps_command = """
            Get-VM | Select-Object Name, State, MemoryStartup, ProcessorCount, 
            CreationTime, Id | ConvertTo-Json
            """
            
            result = subprocess.run([
                "powershell", "-Command", ps_command
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return []
                
            try:
                vms_data = json.loads(result.stdout)
                if isinstance(vms_data, dict):
                    vms_data = [vms_data]
                    
                vms = []
                for vm in vms_data:
                    vms.append({
                        'name': vm.get('Name', 'Unknown'),
                        'state': vm.get('State', 'Unknown'),
                        'memory': f"{vm.get('MemoryStartup', 0) // (1024*1024)} MB",
                        'cpus': vm.get('ProcessorCount', 0),
                        'creation_time': vm.get('CreationTime', ''),
                        'id': str(vm.get('Id', ''))
                    })
                    
                return vms
                
            except json.JSONDecodeError:
                return []
                
        except Exception as e:
            print(f"VMlarni olishda xatolik: {str(e)}")
            return []
            
    def start_vm(self, vm_name: str) -> bool:
        """VMni ishga tushirish"""
        if not self.is_available():
            return False
            
        try:
            result = subprocess.run([
                "powershell", "-Command", f"Start-VM -Name '{vm_name}'"
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"VM ishga tushirishda xatolik: {str(e)}")
            return False
            
    def stop_vm(self, vm_name: str) -> bool:
        """VMni to'xtatish"""
        if not self.is_available():
            return False
            
        try:
            result = subprocess.run([
                "powershell", "-Command", f"Stop-VM -Name '{vm_name}' -Force"
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"VM to'xtatishda xatolik: {str(e)}")
            return False
            
    def create_vm(self, name: str, memory: int = 1024, cpus: int = 1, 
                  hard_disk_path: str = None, iso_path: str = None, hard_disk_size_gb: int = 20) -> bool:
        """Yangi VM yaratish"""
        if not self.is_available():
            return False
            
        try:
            # Memory MB dan GB ga o'tkazish
            memory_gb = memory // 1024
            if memory_gb < 1:
                memory_gb = 1
                
            # VM yaratish
            ps_command = f"""
            New-VM -Name '{name}' -MemoryStartupBytes {memory}MB -Generation 2
            Set-VM -Name '{name}' -ProcessorCount {cpus}
            """
            
            result = subprocess.run([
                "powershell", "-Command", ps_command
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"VM yaratishda xatolik: {result.stderr}")
                return False
                
            # Hard disk yaratish va qo'shish
            if not hard_disk_path:
                # Default hard disk yaratish
                ps_command = f"""
                $vmPath = (Get-VM -Name '{name}').Path
                $vhdPath = Join-Path $vmPath '{name}.vhdx'
                New-VHD -Path $vhdPath -SizeBytes {hard_disk_size_gb}GB -Dynamic
                Add-VMHardDiskDrive -VMName '{name}' -Path $vhdPath
                """
                
                subprocess.run([
                    "powershell", "-Command", ps_command
                ], capture_output=True, text=True, timeout=30)
            else:
                # Yangi hard disk yaratish va ulash
                ps_command = f"""
                New-VHD -Path '{hard_disk_path}' -SizeBytes {hard_disk_size_gb}GB -Dynamic
                Add-VMHardDiskDrive -VMName '{name}' -Path '{hard_disk_path}'
                """
                
                subprocess.run([
                    "powershell", "-Command", ps_command
                ], capture_output=True, text=True, timeout=30)
            
            # ISO ulash (agar berilgan bo'lsa)
            if iso_path and os.path.exists(iso_path):
                self.attach_iso(name, iso_path)
            
            print(f"VM muvaffaqiyatli yaratildi: {name}")
            return True
            
        except Exception as e:
            print(f"VM yaratishda xatolik: {str(e)}")
            return False
            
    def attach_iso(self, vm_name: str, iso_path: str) -> bool:
        """ISO fayl ulash"""
        if not self.is_available():
            return False
            
        try:
            ps_command = f"""
            Add-VMDvdDrive -VMName '{vm_name}' -Path '{iso_path}'
            """
            
            result = subprocess.run([
                "powershell", "-Command", ps_command
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"ISO ulashda xatolik: {str(e)}")
            return False
            
    def detach_iso(self, vm_name: str) -> bool:
        """ISO faylni olib tashlash"""
        if not self.is_available():
            return False
            
        try:
            ps_command = f"""
            $dvdDrive = Get-VMDvdDrive -VMName '{vm_name}'
            if ($dvdDrive) {{
                Remove-VMDvdDrive -VMName '{vm_name}' -ControllerNumber $dvdDrive.ControllerNumber -ControllerLocation $dvdDrive.ControllerLocation
            }}
            """
            
            result = subprocess.run([
                "powershell", "-Command", ps_command
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"ISO olib tashlashda xatolik: {str(e)}")
            return False
            
    def pause_vm(self, vm_name: str) -> bool:
        """VMni pauza qilish"""
        if not self.is_available():
            return False
            
        try:
            result = subprocess.run([
                "powershell", "-Command", f"Suspend-VM -Name '{vm_name}'"
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"VM pauza qilishda xatolik: {str(e)}")
            return False
            
    def resume_vm(self, vm_name: str) -> bool:
        """VMni davom ettirish"""
        if not self.is_available():
            return False
            
        try:
            result = subprocess.run([
                "powershell", "-Command", f"Resume-VM -Name '{vm_name}'"
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"VM davom ettirishda xatolik: {str(e)}")
            return False
            
    def reset_vm(self, vm_name: str) -> bool:
        """VMni qayta ishga tushirish"""
        if not self.is_available():
            return False
            
        try:
            result = subprocess.run([
                "powershell", "-Command", f"Restart-VM -Name '{vm_name}' -Force"
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"VM qayta ishga tushirishda xatolik: {str(e)}")
            return False
            
    def get_vm_status(self, vm_name: str) -> str:
        """VM holatini olish"""
        if not self.is_available():
            return "Unknown"
            
        try:
            result = subprocess.run([
                "powershell", "-Command", f"Get-VM -Name '{vm_name}' | Select-Object -ExpandProperty State"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "Unknown"
                
        except Exception as e:
            print(f"VM holatini olishda xatolik: {str(e)}")
            return "Unknown"
            
    def get_vm_hard_disks(self, vm_name: str) -> List[Dict]:
        """VM hard disk ma'lumotlarini olish"""
        if not self.is_available():
            return []
            
        try:
            ps_command = f"""
            Get-VMHardDiskDrive -VMName '{vm_name}' | Select-Object ControllerType, ControllerNumber, 
            ControllerLocation, Path, Size | ConvertTo-Json
            """
            
            result = subprocess.run([
                "powershell", "-Command", ps_command
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return []
                
            try:
                disks_data = json.loads(result.stdout)
                if isinstance(disks_data, dict):
                    disks_data = [disks_data]
                    
                hard_disks = []
                for disk in disks_data:
                    size_gb = disk.get('Size', 0) // (1024 * 1024 * 1024) if disk.get('Size') else 0
                    hard_disks.append({
                        'controller': f"{disk.get('ControllerType', 'Unknown')} {disk.get('ControllerNumber', 0)}",
                        'port': str(disk.get('ControllerLocation', 0)),
                        'device': str(disk.get('ControllerNumber', 0)),
                        'path': disk.get('Path', ''),
                        'size': f"{size_gb} GB",
                        'format': 'VHDX' if disk.get('Path', '').endswith('.vhdx') else 'VHD'
                    })
                    
                return hard_disks
                
            except json.JSONDecodeError:
                return []
                
        except Exception as e:
            print(f"Hard disk ma'lumotlarini olishda xatolik: {str(e)}")
            return []
            
    def resize_hard_disk(self, disk_path: str, new_size_gb: int) -> bool:
        """Hard disk hajmini o'zgartirish"""
        if not self.is_available():
            return False
            
        try:
            ps_command = f"""
            Resize-VHD -Path '{disk_path}' -SizeBytes {new_size_gb}GB
            """
            
            result = subprocess.run([
                "powershell", "-Command", ps_command
            ], capture_output=True, text=True, timeout=120)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Hard disk hajmini o'zgartirishda xatolik: {str(e)}")
            return False
            
    def add_hard_disk(self, vm_name: str, disk_path: str, size_gb: int = 20) -> bool:
        """Yangi hard disk qo'shish"""
        if not self.is_available():
            return False
            
        try:
            # Hard disk yaratish
            ps_command = f"""
            New-VHD -Path '{disk_path}' -SizeBytes {size_gb}GB -Dynamic
            Add-VMHardDiskDrive -VMName '{vm_name}' -Path '{disk_path}'
            """
            
            result = subprocess.run([
                "powershell", "-Command", ps_command
            ], capture_output=True, text=True, timeout=60)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Hard disk qo'shishda xatolik: {str(e)}")
            return False
            
    def remove_hard_disk(self, vm_name: str, controller_number: int, controller_location: int) -> bool:
        """Hard diskni olib tashlash"""
        if not self.is_available():
            return False
            
        try:
            ps_command = f"""
            Remove-VMHardDiskDrive -VMName '{vm_name}' -ControllerNumber {controller_number} -ControllerLocation {controller_location}
            """
            
            result = subprocess.run([
                "powershell", "-Command", ps_command
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Hard disk olib tashlashda xatolik: {str(e)}")
            return False
