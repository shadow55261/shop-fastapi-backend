from shop_main import app
from fastapi.testclient import TestClient
from routers.token.token_generation import  token_creation
from PIL import Image
import io # هذه المكتبة مسؤولة عن أدارة تدفق البيانات داخل ذاكرة النظام يلي هو الرام  ودا بدينا امكانيات قوية تخيل لو عندك برنامج محتاج يقرأ بيانات من ملف هو مطر لفتح الملف يلي متخزن على الهارد بكود طويل هذه المكتبة بتخليك تعمل نفس الشيء ولاكن داخل الرام و السبب انه نستعمل الرام عشان بعطيك ميزات اقوى بريحك من اخطاء الهارد ديسك و بمسح الصورة تلقائي بعد الأنتهاء من التجربة انما في الهارد انت محتاج تكتب كود لحذفها بعد وضها و الرام اسرع من الهارد بأضعاف
import pytest
from routers.database.database import Users, engine
from sqlmodel import select, create_engine, Session

engine = create_engine("sqlite:///shop.db")

testing = TestClient(app) # شاملة كل شيء response بدون الحاجة لتشغيل السيرفر الفعلي يقوم بإرسال الطلبات إلى مسارات التطبيق و يستلم النتيجة api هي الوسيط الذي يربط بين كود الأختبار و ال  TestClient ال 
def test_code_creation():
    """
    أختبار أنشاء حساب
    """
    test = testing.post("/api/v1/create_account", json={"name": "shadow", "age": "30", "password": "P123Y456#", "email": "shadow@2.com"})
    assert test.status_code == 200 # هي أداة التحقق الشديد المدمجة بالغة بايثون وتعني حرفياً تأكد ان هذا الشرط صحيح و إلا لو خطاء اوقف التنفيذ و ارجع خطاء و اعتبر انه اختبار فاشل assert ال 
    with Session(engine) as session:
        result = select(Users).where(Users.email == "shadow@2.com")
        user = session.exec(result).first()
        if user:
            user.status = "admin"
            session.add(user)
            session.commit()

        
def test_code_recording():
    """
    أختبار تسجيل الدخول
    """
    test = testing.post("/api/v1/recording", json={"email": "shadow@2.com", "password": "P123Y456#"})
    assert test.status_code == 200
@pytest.fixture
def auth_token():
    """
    أستخراج التوكن من تسجيل الدخول
    """
    test = testing.post("/api/v1/recording", json={"email": "shadow@2.com", "password": "P123Y456#"})
    assert test.status_code == 200
    return test.json()["token"]


def test_full_product_and_cart_lifecycle(auth_token):
    #-----------------------------------------
    # أختبار مسار اضافة منتج
    #-----------------------------------------
    img_byte_arr = io.BytesIO() # تفتح في الرام مكان فارغ للتخزين فيه BytesIO هذه الدالة 
    image = Image.new("RGB", (100, 100), color="red") #  هذه اختصار للثلاثة ألوان الأحمر الأخضر الأزرق و نكتبها لتحديد مود التلوين المتبع يعني هنا اخبره انني سوف استعمل ثلاثة ألوان دول للتلوين او جزء منهم و بعدها باقي الكود نحدد ابعاد الصورة و اللون يلي استعملناه الأحمر للتلوين RGB نجهز شكل الصورة وا تصميمها هنا 
    image.save(img_byte_arr, format="PNG") # نمرر له الأمتداد باتع الصورة ليتم تشفير و عمل بايتات الصورة بناء على الأمتداد داه مع الأعدادالكائن الشكلي الذي انشأناه في الذاكرة format="PNG" الوعاء الذي عملناه في الرام ليحفظ به و هنا img_byte_arr دالة الحفظ بناء على كائن الصورة الذي انشأناه في الذاكرة من شوية ونمرر له image.save هنا نحدد 
    real_png_bytes = img_byte_arr.getvalue() # وظيفتها تستخرج البايتات يلي خزناها في الرام تستخرجها لنا من الرام لنستعملها getvalue و الدالة دي 

    admin_token = {"user_id": 1, "status": "admin"}
    test = testing.post("/api/v1/admin/product", 
        data={
        "name": "منتج تجريبي",
        "description": "منتج تجريبي",
        "price": 100, "quantity": 10,
        "category": "منتج تجريبي"

        }, # form ليرسلها لدالة المسار بتعيتنا للحقول  data نمررها لل  form هو الدالالت على لحقول النصية التي من نوع  data هنا نمرر الحقول النصية مع الملف و ال 
        files={"file1": ("test.png", real_png_bytes, "image/png")}, # الخاص بك في دالة مسار استقبال الصور لنمرر لهذا المتغير الذي يستقبل الصور الصورة بتعيتنا كا فليو تحتوي على تابل يحتوي على اسم الصورة و امتدادها بعدها بايتات الصورة التي جهزناها في الأعلى و اخذناها من الرام و  نوع الملف انه صورة و امتداده api و نمرر له قاموس يحتوي على كي في البايدة لأسم المتغير الذي وضعتها في تطبيق ال  TestClient لأن هذه هي المعتمدة لتمرير الملفات في ال  files و هنا نستعمل 
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert test.status_code == 200
    product_id = test.json()["id"]
    #--------------------------------------------
    # اختبار مسار اضافة  منتج للسلة
    # -------------------------------------------
    test_basket = testing.post(f"/api/v1/general/products/basket/{product_id}", json={"quantity": 10}, headers={"Authorization": f"Bearer {auth_token}"})
    assert test_basket.status_code == 200
    #--------------------------------------------
    # أختبار مسار عملية شراء منتجات
    #--------------------------------------------
    test_order = testing.post("/api/v1/general/order", json={"quantity": 10}, headers={"Authorization": f"Bearer {auth_token}"})
    assert test_order.status_code == 200
    order_id = test_order.json()["invoice_id"]
    #--------------------------------------------
    # اختبار عملية إلغاء عملية الشراء
    #--------------------------------------------
    test_delete_order = testing.request("DELETE", f"/api/v1/general/order/{order_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert test_delete_order.status_code == 200
    #--------------------------------------------
    # أختبار عملية حذف المنتج من جدول المنتجات
    #--------------------------------------------
    test_delete_product = testing.request("DELETE", f"/api/v1/admin/product/{product_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert test_delete_product.status_code == 200

def test_add_user_image(auth_token):
    """
    أختبار مسار أضافة صورة بروفايل
    """
    img_byte_arr = io.BytesIO() # تفتح في الرام مكان فارغ للتخزين فيه BytesIO هذه الدالة 
    image = Image.new("RGB", (100, 100), color="red") #  هذه اختصار للثلاثة ألوان الأحمر الأخضر الأزرق و نكتبها لتحديد مود التلوين المتبع يعني هنا اخبره انني سوف استعمل ثلاثة ألوان دول للتلوين او جزء منهم و بعدها باقي الكود نحدد ابعاد الصورة و اللون يلي استعملناه الأحمر للتلوين RGB نجهز شكل الصورة وا تصميمها هنا 
    image.save(img_byte_arr, format="PNG") # نمرر له الأمتداد باتع الصورة ليتم تشفير و عمل بايتات الصورة بناء على الأمتداد داه مع الأعدادالكائن الشكلي الذي انشأناه في الذاكرة format="PNG" الوعاء الذي عملناه في الرام ليحفظ به و هنا img_byte_arr دالة الحفظ بناء على كائن الصورة الذي انشأناه في الذاكرة من شوية ونمرر له image.save هنا نحدد 
    real_png_bytes = img_byte_arr.getvalue() # وظيفتها تستخرج البايتات يلي خزناها في الرام تستخرجها لنا من الرام لنستعملها getvalue و الدالة دي 
    test_add_image_profile = testing.post("/api/v1/users/profile/image", files=
                        {
                            "file": ("test.png", real_png_bytes, "image/png")

                        },
                        headers={"Authorization": f"Bearer {auth_token}"}
                        )
    assert test_add_image_profile.status_code == 200
def test_delete_image(auth_token):
    """
    أختبار حذف صورة الملف الشخصي
    """
    test_delete_image = testing.request("DELETE", "/api/v1/users/profile/image", headers={"Authorization": f"Bearer {auth_token}"})
    assert test_delete_image.status_code == 200


def test_delete_user(auth_token):
    """
    أختبار مسار حذف حساب مستخدم
    """
    test_delete_account = testing.request("DELETE", "/api/v1/users/account", json={"password": "P123Y456#"},  headers={"Authorization": f"Bearer {auth_token}"})
    assert test_delete_account.status_code == 200