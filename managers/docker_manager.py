#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker Manager - Docker konteynerlarini boshqarish
"""

import docker
import json
import os
from typing import List, Dict, Optional

class DockerManager:
    def __init__(self):
        self.client = None
        self.is_connected = False
        self.connect()
        
    def connect(self):
        """Docker clientga ulanish"""
        try:
            self.client = docker.from_env()
            # Ulanishni tekshirish
            self.client.ping()
            self.is_connected = True
            print("Docker ga muvaffaqiyatli ulandi")
        except Exception as e:
            print(f"Docker ga ulanishda xatolik: {str(e)}")
            self.is_connected = False
            
    def is_available(self) -> bool:
        """Docker mavjudligini tekshirish"""
        return self.is_connected
        
    def get_containers(self, all_containers: bool = True) -> List[Dict]:
        """Barcha konteynerlarni olish"""
        if not self.is_connected:
            return []
            
        try:
            containers = self.client.containers.list(all=all_containers)
            result = []
            
            for container in containers:
                result.append({
                    'id': container.short_id,
                    'name': container.name,
                    'image': container.image.tags[0] if container.image.tags else container.image.id,
                    'status': container.status,
                    'created': container.attrs['Created'],
                    'ports': container.ports
                })
                
            return result
            
        except Exception as e:
            print(f"Konteynerlarni olishda xatolik: {str(e)}")
            return []
            
    def get_images(self) -> List[Dict]:
        """Barcha imagelarni olish"""
        if not self.is_connected:
            return []
            
        try:
            images = self.client.images.list()
            result = []
            
            for image in images:
                result.append({
                    'id': image.short_id,
                    'tags': image.tags,
                    'size': image.attrs['Size'],
                    'created': image.attrs['Created']
                })
                
            return result
            
        except Exception as e:
            print(f"Imagelarni olishda xatolik: {str(e)}")
            return []
            
    def run_container(self, image_name: str, name: str = None, 
                     ports: Dict = None, environment: Dict = None,
                     volumes: Dict = None) -> bool:
        """Yangi konteyner ishga tushirish"""
        if not self.is_connected:
            return False
            
        try:
            container = self.client.containers.run(
                image_name,
                name=name,
                ports=ports,
                environment=environment,
                volumes=volumes,
                detach=True
            )
            print(f"Konteyner muvaffaqiyatli ishga tushirildi: {container.name}")
            return True
            
        except Exception as e:
            print(f"Konteyner ishga tushirishda xatolik: {str(e)}")
            return False
            
    def stop_container(self, container_id: str) -> bool:
        """Konteynerni to'xtatish"""
        if not self.is_connected:
            return False
            
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            print(f"Konteyner to'xtatildi: {container.name}")
            return True
            
        except Exception as e:
            print(f"Konteyner to'xtatishda xatolik: {str(e)}")
            return False
            
    def remove_container(self, container_id: str) -> bool:
        """Konteynerni o'chirish"""
        if not self.is_connected:
            return False
            
        try:
            container = self.client.containers.get(container_id)
            container.remove()
            print(f"Konteyner o'chirildi: {container.name}")
            return True
            
        except Exception as e:
            print(f"Konteyner o'chirishda xatolik: {str(e)}")
            return False
            
    def pull_image(self, image_name: str) -> bool:
        """Image yuklab olish"""
        if not self.is_connected:
            return False
            
        try:
            self.client.images.pull(image_name)
            print(f"Image yuklab olindi: {image_name}")
            return True
            
        except Exception as e:
            print(f"Image yuklab olishda xatolik: {str(e)}")
            return False
