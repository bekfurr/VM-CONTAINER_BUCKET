#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISO Manager - ISO fayllarini boshqarish
"""

import os
import json
import requests
from typing import List, Dict
from urllib.parse import urlparse

class ISOManager:
    def __init__(self, templates_file: str = "templates/iso_templates.json"):
        self.templates_file = templates_file
        self.templates = self.load_templates()
        
    def load_templates(self) -> Dict:
        """ISO template'larini yuklash"""
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Template'larni yuklashda xatolik: {str(e)}")
                
        return {"popular_isos": [], "local_isos": []}
        
    def get_popular_isos(self) -> List[Dict]:
        """Mashhur ISO'larni olish"""
        return self.templates.get("popular_isos", [])
        
    def get_local_isos(self) -> List[Dict]:
        """Mahalliy ISO'larni olish"""
        return self.templates.get("local_isos", [])
        
    def add_local_iso(self, name: str, path: str, description: str = ""):
        """Mahalliy ISO qo'shish"""
        local_isos = self.templates.get("local_isos", [])
        
        # Mavjud ISO'ni tekshirish
        for iso in local_isos:
            if iso.get("name") == name:
                iso["path"] = path
                iso["description"] = description
                break
        else:
            local_isos.append({
                "name": name,
                "path": path,
                "description": description
            })
            
        self.templates["local_isos"] = local_isos
        self.save_templates()
        
    def remove_local_iso(self, name: str):
        """Mahalliy ISO'ni olib tashlash"""
        local_isos = self.templates.get("local_isos", [])
        self.templates["local_isos"] = [iso for iso in local_isos if iso.get("name") != name]
        self.save_templates()
        
    def save_templates(self):
        """Template'larni saqlash"""
        try:
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Template'larni saqlashda xatolik: {str(e)}")
            return False
            
    def download_iso(self, url: str, save_path: str, progress_callback=None) -> bool:
        """ISO fayl yuklab olish"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
                            
            return True
            
        except Exception as e:
            print(f"ISO yuklab olishda xatolik: {str(e)}")
            return False
            
    def get_iso_info(self, iso_path: str) -> Dict:
        """ISO fayl haqida ma'lumot olish"""
        if not os.path.exists(iso_path):
            return {}
            
        stat = os.stat(iso_path)
        size_mb = stat.st_size / (1024 * 1024)
        
        return {
            "path": iso_path,
            "name": os.path.basename(iso_path),
            "size": f"{size_mb:.1f} MB",
            "created": stat.st_ctime,
            "modified": stat.st_mtime
        }
        
    def scan_local_isos(self, directory: str) -> List[Dict]:
        """Papkadan ISO fayllarni topish"""
        iso_files = []
        
        if not os.path.exists(directory):
            return iso_files
            
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.iso'):
                        full_path = os.path.join(root, file)
                        iso_info = self.get_iso_info(full_path)
                        iso_files.append(iso_info)
                        
        except Exception as e:
            print(f"ISO fayllarni skan qilishda xatolik: {str(e)}")
            
        return iso_files
        
    def validate_iso(self, iso_path: str) -> bool:
        """ISO fayl to'g'riligini tekshirish"""
        if not os.path.exists(iso_path):
            return False
            
        # Asosiy tekshirish - fayl mavjudligi va hajmi
        try:
            stat = os.stat(iso_path)
            return stat.st_size > 1024 * 1024  # Kamida 1MB bo'lishi kerak
        except:
            return False
