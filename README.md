================================================================================
                      سامانه رزرو نوبت (Appointment Booking System)
================================================================================

یک پروژه جامع و حرفه‌ای برای مدیریت رزرو نوبت با قابلیت‌های مشتری،
ارائه‌دهنده خدمات و مدیریت، پیاده‌سازی شده با Django و Django REST Framework.

--------------------------------------------------------------------------------
                           ✨ ویژگی‌های اصلی
--------------------------------------------------------------------------------

✅ احراز هویت مبتنی بر Session با نقش‌های customer، provider، admin
✅ پنل مشتری: رزرو نوبت (دو مرحله‌ای بدون جاوااسکریپت)، لغو نوبت، مشاهده تاریخچه نوبت‌ها
✅ پنل ارائه‌دهنده: تأیید/رد نوبت، تقویم روز/هفته/ماه، مدیریت ساعات کاری (CRUD)، مدیریت انواع خدمات (CRUD)
✅ پنل مدیریت سایت (سفارشی برای ادمین): مشاهده کاربران، ارائه‌دهندگان، همه نوبت‌ها
✅ سیستم اعلان داخل سایت (Notification) با استفاده از Signals و Context Processor
✅ APIهای RESTful با Django REST Framework (مستند شده با Swagger/ReDoc)
✅ مستندات تعاملی Swagger UI و ReDoc برای تست و بررسی APIها
✅ تست‌های خودکار (Unit Tests) برای مدل‌ها، سرویس‌ها، APIها و ویوهای HTML
✅ مدیریت پروفایل کاربر (ویرایش اطلاعات و تغییر رمز عبور)
✅ ثبت‌نام ارائه‌دهنده با فعال‌سازی خودکار
✅ کد تمیز، ماژولار و پیرو الگوهای طراحی (Service Layer, Repository, Strategy, Observer)

--------------------------------------------------------------------------------
                           🛠️ تکنولوژی‌ها
--------------------------------------------------------------------------------

- Python 3.10+
- Django 5.2
- Django REST Framework 3.15+
- drf-yasg (Swagger/ReDoc)
- PostgreSQL (توسعه و تولید)
- HTML5 + CSS3 (بدون جاوااسکریپت)

--------------------------------------------------------------------------------
                           📂 ساختار پروژه
--------------------------------------------------------------------------------

core/                           # تنظیمات اصلی پروژه
├── settings.py                 # تنظیمات عمومی
└── urls.py                     # مسیرهای سطح بالا

users/                          # اپ مدیریت کاربران
├── models.py                   # مدل سفارشی User با نقش‌ها (RoleChoices داخلی)
├── views.py                    # ثبت‌نام مشتری و ارائه‌دهنده، ویرایش پروفایل
├── decorators.py               # دکوراتور require_role
├── managers.py                 # CustomUserManager
├── forms.py                    # فرم‌های سفارشی (بازیابی رمز)
└── urls.py                     # مسیرهای مربوط به کاربران

appointments/                   # اپ اصلی (هسته پروژه)
├── api/
│   └── v1/                     # نسخه‌بندی API
│       ├── views.py            # ویوهای API (DRF)
│       ├── serializers.py      # سریالایزرهای ورودی/خروجی
│       ├── permissions.py      # RolePermission (کلاس مجوز)
│       └── urls.py             # مسیرهای API نسخه 1
├── models/                     # پکیج مدل‌ها (جداگانه)
│   ├── appointment.py          # مدل Appointment
│   ├── schedule.py             # مدل Schedule
│   └── service_type.py         # مدل ServiceType
├── services.py                 # منطق تجاری (Service Layer)
├── repositories.py             # Repository Pattern (جایگزین Selector)
├── views_html.py               # ویوهای HTML (بدون JS)
├── admin.py
├── urls.py                     # مسیرهای HTML
└── tests/                      # تست‌های جامع (شامل Edge Cases)

notifications/                  # اپ اعلان‌ها
├── models.py
├── signals.py                  # سیگنال‌های ارسال اعلان
├── views.py
├── context_processors.py
└── urls.py

templates/                      # قالب‌های HTML
├── base.html
├── registration/               # لاگین، ثبت‌نام، بازیابی رمز
├── appointments/               # داشبوردها، رزرو، تقویم، مدیریت
└── notifications/              # لیست اعلان‌ها

static/                         # فایل‌های استاتیک (CSS)
└── appointments/css/base.css

--------------------------------------------------------------------------------
                           🚀 نصب و راه‌اندازی
--------------------------------------------------------------------------------

1. کلون مخزن
   git clone https://github.com/yourusername/appointment-booking.git
   cd appointment-booking

2. ایجاد و فعال‌سازی محیط مجازی
   ویندوز:
   python -m venv venv
   venv\Scripts\activate

   لینوکس/مک:
   python3 -m venv venv
   source venv/bin/activate

3. نصب وابستگی‌ها
   pip install -r requirements.txt

4. تنظیم دیتابیس PostgreSQL
   - ایجاد دیتابیس با نام appointment_db
   - تنظیم نام کاربری و رمز عبور در settings.py (یا استفاده از .env)

5. اعمال مایگریشن‌ها
   python manage.py makemigrations
   python manage.py migrate

6. جمع‌آوری فایل‌های استاتیک
   python manage.py collectstatic

7. ایجاد کاربر ادمین (سوپر یوزر)
   python manage.py createsuperuser

8. اجرای سرور توسعه
   python manage.py runserver

--------------------------------------------------------------------------------
                           🌐 دسترسی به بخش‌های مختلف
--------------------------------------------------------------------------------

صفحه اصلی                          /
پنل ادمین جنگو                     /admin/
پنل مدیریت سایت (سفارشی)          /users/admin/dashboard/  (فقط نقش admin)
داشبورد مشتری                      /app/customer/dashboard/
رزرو نوبت (مرحله اول)              /app/customer/create/
داشبورد ارائه‌دهنده                /app/provider/dashboard/
تقویم پیشرفته (روز/هفته/ماه)       /app/provider/calendar/
مدیریت ساعات کاری                  /app/provider/schedules/
مدیریت انواع خدمات                 /app/provider/service-types/
لیست اعلان‌ها                       /notifications/
تغییر رمز عبور (کاربر لاگین شده)    /password-change/
بازیابی رمز عبور                    /password-reset/
مستندات Swagger UI                 /swagger/
مستندات ReDoc                      /redoc/
فایل OpenAPI JSON                  /swagger.json

--------------------------------------------------------------------------------
                           📡 APIها (نسخه v1)
--------------------------------------------------------------------------------

مسیر پایه: /api/v1/

متد    آدرس                                          توضیح                      نقش
POST    /appointments/                                رزرو نوبت جدید             مشتری
GET     /appointments/my-appointments/                لیست نوبت‌های مشتری جاری   مشتری
GET     /appointments/provider-appointments/          لیست نوبت‌های ارائه‌دهنده  ارائه‌دهنده
POST    /appointments/{id}/cancel/                    لغو نوبت                   مشتری یا ارائه‌دهنده
POST    /appointments/{id}/confirm/                   تایید نوبت                 ارائه‌دهنده
POST    /appointments/{id}/reject/                    رد نوبت                    ارائه‌دهنده
GET     /appointments/available-slots/{provider_id}/{date}/  دریافت زمان‌های آزاد  همه
GET     /service-types/                               لیست انواع خدمات           همه

نکته: مستندات کامل و تعاملی در /swagger/ قابل مشاهده است.
پاسخ‌ها با کش (LocMemCache) و صفحه‌بندی (PageNumberPagination) بهینه‌سازی شده‌اند.

--------------------------------------------------------------------------------
                           🧪 تست‌ها
--------------------------------------------------------------------------------

اجرای تمام تست‌های اپلیکیشن‌ها:
python manage.py test

اجرای تست‌های اپ appointments:
python manage.py test appointments

اجرای تست‌های اپ users:
python manage.py test users

اجرای تست‌های اپ notifications:
python manage.py test notifications

اجرای یک فایل تست خاص:
python manage.py test appointments.tests.test_edge_cases

--------------------------------------------------------------------------------
                           🧩 الگوهای طراحی و معماری
--------------------------------------------------------------------------------

- Service Layer: جداسازی منطق تجاری (services.py) از ویوها
- Repository Pattern: کپسوله‌سازی کوئری‌های خواندن داده (repositories.py)
- Strategy Pattern: نمایش نوبت‌ها در قالب روز/هفته/ماه (تقویم)
- Observer Pattern: ارسال خودکار اعلان‌ها با استفاده از Signals
- Decorator Pattern: بررسی نقش کاربران با دکوراتور require_role
- نسخه‌بندی API: ساختار api/v1/ برای توسعه و تغییرات آینده
- جداسازی مدل‌ها: هر مدل در فایل جداگانه در پکیج models/

--------------------------------------------------------------------------------
                           🛡️ امنیت
--------------------------------------------------------------------------------

- احراز هویت مبتنی بر Session با کوکی‌های امن
- CSRF Protection در تمام فرم‌های POST
- Role-Based Access Control (RBAC) در ویوها و APIها (RolePermission)
- دکوراتور require_role برای بررسی نقش در ویوهای تابعی
- Validation در سه لایه (مدل، سرویس، سریالایزر) برای جلوگیری از ورود داده‌های ناسازگار
- بازیابی رمز عبور با اعتبارسنجی وجود ایمیل در دیتابیس

--------------------------------------------------------------------------------
                           📦 وابستگی‌های اصلی
--------------------------------------------------------------------------------

- Django>=5.2
- djangorestframework>=3.15
- drf-yasg>=1.21.8
- psycopg2-binary (برای PostgreSQL)

--------------------------------------------------------------------------------
                           📄 لایسنس
--------------------------------------------------------------------------------

MIT

تاریخ انتشار: تیر ۱۴۰5
نسخه: v1.0.0
================================================================================