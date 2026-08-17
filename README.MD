# 🛒 Shop API - FastAPI Backend Service

A complete backend application for an e-commerce store, built using modern asynchronous Python architecture.

## 🚀 Quick Start

To run the project on your local machine, follow these steps:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🛠️ Tech Stack

* **Framework:** FastAPI
* **Database & ORM:** SQLModel / SQLAlchemy (AsyncSession) with SQLite (aiosqlite)
* **Auth & Security:** PyJWT (JSON Web Tokens), Passlib / Bcrypt, HTTPBearer
* **Logging & Imaging:** Loguru, Pillow (PIL)
* **Data Validation:** Pydantic V2
* **File Management:** Pathlib
* **Main Algorithm:** Hash Table Algorithm
* **Concurrency Control:** Atomic Update (used to fix the Inventory Race Condition vulnerability)

---

# 🗄️ Database Schemas & Models

---

## 👤 1. Users Table (`Users`)
* **Primary Key (`id`):** A unique, automatically generated ID for each user.
* **Role (`status`):** Defines the user's role in the system (Default value: `"User"`).
* **Personal Data:** Stores name (`name`), email (`email`), hashed password (`password`), and age (`age`).
* **Optional Data:** Profile picture path (`image`) and a short bio (`overview`).

---

## 📦 2. Products Table (`Products`)
* **Core Data:** Product ID (`id`), name (`name`), description (`description`), price (`price`), and available stock (`quantity`).
* **Timestamp (`time_add`):** Uses `default_factory` with `datetime.now(timezone.utc)` to record the exact product creation time in UTC.
* **Status & Category:** `is_active` field to check product availability, and `category` to group products (e.g., Electronics, Fashion).
* **Media & Extra Info:** Fields for four image paths (`image_route1` to `image_route4`), creator ID (`admin_id`), manufacturer (`brand`), discounted price (`discount_price`), weight (`weight`), and size (`size`).

---

## 🛒 3. Shopping Carts Table (`ShoppingCarts`)
* **Relationships (`Foreign Keys`):** Links each cart item to a user (`user_id`) and a product (`product_id`) to ensure data integrity.
* **Quantity Constraint (`quantity`):** Defines the requested amount with a validation rule (`ge=1`) to make sure the item count is at least 1.
* **Timestamp (`time_add`):** Records when the product was added to the cart using UTC.

---

## 📦 4. Orders Table (`Orders`)
* **IDs & Links:** Primary key `id`, and the client ID (`user_id`) connected to the Users table.
* **Order Date (`time_add`):** Records the exact order creation time using `timezone.utc`.
* **Order Status (`is_active`):** A boolean flag to check if the order is currently active or canceled.

---

## 📑 5. Order Items Table (`OrdersItems`)
* **Relationships:** Links each item to its main order (`order_id`) and the purchased product (`product_id`).
* **Historical Data Snapshot (Financial Archiving):** 
  * Stores the product name (`product_name`) and price per unit (`unit_price`) at the exact time of purchase. This protects invoice records from future changes in the main Products table (such as price updates or product deletions).
  * Saves the requested amount (`quantity`) and the calculated total price for that item (`subtotal`).

---

## ⚙️ Database Initialization & Connection (`init_db & Engine`)
* **Asynchronous Connection Engine (`create_async_engine`):** Connects the app to a specific SQLite file (`shop.db`) using the `aiosqlite` library for async operations.
* **Safe Transactions (`engine.begin`):** Uses `begin()` to guarantee an automatic `Rollback` if database creation fails, protecting data integrity.
* **Table Creation (`run_sync`):** Creates all tables at once in the background using `SQLModel.metadata.create_all` to keep the server running smoothly.

---

## 🔐 Authentication & Authorization System

The system includes a built-in module to manage user accounts, generate secure tokens, and verify permissions.

### 1. Validation Schemas (Pydantic Models)

* **`CheckingInputInformation`**: Validates registration data when creating a new account.
  * **Name and Age:** Matches basic field requirements.
  * **Password:** Uses a `field_validator` to enforce a strong password (8 to 16 characters, including numbers, symbols, and uppercase letters).
  * **Email:** Uses a `field_validator` with Regex to check for a valid email format.
* **`Recording`**: Handles user login inputs (`email`, `password`).
* **`CheckingTheOutput`**: A custom structured response model that returns the access token (`token: str`).

---

### 2. API Endpoints

**Base Path:** `/api/v1` | **Tag:** `Recording`

#### ➕ Register a New Account (`POST /create_account`)
1. **Duplicate Check:** Scans the email using the `no_user_available` function to prevent duplicate accounts.
2. **Encryption:** Hashes the password securely using the `password_encryption` function.
3. **Saving Data:** Inserts the new user data into the database using the `insort` function.
4. **Token Generation:** Generates and returns an access token immediately upon successful registration.

#### 🔑 User Login (`POST /recording`)
1. **Account Verification:** Looks up the email and encrypted password using the `select_user` function.
2. **Hash Matching:** Compares the entered password with the stored hash using the `check_password_match` function.
3. **Fetch Details:** Extracts the specific user ID (`id_user`).
4. **Return Token:** Generates a new JWT token and returns it inside the response.

---
## 📌 Admin Panel Product Management Routes Guide (Products Admin Panel)

---

### 📦 1. Add a New Product Route (`POST /product`)
* **Data Processing & Sanitization (`get_product_data`):** Receives the input data through a `Form` and passes it to `distance_cleaner` to clean and sanitize it before storing it in the `ProductInputs` model class.
* **Validation & Multiple Image Uploads:** The route accepts up to 4 image files (`file1` to `file4`). It requires at least the first primary image, while the other three are optional.
* **Processing & Storage:** Images are passed through the `ImagesProcessing` class to validate their type and size. They are then resized and compressed to `800x800` at `85%` quality and saved in the `uploads/products` folder with unique `UUID` filenames.
* **Database Storage & URL Generation:** Saves the product details using `adding_products_database`, then generates dynamic URLs for the images via `request.url_for` using object conversion (`model_validate` with `from_attributes = True`).

---

### ✏️ 2. Partial Product Update Route (`PATCH /product/{product_id}`)
* **Flexible Data Modification:** Relies on the `ProductUpdate` model, which uses optional fields (`None`) to update only the fields sent in the request.
* **Data Dumping:** Uses `model_dump(exclude_none=True)` to exclude empty fields, then passes the filtered data to `product_update_database`. This function uses `setattr` to dynamically update the required columns based on the product ID (`product_id`).

---

### 🔍 3. View Inactive and Out-of-Stock Products Route (`GET /products/inactive`)
* **Pagination:** Supports `limit` and `offset` query parameters to manage the number of items displayed per batch.
* **Advanced Conditional Query:** Calculates the total count and filters the products in the database using `func.count` combined with an `or_` condition (products where `is_active == False` or where stock is depleted, `quantity == 0`).
* **Result Ordering:** Fetches the products sorted in descending order from newest to oldest using `order_by(Products.id.desc())` and prepares their images and links for display.

---

### 🗑️ 4. Delete Product Route (`DELETE /product/{product_id}`)
* **Database Deletion:** Calls `product_delete_database` to find and permanently remove the product from the database, returning the deleted product object to access its associated image names.
* **Local Storage Cleanup:** Loops through the four product image fields and uses the `Pathlib` library along with the `delete_images_product` function to permanently delete the physical files from the hard drive, preventing storage clutter.
  
---

## 📌 General & E-commerce Routes Guide (Shopping Cart & Checkout Operations)

---

### 👁️ 1. View Product Page Details (`GET /product/page/{product_id}`)
* **Fetch Product Data:** Calls the database function `product_page_view_database` to look up the product by its ID (`product_id`). It returns the product details or triggers a `404` error if the product is not found.
* **Prepare Image Links:** Loops through the four product image fields and generates dynamic access links using `request.url_for`.
* **Validation & Model Transformation:** Uses `model_validate` with `from_attributes = True` to merge the database object into the `ProductPageViewDatabase` response model for display.

---
### 🔍 2. Product Search & General Browsing (`GET /product/search` & `GET /products`)
* **Flexible Advanced Search (`ilike`):** The search route uses the `or_` function with `ilike` to search simultaneously across product names, categories, and brands while ignoring letter casing.
* **Pagination:** Supports `limit` and `offset` query parameters to organize product delivery in batches, returning the total results count (`total_Products` or `total_products`) for the frontend and user.
* **Stock Status Validation:** Only displays active products that have a stock count greater than zero (`is_active == True` and `quantity != 0`), sorted in descending order from newest to oldest using `order_by(Products.id.desc())`.

---

### 🛒 3. Shopping Cart Management (`Basket Operations`)
* **Add Product to Cart (`POST /products/basket/{product_id}`):** Verifies the existence, active status, and available stock of the product before adding it or updating its quantity inside the `ShoppingCarts` table.
* **View Cart Contents (`GET /products/basket`):** Fetches all items linked to the current user's cart using a `join` between the cart table and the products table, calculating the total price for each item based on its quantity.
* **Update & Delete Cart Items (`PUT / DELETE`):** Allows users to update requested quantities or remove specific items from the cart, while validating stock availability and user authorization via `verify_token`.

---

### 💳 4. Checkout Operations & Invoicing (`Orders & Invoices`)
* **Place Order (`POST /order`):** 
  * Creates a new order record (`Orders`) and uses `flush` to capture the order ID without executing an early, final save.
  * Uses a **Hash Table** algorithm via Python dictionaries (`product_dict`) to map cart items to the products table efficiently, eliminating expensive nested loops.
* **Inventory Race Condition Protection:** Implements atomic updates (`update` with strict quantity and status conditions) to prevent ghost sales if quantities are split or depleted during checkout, executing a session `rollback` if any error occurs.
* **Invoice Management & Cancellation (`GET / DELETE /order`):** Allows users to view their past purchase invoices with full details, alongside the ability to cancel an order via `cancel_order`.

---

### ⏱️ 1. Cancellation Window Validation (24-Hour Window)
* **UTC Timestamp Handling (`timezone.utc`):** Configures the order creation time (`order.time_add`) to align with Coordinated Universal Time.
* **Strict Time Constraint:** Checks that the difference between the current time and the order creation time does not exceed 24 hours (`timedelta(hours=24)`). If this window passes, an `HTTPException(422)` is raised to block late cancellations.

---

### 📦 2. Fetching & Updating Order Items and Stock (`Restoring Quantities`)
* **Invoice Items Query:** Fetches all items associated with the order ID (`order_id`) from the `OrdersItems` table and verifies their existence.
* **Smart Stock Restoration (Hash Table & Bulk Lookup):** Collects product IDs and retrieves them all at once using the `in_` operator, then maps them into a dictionary (`product_dict`) for fast and efficient stock quantity updates.
* **Restoring Quantities & Order Cancellation:** Adds the sold quantities back to the main product stock (`product.quantity += item.quantity`), then permanently deletes the order items (`item`) and the primary order record (`order`) from the database before finalizing the process via `session.commit()`.

---
# 🧪 System Testing Guide (Pytest & FastAPI TestClient)

---

## 🛠️ 1. Global Setup & Tools (`Setup & Imports`)
* **Simulation Mocking (`TestClient`):** Creates a mock testing instance `testing` to communicate with the application's (`FastAPI`) routes, sending requests and catching responses smoothly without booting a physical server.
* **In-Memory Image Buffering (`io.BytesIO & Pillow`):** Uses the `PIL` library to generate dummy images with required dimensions and colors, storing them temporarily in RAM via `io.BytesIO` to maximize speed and bypass slow hard drive writes.

---

## 👤 2. Authentication & User Tests (`Auth & User Tests`)
* **Account Creation (`test_code_creation`):** Submits a test request to register a new user account, then directly modifies their status in the test database to an `ADMIN` role for downstream product testing.
* **User Login & Token Extraction (`test_code_recording & auth_token`):** A custom fixture function (`@pytest.fixture`) tasked with submitting login credentials and parsing the returned `JWT Token` to secure subsequent private endpoints automatically.
* **Profile Image Operations (`test_add_user_image & test_delete_image`):** Verifies profile image uploads by passing dummy RAM-buffered assets through the `files` parameter, followed by a check on the image removal endpoint.
* **Account Deletion (`test_delete_user`):** Validates account destruction by passing both the account password and the authentication token to purge the record permanently.

---

## 🛍️ 3. Product, Cart, & Checkout Lifecycle Tests (`Product & Cart Lifecycle Test`)
* **Add a New Product (`Admin Product`):** Generates a dummy product image asset, passing textual inputs and the file attachment simultaneously via `data` and `files` parameters under an authorized Admin account to verify successful item creation and capture the `product_id`.
* **Cart Insertion & Checkout (`Basket & Order`):** Simulates adding the newly created item into the active user's shopping basket, followed by a transaction request to checkout (`Order`) and parse the resulting `invoice_id`.
* **Order Cancellation & Item Cleanup (`Cleanup & Rollback`):** Validates the order cancellation routing to ensure accurate stock recovery, ending with a test on the Admin-level product deletion path to completely clean up database records.

---

# 🛒 Shop API - FastAPI Backend Service

تطبيق برمجي متكامل لإدارة الخدمات الخلفية (Backend) لمتجر إلكتروني مبني باستخدام أحدث تقنيات بايثون المتزامنة (Async Architecture).
## 🚀 تشغيل المشروع (Quick Start)

لتشغيل المشروع على جهازك المحلي، اتبع الخطوات التالية:

1. **تثبيت المتطلبات والمكتبات:**
   ```bash
   pip install -r requirements.txt
---
## 🛠️ التقنيات المستخدمة (Tech Stack)

* **الإطار البرمجي (Framework):** FastAPI
* **قواعد البيانات (ORM & Database):** SQLModel / SQLAlchemy (AsyncSession/Async) مع SQLite (aiosqlite)
* **المصادقة والأمان (Auth & Security):** PyJWT (JSON Web Tokens), Passlib / Bcrypt, HTTPBearer
* **تسجيل البيانات والمعالجة (Logging & Imaging):** Loguru, Pillow (PIL)
* **التحقق من البيانات (Data Validation):** Pydantic V2
* **للتعامل مع  مسارات الملفات و المجلدات:** Pathlib
* **اشهر الخوارزميات المستخدمة** Hash Table Algorithm
* **التقنية المستخدمة لحل ثغرة سباق المخزون(Inventory Race Condition)** Atomic Update
---
# 🗄️ هيكل جداول قاعدة البيانات (Database Schemas & Models)

---

## 👤 1. جدول المستخدمين (`Users`)
* **المفتاح الرئيسي (`id`):** معرّف فريد لكل مستخدم يتم توليده تلقائياً (`Primary Key`).
* **الصلاحية (`status`):** تحديد دور المستخدم في النظام (القيمة الافتراضية `"User"`).
* **البيانات الشخصية:** تخزين الاسم (`name`), البريد الإلكتروني (`email`), كلمة المرور المشفرة (`password`), والعمر (`age`).
* **البيانات الاختيارية:** حقل مسار الصورة الشخصية (`image`) وحقل النبذة التعريفية (`overview`).

---

## 📦 2. جدول المنتجات (`Products`)
* **البيانات الأساسية:** معرّف المنتج (`id`), الاسم (`name`), الوصف (`description`), السعر (`price`), والكمية المتوفرة (`quantity`).
* **التوقيت الزمني (`time_add`):** استخدام `default_factory` مع `datetime.now(timezone.utc)` لتسجيل وقت إضافـة المنتج بدقة وفق التوقيت العالمي الموحد.
* **الحالة والصنف:** حقل `is_active` للتحقق من توفر المنتج، وحقل `category` لتصنيف المنتجات (إلكترونيات، أزياء، إلخ).
* **معلومات الوسائط والتفاصيل الاختيارية:** حقول لروابط الصور الأربعة (`image_route1` إلى `image_route4`)، معرّف المشرف (`admin_id`), الشركة المصنعة (`brand`), السعر بعد الخصم (`discount_price`), الوزن (`weight`), والمقاس (`size`).

---

## 🛒 3. جدول سلة التسوق (`ShoppingCarts`)
* **الربط بالعلاقات (`Foreign Keys`):** ربط السلة بكل من جدول المستخدمين (`user_id`) وجدول المنتجات (`product_id`) لضمان تكامل البيانات.
* **الكمية والقيود (`quantity`):** تحديد الكمية المطلوبة مع شرط التحقق `ge=1` لضمان ألا تقل الكمية عن قطعة واحدة.
* **وقت الإضافة (`time_add`):** تسجيل وقت إضافة المنتج للسلة باستخدام التوقيت العالمي الموحد.

---

## 📦 4. جدول الطلبات الرئيسية (`Orders`)
* **المعرّف والربط:** مفتاح رئيسي `id`، ومعرّف المستخدم صاحب الطلب `user_id` المرتبط بجدول المستخدمين.
* **تاريخ الطلب (`time_add`):** توثيق وقت إنشاء الطلب بدقة باستخدام `timezone.utc`.
* **حالة الطلب (`is_active`):** مؤشر يحدد ما إذا كان الطلب نشطاً أو ملغياً.

---

## 📑 5. جدول عناصر الطلب والأرشفة (`OrdersItems`)
* **الربط:** يربط كل عنصر طلب برقم الطلب الأساسي (`order_id`) والمنتج المطلوب (`product_id`).
* **الأرشفة المالية والتاريخية (Historical Data Snapshot):** 
  * تخزين اسم المنتج (`product_name`) وسعر الوحدة وقت الشراء (`unit_price`) لحماية الفاتورة من أي تغيرات مستقبلية قد تطرأ على جدول المنتجات الأساسي (مثل تعديل الأسعار أو حذف المنتجات).
  * حفظ الكمية المطلوبة (`quantity`) والمجموع الجزئي للعر (`subtotal`).

---

## ⚙️ تهيئة قاعدة البيانات والتوصيل (`init_db & Engine`)
* **محرك الاتصال غير المتزامن (`create_async_engine`):** ربط التطبيق بقاعدة بيانات SQLite محددة (`shop.db`) باستخدام مكتبة `aiosqlite` للعمل بشكل غير متزامن (`Async`).
* **المعاملات الآمنة (`engine.begin`):** استخدام `begin()` لضمان التراجع التلقائي (`Rollback`) عن عمليات الإنشاء في حال حدوث أي خطأ طارئ لحماية سلامة قاعدة البيانات.
* **إنشاء الجداول (`run_sync`):** تنفيذ عملية إنشاء الجداول دفعة واحدة في الخلفية عبر `SQLModel.metadata.create_all` لتجنب إبطاء عمل السيرفر.
---


## 🔐 نظام المصادقة والحسابات (Authentication & Authorization)

يحتوي النظام على وحدة متكاملة لإدارة الحسابات وتوليد التوكنات الأمنية والتأكد من الصلاحيات.

### 1. نماذج التحقق (Pydantic Schemas)

* **`CheckingInputInformation`**: التحقق من بيانات التسجيل عند إنشاء حساب جديد.
  * **الاسم والسن:** مطابقة القيود الأساسية.
  * **كلمة المرور:** استخدام `field_validator` للتأكد من قوة كلمة السر (تتكون من 8 إلى 16 خانة، وتحتوي على أرقام، رموز، وحروف كبيرة).
  * **البريد الإلكتروني:** استخدام `field_validator` مع Regex للتحقق من صحة صيغة البريد.
* **`Recording`**: استقبال بيانات تسجيل الدخول (`email`, `password`).
* **`CheckingTheOutput`**: نموذج الاستجابة الهيكلية المخصصة لإرجاع التوكن (`token: str`).

---

### 2. نقاط الاتصال (API Endpoints)

**المسار الأساسي:** `/api/v1` | **الوسم (Tag):** `Recording`

#### ➕ إنشاء حساب جديد (`POST /create_account`)
1. **التحقق من التكرار:** يفحص البريد الإلكتروني عبر دالة `no_user_available` لضمان عدم وجود حساب سابق.
2. **التشفير:** تشفير كلمة السر باستخدام خوارزمية التشفير `password_encryption`.
3. **الحفظ:** إدراج بيانات المستخدم الجديدة في قاعدة البيانات عبر دالة `insort`.
4. **التوكن:** إنتاج توكن الوصول وإرجاعه للمستخدم فور التنسيق.

#### 🔑 تسجيل الدخول (`POST /recording`)
1. **التحقق من الحساب:** البحث عن البريد الإلكتروني وكلمة السر المشفرة عبر `select_user`.
2. **مطابقة التشفير:** فحص مطابقة كلمة السر المدخلة مع الهاش المخزن باستخدام `check_password_match`.
3. **جلب البيانات:** استخراج المعرف الخاص بالمستخدم `id_user`.
4. **إرجاع التوكن:** توليد توكن JWT جديد وإرجاعه في الاستجابة.

---

### 3. نظام التوكن والصلاحيات (Token Engine & Dependencies)

* **`token_creation(payload)`**: بناء وتشفير التوكن المعتمد على خوارزمية `HS256` مع تحديد وقت انتهاء الصلاحية (`exp`).
* **`verify_token(...)`**: دالة تحقق شريطة تستخرج التوكن عبر `HTTPBearer` وتقوم بفك تشفيره والتحقق من صحته، مع إدارة استثناءات الانتهاء والتلاعب:
  * `ExpiredSignatureError`: إرجاع كود `401 Token expired`.
  * `InvalidTokenError`: إرجاع خطأ أمني وتحذيري في الـ Logs.
* **`verify_admin_token(...)`**: دالة حماية برمجية (Dependency) تفحص صلاحيات المستخدم من قاعدة البيانات للتحقق من امتلاكه صلاحية `ADMIN` قبل السماح له بالوصول للمسارات المحمية (تُرجع `403 Forbidden` عند عدم الامتلاك).


---

## 📌 دليل شرح ملفات إدارة دورة حياة وحساب المستخدم (الملف الشخصي، الصور، الأمان)

---

### 🖼️ 1. مسارات ومعالجة صور المستخدمين (`users` & `image_file` & `delete_image`)
تعتمد على معالجة الصور محلياً وضغطها لتوفير مساحة التخزين عبر فئات مخصصة:
* **رفع وصورة البروفايل (`/profile/image`):** تستقبل الملف عبر `UploadFile` وتتحقق من صحته ونوعه عبر `ImagesProcessing`، ثم تضغط الصورة بأبعاد `800x800` وجودة `85` لتقليل المساحة، وتحفظها في مجلد `uploads/users` مع اسم فريد `UUID`.
* **حذف واستبدال الصورة:** عند رفع صورة جديدة، يتم جلب اسم الصورة القديمة من قاعدة البيانات وحذفها نهائياً من القرص الصلب باستخدام مكتبة `Pathlib` ودالة `delete_images_user` لتفادي تراكم الملفات المهملة.
* **حذف صورة البروفايل (`DELETE /profile/image`):** تزيل مسار الصورة من جدول المستخدمين وتحذف الملف الفعلي من التخزين المحلي.

---

### 👤 2. مسارات عرض وتحديث بيانات الحساب (`/name`, `/profile/me`)
* **عرض الملف الشخصي (`GET /profile/me`):** تجلب بيانات المستخدم باستخدام الـ `id` المستخرج من التوكن، وتجهز رابط الصورة المرن عبر `request.url_for` مع إخفاء حالة الحساب الافتراضية (`User`).
* **تحديث الاسم (`PUT /name`):** تستقبل الاسم الجديد ضمن موديل `UpdateName` وتحدثه في قاعدة البيانات عبر دالة `name_change_database`.

---

### 🔐 3. مسارات الأمان وتغيير كلمات المرور والبريد (`/password`, `/email`, `/account`)
* **تحديث كلمة المرور (`PUT /password`):** 
  1. التحقق من قوة كلمة المرور الجديدة عبر `field_validator` للتأكد من احتوائها على الحد الأدنى من الأرقام، الرموز، والحروف الكبيرة.
  2. التحقق من تطابق كلمة المرور الحالية المدخلة مع الـ Hash المخزن عبر `check_password_match`.
  3. تشفير كلمة المرور الجديدة وتحديثها في قاعدة البيانات.
* **تحديث البريد الإلكتروني (`PUT /email`):** التحقق من صحة صيغة البريد الجديد بـ `Regex`، التأكد من عدم استخدامه مسبقاً، وتثبيته بعد مطابقة كلمة المرور الحالية للمستخدم.
* **حذف الحساب نهائياً (`DELETE /account`):** تتطلب إدخال كلمة المرور للتأكيد، ثم تقوم بحذف سجل المستخدم بالكامل من قاعدة البيانات وإزالة صورة الملف الشخصي المرتبطة به من الخادم.
---

## 📌 دليل شرح مسارات وإدارة منتجات لوحة التحكم (Products Admin Panel)

---

### 📦 1. مسار إضافة منتج جديد (`POST /product`)
* **تجهيز وتطهير البيانات (`get_product_data`):** تُستخدم لاستقبال بيانات المدخلات عبر `Form` وتمريرها إلى `distance_cleaner` لتنظيفها وتهئيتها قبل حفظها في كلاس موديل `ProductInputs`.
* **التحقق ورفع الصور المتعددة:** يستقبل المسار حتى 4 صور (`file1` إلى `file4`)، ويشترط إرفاق الصورة الأساسية الأولى على الأقل، بينما الباقي اختياري.
* **المعالجة والتخزين:** تمرير الصور عبر كلاس `ImagesProcessing` للتحقق من نوعها وحجمها، ثم ضغطها بأبعاد `800x800` وجودة `85` وحفظها في مجلد `uploads/products` بأسماء `UUID` فريدة.
* **تخزين قاعدة البيانات وعرض الروابط:** حفظ بيانات المنتج عبر `adding_products_database`، ثم توليد روابط وصول مرنة لعرض الصور عبر `request.url_for` باستخدام تقنية تحويل الكائنات (`model_validate` مع `from_attributes = True`).

---

### ✏️ 2. مسار تحديث المنتجات الجزئي (`PATCH /product/{product_id}`)
* **تعديل مرن للبيانات:** يعتمد على نموذج `ProductUpdate` الذي يحتوي على حقول اختيارية (`None`) لتحديث الحقول المُرسلة فقط.
* **تفريغ البيانات:** استخدام `model_dump(exclude_none=True)` لاستبعاد القيم الفارغة، ثم تمريرها إلى دالة القاعدة `product_update_database` التي تستخدم `setattr` لتحديث الأعمدة المطلوبة ديناميكياً بناءً على معرف المنتج (`product_id`).

---

### 🔍 3. مسار عرض المنتجات غير النشطة والمنتهية (`GET /products/inactive`)
* **التقسيم والتخطي (Pagination):** يدعم معاملات الاستعلام `limit` و `offset` للتحكم في عدد العناصر المعروضة لكل دفعة.
* **الاستعلام الشرطي المتقدم:** يتم حساب العدد الإجمالي للمنتجات وتصفيتها في قاعدة البيانات باستخدام `func.count` مع شرط `or_` (المنتجات غير النشطة `is_active == False` أو التي نفذ مخزونها `quantity == 0`).
* **ترتيب النتائج:** جلب المنتجات مرتبة تنازلياً من الأحدث إلى الأقدم باستخدام `order_by(Products.id.desc())` وتجهيز صورها وروابطها للعرض.

---

### 🗑️ 4. مسار حذف المنتج (`DELETE /product/{product_id}`)
* **الحذف من قاعدة البيانات:** استدعاء `product_delete_database` للبحث عن المنتج وحذفه نهائياً من قاعدة البيانات مع إرجاع كائن المنتج المحذوف للوصول إلى أسماء صوره المرتبطة.
* **تنظيف التخزين المحلي:** التكرار عبر صور المنتج الأربع واستخدام مكتبة `Pathlib` ودالة `delete_images_product` لحذف الملفات الفعلية من القرص الصلب لمنع تراكم الملفات المهملة.
  
---

## 📌 دليل شرح نظام مسارات المتجر العامة وعمليات سلة التسوق والشراء (General & E-commerce Endpoints)

---

### 👁️ 1. عرض تفاصيل صفحة المنتج (`GET /product/page/{product_id}`)
* **جلب بيانات المنتج:** استدعاء دالة قاعدة البيانات `product_page_view_database` للبحث عن المنتج عبر معرّفه (`product_id`) وإرجاعه أو إطلاق خطأ `404` إذا لم يكن موجوداً.
* **تجهيز روابط الصور:** تكرار فحص حقول صور المنتج الأربعة وتوليد روابط وصول ديناميكية لها باستخدام `request.url_for`.
* **التحقق وتحويل النموذج:** استخدام `model_validate` مع تفعيل خاصية `from_attributes = True` لدمج كائن قاعدة البيانات مع نموذج `ProductPageViewDatabase` وعرض النتيجة.

---

### 🔍 2. البحث عن المنتجات والتصفح العام (`GET /product/search` & `GET /products`)
* **بحث مرن ومتطور (`ilike`):** في مسار البحث، يتم استخدام دالة `or_` مع `ilike` للبحث المتزامن في الأسماء، الأصناف، والشركات المصنعة مع تجاهل حالة الأحرف.
* **التقسيم والتخطي (Pagination):** دعم معاملات `limit` و `offset` لتنظيم عرض المنتجات في دفعات وعرض إجمالي النتائج (`total_Products` أو `total_products`) للمستخدم والواجهة الأمامية.
* **التحقق من حالة المخزون:** عرض المنتجات النشطة فقط والتي تمتلك مخزوناً أكبر من الصفر (`is_active == True` و `quantity != 0`) وترتيبها تنازلياً من الأحدث إلى الأقدم عبر `order_by(Products.id.desc())`.

---

### 🛒 3. إدارة سلة التسوق (`Basket Operations`)
* **إضافة منتج للسلة (`POST /products/basket/{product_id}`):** التحقق من وجود المنتج وحالته النشطة وتوفر الكمية المطلوبة في المخزون، ثم إضافته أو تحديث كميته باستخدام جدول `ShoppingCarts`.
* **عرض محتويات السلة (`GET /products/basket`):** جلب المنتجات المرتبطة بسلة المستخدم الحالي باستخدام `join` بين جدول السلة وجدول المنتجات، وحساب السعر الإجمالي لكل عنصر بناءً على الكمية.
* **تعديل وحذف المنتجات من السلة (`PUT / Delete`):** إمكانية تحديث الكميات المطلوبة أو حذف منتجات محددة من السلة مع التحقق من توفر المخزون وصلاحيات المستخدم عبر `verify_token`.

---

### 💳 4. إتمام عملية الشراء والفواتير (`Orders & Invoices`)
* **إتمام الطلب (`POST /order`):** 
  * إنشاء سجل طلب جديد (`Orders`) واستخدام `flush` للحصول على معرف الطلب دون الحفظ النهائي المبكر.
  * استخدام خوارزمية **Hash Table** عبر القواميس (`product_dict`) لمطابقة منتجات السلة مع جدول المنتجات بكفاءة عالية وبدون الحاجة لعمليات تكرار ثنائية مكلفة.
* **الحماية من سباق المخزون (Inventory Race Condition):** استخدام التحديث الذري (`update` مع شروط صارمة على الكمية والحالة) لضمان عدم حدوث بيع وهمي لوزعت الكميات أو نفذت أثناء الطلب، مع إرجاع الجلسة (`rollback`) في حال حدوث أي خطأ.
* **إدارة الفواتير وإلغاؤها (`GET / DELETE /order`):** إتاحة عرض قائمة فواتير الشراء السابقة الخاصة بالمستخدم مع تفاصيلها، وإمكانية إلغاء طلب الشراء عبر `cancel_order`.
* ### ⏱️ 1. التحقق من المدة الزمنية للإلغاء (24-Hour Window)
* **معالجة التوقيت العالمي (`timezone.utc`):** ضبط وقت إنشاء الطلب (`order.time_add`) ليتوافق مع التوقيت العالمي الموحد.
* **الشرط الزمني الصارم:** التحقق من أن الفرق بين الوقت الحالي ووقت إنشاء الطلب لا يتجاوز 24 ساعة (`timedelta(hours=24)`). إذا انقضت المدة، يتم إطلاق خطأ `HTTPException(422)` لمنع إلغاء الطلب بعد فوات الأوان.

---

### 📦 2. جلب وتحديث عناصر الطلب والمخزون (`Restoring Quantities`)
* **استعلام عناصر الفاتورة:** جلب جميع العناصر المرتبطة برقم الطلب (`order_id`) من جدول `OrdersItems` والتأكد من وجودها.
* **الاسترجاع الذكي للمخزون (Hash Table & Bulk Lookup):** جمع معرفات المنتجات واستخراجها دفعة واحدة باستخدام `in_` ثم تخزينها في قاموس (`product_dict`) لتحديث كميات المخزون بسرعة وكفاءة عالية.
* **إعادة الكميات وإلغاء الطلب:** إضافة الكميات المباعة مجدداً إلى مخزون المنتجات (`product.quantity += item.quantity`)، ثم حذف عناصر الطلب (`item`) وسجل الطلب الرئيسي (`order`) نهائياً من قاعدة البيانات وإتمام العملية بنجاح عبر `session.commit()`.
---

# 🧪 شرح ملف اختبارات النظام (Pytest & FastAPI TestClient)

---

## 🛠️ 1. الإعدادات العامة والأدوات (`Setup & Imports`)
* **أداة المحاكاة (`TestClient`):** إنشاء كائن اختبار `testing` للتعامل مع مسارات التطبيق (`FastAPI`) وإرسال الطلبات واستقبال الاستجابات (`Response`) بشكل وهمي سريع ودون الحاجة لتشغيل سيرفر فعلي.
* **إدارة الذاكرة المؤقتة للصور (`io.BytesIO & Pillow`):** استخدام مكتبة `PIL` لتوليد صورة وهمية بالأبعاد والألوان المطلوبة، وحفظها مؤقتاً داخل الذاكرة العشوائية (`RAM`) عبر `io.BytesIO` لتوفير الأداء العالي وتجنب الحفظ المؤقت على القرص الصلب.

---

## 👤 2. اختبارات المصادقة والمستخدمين (`Auth & User Tests`)
* **إنشاء الحساب (`test_code_creation`):** إرسال طلب تجريبي لإنشاء حساب مستخدم جديد، ثم تحديث صلاحياته في قاعدة البيانات مباشرة ليصبح مشرفاً (`admin`) لأغراض اختبار المنتجات.
* **تسجيل الدخول واستخراج التوكن (`test_code_recording & auth_token`):** دالة فيكسشر (`@pytest.fixture`) مسؤولة عن إرسال بيانات الاعتماد واستخراج توكن المصادقة (`JWT Token`) لاستخدامه تلقائياً في باقي مسارات الاختبار المحمية.
* **إدارة الصور الشخصية (`test_add_user_image & test_delete_image`):** اختبار رفع صورة بروفايل وهمية من الرام عبر تمريرها بـ `files`، ثم اختبار مسار حذف الصورة الشخصية بنجاح.
* **حذف الحساب (`test_delete_user`):** اختبار إرسال كلمة المرور مع توكن المصادقة لحذف حساب المستخدم نهائياً.

---

## 🛍️ 3. دورة حياة المنتج، السلة، والشراء (`Product & Cart Lifecycle Test`)
* **إضافة منتج جديد (`Admin Product`):** إنشاء صورة وهمية للأداة وتمرير بيانات المنتج النصية والملف عبر `data` و `files` بصلاحيات المشرف، مع التحقق من نجاح العملية واستخراج معرف المنتج (`product_id`).
* **إضافة للسلة والطلب (`Basket & Order`):** اختبار إضافة المنتج إلى سلة التسوق للمستخدم، ثم إتمام عملية الشراء (`Order`) والحصول على رقم الفاتورة (`invoice_id`).
* **إلغاء الطلب وحذف المنتج (`Cleanup & Rollback`):** اختبار مسار إلغاء عملية الشراء واسترجاع المخزون، يليه اختبار مسار حذف المنتج نهائياً من جدول المنتجات عبر صلاحيات المشرف.