#!/bin/bash

echo "VM-Container Bucket ishga tushmoqda..."
echo

# Python mavjudligini tekshirish
if ! command -v python3 &> /dev/null; then
    echo "Xatolik: Python3 o'rnatilmagan!"
    echo "Iltimos, Python 3.7+ ni o'rnating"
    exit 1
fi

# Kerakli paketlarni o'rnatish
echo "Kerakli paketlar o'rnatilmoqda..."
pip3 install -r requirements.txt

# Dasturni ishga tushirish
echo
echo "Dastur ishga tushmoqda..."
python3 main.py
