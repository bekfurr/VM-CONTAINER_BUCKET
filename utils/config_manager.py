#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config Manager - Dastur sozlamalarini boshqarish
"""

import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_file: str = "configs/settings.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Sozlamalarni yuklash"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Sozlamalarni yuklashda xatolik: {str(e)}")
                
        # Default sozlamalar
        return {
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
        
    def save_config(self):
        """Sozlamalarni saqlash"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Sozlamalarni saqlashda xatolik: {str(e)}")
            return False
            
    def get(self, key: str, default=None):
        """Sozlamani olish"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
        
    def set(self, key: str, value: Any):
        """Sozlamani o'rnatish"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
        self.save_config()
        
    def get_docker_config(self) -> Dict[str, Any]:
        """Docker sozlamalarini olish"""
        return self.get("docker", {})
        
    def get_virtualbox_config(self) -> Dict[str, Any]:
        """VirtualBox sozlamalarini olish"""
        return self.get("virtualbox", {})
        
    def get_hyperv_config(self) -> Dict[str, Any]:
        """Hyper-V sozlamalarini olish"""
        return self.get("hyperv", {})
