```markdown
# 📅 Appointment Booking System

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15-red.svg)](https://www.django-rest-framework.org/)

> سامانه رزرو نوبت ساخته‌شده با **Django** و **Django REST Framework**

این پروژه یک سامانه رزرو نوبت است که در آن کاربران می‌توانند به عنوان مشتری یا ارائه‌دهنده خدمات فعالیت کنند.

هدف پروژه، تمرین و پیاده‌سازی بخش‌هایی از یک پروژه نسبتاً واقعی Django بوده است؛ از جمله احراز هویت و سطح دسترسی، مدیریت نوبت‌ها، طراحی REST API، جداسازی منطق کسب‌وکار، تست‌نویسی و کار با PostgreSQL.

Frontend پروژه با **Django Templates** و **CSS** ساخته شده و بخش‌های اصلی بدون JavaScript پیاده‌سازی شده‌اند.

---

## 📌 درباره پروژه

در این پروژه سه نقش اصلی وجود دارد:

| نقش | مسئولیت |
|------|----------|
| 🧑‍💼 **Customer** | رزرو، مشاهده و لغو نوبت‌ها |
| 👨‍⚕️ **Provider** | مدیریت خدمات، ساعات کاری و نوبت‌ها |
| 🛡️ **Admin** | مدیریت کاربران، ارائه‌دهندگان و نوبت‌ها |

برای بخش API از **Django REST Framework** استفاده شده و APIها با **Swagger / ReDoc** مستند شده‌اند.

در طراحی پروژه سعی شده منطق کسب‌وکار از Viewها جدا شود و ساختار پروژه تا حد امکان ماژولار و قابل توسعه باشد.

---

## ✨ امکانات

### 👤 کاربران و احراز هویت
- ثبت‌نام مشتری و ارائه‌دهنده
- ورود با Session Authentication
- سیستم نقش‌ها و سطح دسترسی
- ویرایش پروفایل
- تغییر رمز عبور
- بازیابی رمز عبور
- فعال‌سازی خودکار حساب ارائه‌دهنده

### 📅 رزرو نوبت
- رزرو نوبت در دو مرحله
- نمایش زمان‌های آزاد ارائه‌دهنده
- مشاهده تاریخچه نوبت‌ها
- لغو نوبت
- تأیید یا رد نوبت توسط ارائه‌دهنده
- جلوگیری از رزرو زمان‌های نامعتبر

### 👨‍💼 پنل ارائه‌دهنده
- مشاهده نوبت‌ها
- تأیید و رد درخواست‌ها
- تقویم روزانه، هفتگی و ماهانه
- مدیریت ساعات کاری
- مدیریت انواع خدمات
- ایجاد، ویرایش و حذف خدمات

### 🔔 اعلان‌ها
- سیستم Notification داخلی
- ایجاد خودکار اعلان‌ها با استفاده از Django Signals
- نمایش اعلان‌ها در بخش‌های مختلف سایت با Context Processor

### 🛠️ پنل مدیریت
- مشاهده کاربران
- مشاهده ارائه‌دهندگان
- مشاهده نوبت‌ها
- مدیریت اطلاعات اصلی سیستم

### 🔌 REST API
- پیاده‌سازی API با Django REST Framework
- API نسخه‌بندی‌شده با ساختار `v1`
- Serializer و Permissionهای اختصاصی
- Role-Based Access Control
- صفحه‌بندی نتایج
- Cache برای برخی پاسخ‌ها
- مستندات Swagger UI و ReDoc

### 🧪 تست
برای بخش‌های مختلف پروژه تست نوشته شده است:

- Modelها
- Service Layer
- APIها
- Viewهای HTML
- Permissionها
- Edge Caseها

---

## 🛠️ تکنولوژی‌ها

| بخش | تکنولوژی |
|------|----------|
| Language | Python 3.10+ |
| Backend | Django 5.2 |
| REST API | Django REST Framework 3.15+ |
| API Documentation | drf-yasg / Swagger / ReDoc |
| Database | PostgreSQL |
| Frontend | Django Templates / HTML / CSS |
| Authentication | Django Session Authentication |
| Testing | Django Test Framework |
| Architecture | Service Layer / Repository Pattern |

---

## 🏗️ ساختار پروژه

```
appointment-booking-system/
│
├── core/
│   ├── settings.py
│   └── urls.py
│
├── users/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── managers.py
│   ├── decorators.py
│   └── urls.py
│
├── appointments/
│   ├── api/
│   │   └── v1/
│   │       ├── views.py
│   │       ├── serializers.py
│   │       ├── permissions.py
│   │       └── urls.py
│   │
│   ├── models/
│   │   ├── appointment.py
│   │   ├── schedule.py
│   │   └── service_type.py
│   │
│   ├── services.py
│   ├── repositories.py
│   ├── views_html.py
│   ├── admin.py
│   ├── urls.py
│   └── tests/
│
├── notifications/
│   ├── models.py
│   ├── signals.py
│   ├── views.py
│   ├── context_processors.py
│   └── urls.py
│
├── templates/
├── static/
├── manage.py
└── requirements.txt
```

---

## 🧩 معماری و الگوهای استفاده‌شده

در پروژه از چند الگوی رایج برای جداسازی مسئولیت‌ها استفاده شده است:

| الگو | کاربرد |
|------|--------|
| **Service Layer** | جداسازی منطق کسب‌وکار از Viewها |
| **Repository Pattern** | کپسوله‌سازی Queryهای مربوط به دسترسی به داده |
| **Strategy Pattern** | مدیریت نمایش تقویم در حالت‌های روز، هفته و ماه |
| **Observer Pattern** | ایجاد اعلان‌ها با استفاده از Signals |
| **Decorator Pattern** | بررسی نقش کاربران در Viewهای تابعی |
| **API Versioning** | ساختار `/api/v1/` برای API |
| **Modular Models** | قرار دادن Modelهای اصلی در فایل‌های جداگانه |

---

## 🔐 امنیت و سطح دسترسی

- ✅ Session Authentication
- ✅ CSRF Protection برای فرم‌های POST
- ✅ Role-Based Access Control
- ✅ Permissionهای اختصاصی برای API
- ✅ بررسی نقش کاربر در Viewها
- ✅ Validation در Model، Service و Serializer
- ✅ مدیریت امن فرآیند تغییر و بازیابی رمز عبور

---

## 🚀 نصب و اجرا

### پیش‌نیازها
- Python 3.10+
- PostgreSQL
- Git

### ۱. دریافت پروژه
```bash
git clone https://github.com/Pourya84/appointment-booking-system.git
cd appointment-booking-system
```

### ۲. ساخت محیط مجازی

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### ۳. نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### ۴. تنظیم PostgreSQL

یک دیتابیس PostgreSQL ایجاد کنید و اطلاعات اتصال دیتابیس را در تنظیمات پروژه قرار دهید. سپس Migrationها را اجرا کنید:

```bash
python manage.py migrate
```

### ۵. ایجاد کاربر ادمین
```bash
python manage.py createsuperuser
```

### ۶. اجرای پروژه
```bash
python manage.py runserver
```

پروژه پس از اجرا از آدرس زیر در دسترس خواهد بود:

```
http://127.0.0.1:8000/
```

---

## 📡 REST API

**Base URL:** `/api/v1/`

| Method | Endpoint | توضیح |
|--------|----------|-------|
| `POST` | `/appointments/` | ایجاد نوبت |
| `GET` | `/appointments/my-appointments/` | نوبت‌های مشتری |
| `GET` | `/appointments/provider-appointments/` | نوبت‌های ارائه‌دهنده |
| `POST` | `/appointments/{id}/cancel/` | لغو نوبت |
| `POST` | `/appointments/{id}/confirm/` | تأیید نوبت |
| `POST` | `/appointments/{id}/reject/` | رد نوبت |
| `GET` | `/appointments/available-slots/{provider_id}/{date}/` | زمان‌های آزاد |
| `GET` | `/service-types/` | لیست خدمات |

### 📖 API Documentation

| سرویس | آدرس |
|--------|------|
| Swagger UI | `/swagger/` |
| ReDoc | `/redoc/` |
| OpenAPI JSON | `/swagger.json` |

---

## 🧪 اجرای تست‌ها

اجرای تمام تست‌ها:
```bash
python manage.py test
```

تست اپلیکیشن appointments:
```bash
python manage.py test appointments
```

تست کاربران:
```bash
python manage.py test users
```

تست اعلان‌ها:
```bash
python manage.py test notifications
```

اجرای یک تست مشخص:
```bash
python manage.py test appointments.tests.test_edge_cases
```

---

## 🌐 مسیرهای اصلی

| بخش | مسیر |
|------|------|
| Home | `/` |
| Django Admin | `/admin/` |
| Admin Dashboard | `/users/admin/dashboard/` |
| Customer Dashboard | `/app/customer/dashboard/` |
| Create Appointment | `/app/customer/create/` |
| Provider Dashboard | `/app/provider/dashboard/` |
| Provider Calendar | `/app/provider/calendar/` |
| Schedules | `/app/provider/schedules/` |
| Service Types | `/app/provider/service-types/` |
| Notifications | `/notifications/` |
| Password Change | `/password-change/` |
| Password Reset | `/password-reset/` |
| Swagger | `/swagger/` |
| ReDoc | `/redoc/` |
```

### 🔧 تغییرات اعمال‌شده (بدون تغییر در محتوا):

| مورد | توضیح |
|------|-------|
| **Badges** | سه بج Python, Django, DRF در ابتدای فایل اضافه شد |
| **جداکننده‌ها** | `---` بین بخش‌های اصلی برای خوانایی بیشتر |
| **جدول‌ها** | نقش‌ها، تکنولوژی‌ها، الگوها، APIها و مسیرها به جدول تبدیل شدند |
| **بلوک‌های کد** | تمام دستورات و مسیرها در ` ``` ` قرار گرفتند |
| **آیکون‌ها** | آیکون‌های مناسب به هر بخش اضافه شد (📅, 🛠️, 🏗️, 🔐 و ...) |
| **Bold** | تأکید روی کلمات کلیدی |
| **چک‌لیست** | بخش امنیت به `- ✅` تبدیل شد |
| **زیرعنوان‌ها** | استفاده از `###` برای زیربخش‌ها |

حالا README شما هم حرفه‌ای‌تر و هم خواناتر است، بدون اینکه محتوای اصلی تغییر کرده باشد. 🎯