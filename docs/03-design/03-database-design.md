# طراحی پایگاه داده

پایگاه داده سامانه Help Desk مسئول نگهداری اطلاعات کاربران، تیکت‌ها، پاسخ‌ها، فایل‌های پیوست و سایر داده‌های مورد نیاز سیستم است.

طراحی پایگاه داده بر اساس مدل دامنه (Domain Model)، نیازمندی‌های داده‌ای و نمودار موجودیت-رابطه (ERD) انجام شده است. هدف از این طراحی، ایجاد ساختاری منسجم، قابل توسعه و سازگار با نیازمندی‌های سامانه است.

## جدول User

اطلاعات کاربران سامانه در این جدول ذخیره می‌شود.

```text
User
------
id
name
username
email
role
status
created_at
updated_at
```

### توضیحات

* `id` : شناسه یکتای کاربر
* `name` : نام و نام خانوادگی
* `username` : شماره دانشجویی/ کارمندی یا نام کاربری
* `email` : پست الکترونیکی
* `role` : نقش کاربر در سامانه
* `status` : وضعیت حساب کاربری
* `created_at` : زمان ایجاد حساب
* `updated_at` : آخرین زمان ویرایش حساب

## جدول Ticket

اطلاعات درخواست‌های پشتیبانی در این جدول نگهداری می‌شود.

```text
Ticket
------
id
title
description
status
priority
created_at
updated_at
creator_id
category_id
department_id
assigned_to
satisfaction_rating
```

### توضیحات

* `creator_id` : کاربر ایجادکننده تیکت
* `category_id` : دسته‌بندی تیکت
* `department_id` : واحد مسئول رسیدگی
* `status` : وضعیت فعلی تیکت
* `priority` : سطح اولویت تیکت
* `assigned_to`: شناسه کارشناس مربوطه
* `satisfaction_rating`: امتیاز کاربر پس از پاسخ تیکت

## جدول Response

پاسخ‌ها و فعالیت‌های ثبت‌شده روی تیکت‌ها در این جدول ذخیره می‌شوند.

```text
Response
------
id
ticket_id
creator_id
parent_response_id
text
created_at
updated_at
```

### توضیحات

* `ticket_id` : تیکت مربوطه
* `creator_id` : ثبت‌کننده پاسخ
* `parent_response_id` : پاسخ والد (در صورت وجود)
* `text` : متن پاسخ

## جدول Category

دسته‌بندی‌های تیکت‌ها در این جدول نگهداری می‌شوند.

```text
Category
------
id
name
```

## جدول Department

واحدهای مسئول رسیدگی به درخواست‌ها در این جدول ذخیره می‌شوند.

```text
Department
------
id
name
```

## جدول Attachment

فایل‌های پیوست تیکت‌ها در این جدول ذخیره می‌شوند.

```text
Attachment
------
id
ticket_id
creator_id
response_id
file_name
file_type
path
created_at
```

### توضیحات

* `ticket_id` : تیکت مرتبط با فایل
* `creator_id` : بارگذاری‌کننده فایل
* `response_id`: پاسخ مرتبط با فایل (درصورت نیاز)
* `file_name` : نام فایل
* `file_type` : نوع فایل
* `path` : مسیر ذخیره‌سازی فایل

## جدول Notification

اطلاعات اعلان‌های سامانه در این جدول ذخیره می‌شود.

```text
Notification
------
id
receiver_id
creator_id
title
text
url
is_read
created_at
```

### توضیحات

* `receiver_id` : دریافت‌کننده اعلان
* `creator_id` : ایجادکننده اعلان
* `title` : عنوان اعلان
* `text` : متن اعلان
* `url` : لینک ارجاع
* `is_read` : وضعیت مشاهده اعلان
