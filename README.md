# VM-Container Bucket

Virtual mashinalar va konteynerlar uchun birlashtirilgan boshqaruv dasturi.

## Tavsif

Bu dastur turli xil virtualizatsiya texnologiyalarini bitta interfeysda boshqarish imkonini beradi:

- **Docker** - Konteynerlar
- **VirtualBox** - Virtual mashinalar  
- **Hyper-V** - Windows virtual mashinalar

## Xususiyatlar

### Docker
- Konteynerlarni ko'rish va boshqarish
- Imagelarni ko'rish
- Yangi konteyner yaratish
- Konteynerlarni ishga tushirish/to'xtatish

### VirtualBox
- Virtual mashinalarni ko'rish
- VM holatini boshqarish
- Yangi VM yaratish
- VM sozlamalarini ko'rish

### Hyper-V
- Windows virtual mashinalarini boshqarish
- VM yaratish va sozlash
- PowerShell orqali boshqarish

## O'rnatish

### Talablar
- Python 3.7+
- Docker (ixtiyoriy)
- VirtualBox (ixtiyoriy)
- Hyper-V (Windows, ixtiyoriy)

### O'rnatish qadamlar

1. Repository ni klonlash:
```bash
git clone <repository-url>
cd VM-CONT-BUCKET
```

2. Kerakli paketlarni o'rnatish:
```bash
pip install -r requirements.txt
```

3. Dasturni ishga tushirish:
```bash
python main.py
```

## Foydalanish

### Birinchi ishga tushirish
Dastur birinchi marta ishga tushganda barcha mavjud bo'lgan texnologiyalarni avtomatik aniqlaydi va faqat mavjud bo'lganlar uchun interfeys ko'rsatadi.

### Docker bilan ishlash
1. "Docker" tabiga o'ting
2. Mavjud konteynerlarni ko'ring
3. "Yangi Konteyner" tugmasini bosing
4. Kerakli parametrlarni kiriting

### VirtualBox bilan ishlash
1. "VirtualBox" tabiga o'ting
2. Mavjud VMlarni ko'ring
3. "Yangi VM" tugmasini bosing
4. VM parametrlarini sozlang

### Hyper-V bilan ishlash
1. "Hyper-V" tabiga o'ting
2. Mavjud VMlarni ko'ring
3. "Yangi VM" tugmasini bosing
4. VM parametrlarini sozlang

## Konfiguratsiya

Dastur sozlamalari `configs/settings.json` faylida saqlanadi. Quyidagi sozlamalarni o'zgartirish mumkin:

- Mavzu (light/dark)
- Til
- Avtomatik yangilash
- Har bir texnologiya uchun default qiymatlar

## Rivojlantirish

### Loyiha strukturasi
```
VM-CONT-BUCKET/
├── main.py                 # Asosiy dastur
├── requirements.txt        # Kerakli paketlar
├── managers/              # Texnologiya managerlari
│   ├── docker_manager.py
│   ├── virtualbox_manager.py
│   └── hyperv_manager.py
├── ui/                    # GUI komponentlari
│   └── main_window.py
├── utils/                 # Yordamchi funksiyalar
│   └── config_manager.py
├── configs/               # Sozlamalar
├── templates/             # VM template'lari
└── assets/                # Rasm va boshqa fayllar
```

### Yangi texnologiya qo'shish
1. `managers/` papkasida yangi manager yarating
2. `main.py` da import qiling
3. `ui/main_window.py` da interfeys qo'shing

## Muammolar va Yechimlar

### Docker ishlamayapti
- Docker Desktop ishga tushirilganligini tekshiring
- Docker daemon ishlamoqda ekanligini tekshiring

### VirtualBox ishlamayapti
- VirtualBox o'rnatilganligini tekshiring
- VBoxManage yo'li to'g'ri ekanligini tekshiring

### Hyper-V ishlamayapti
- Windows Pro/Enterprise versiyasida ishlatiladi
- Hyper-V ro'yxatdan o'tkazilganligini tekshiring
- PowerShell orqali boshqarish imkoniyati borligini tekshiring

## Litsenziya

Bu loyiha MIT litsenziyasi ostida tarqatiladi.

## Hissa qo'shish

1. Fork qiling
2. Yangi branch yarating
3. O'zgarishlarni commit qiling
4. Pull request yuboring

## Aloqa

Savollar va takliflar uchun issue oching.
