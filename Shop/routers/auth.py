from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from routers.database.database_auth import no_user_available, insort, id_user, select_user
from password_encryption import password_encryption, check_password_match
from routers.token.token_generation import token_creation
import re
import string
from logging_info import log_message
router = APIRouter(prefix="/api/v1", tags=["Recording"])

class CheckingInputInformation(BaseModel): # كلاس يرث من البايدانتك لتحقق من المدخلات و تجنب المدخلات الخبيثة
    name: str # مطلوب هنا ادخال اسم
    age: int # العمر
    password: str = Field(min_length=8, max_length=16) # ادخل كلمة سر قوية يتكون طولها على الأقل من 8 إلى 16 حرف
    email: str # ادخال البريد الألكتروني

    @field_validator("password") # نستدخم هذا الدوكريتر للتحقق من مدخلات كلمة السر في بداية تسشغيل السيرفر و ارسال له المدخلات فا لو طابقة المدخلات الشروط داخل الدالة يتم تمريرها لدالة المسار و لو لم تطابق يتم أقاف البرنامج قبل وصول البيانات التالفة للكود ادناه
    @classmethod # نستخدم هذا الديكريتر لجعل الدالة في الأسفل قادرة على الوصول لمثد او المكونات الأخرى للكلاس
    def _check_password(cls, v: str): # داخلها password وتحديد تغير   @field_validator كا برامتر للتحقق من الشروط الموجودة في الدالة يتم تمريره تلفائي عند استعمال password يتم تمرير المتغير 
        #ننشاء قاموس لعد تكرار ظهور الأرقام و الرموز و الحروف داخل كلمة السر و بناء على ذالك نقرر اذا كانت قوية او مناسبة
        repeat = {
            "numbers": 0,
            "symbols": 0,
            "letters": 0
        }
        # الذي يحتوي كلمة السر v نقوم بعمل لوب على متغير 
        for value_password in v:
            if value_password in string.digits: # نتحق لو كان النص الذي نمسك به الأن رقم نزيد واحد للأرقام في القاموس
                repeat["numbers"] += 1
            elif value_password in string.ascii_uppercase: # نتحقق لو كان الذي نمسك به الأن حرف كبير نزيد بمقدام واحد للحروف في القاموس
                repeat["letters"] += 1
            elif value_password in string.punctuation: # نتحقق لو كان الذي نمسك به الأن رمز نزيد بمقدار واحد للرموز داخل القاموس
                repeat["symbols"] += 1
            else: # وإلا لو الذي نمسك به الأن ليس رمز ولا رقم ولا حرف نرفض كلمة السر و نقول انها ضعيفة
                raise ValueError("كلمة سر ضعيفة يسمح فقط بحروف كبيرة ورموز وأرقام مثال(P6884$59)")
        # التحقق من المكونات المتوفرة في كلمة السر على الأقل يجب ان تكون مكونة من 6 أرقام و 1 رمز و1 حروف اذا اقل ترجعل له خطاء
        if repeat["numbers"] < 6 or repeat["symbols"] < 1 or repeat["letters"] < 1: 
            raise ValueError("كلمة سر ضعيفة يسمح فقط الحد الأدنى 6 أرقام و حرف واحد كبير على الأقل و رمز واحد خاص ")
        return v # post أرجاع كلمة السر بعد التحقق من صحتها لدالة المسار 

    @field_validator("email") # نستدخم هذا الدوكريتر للتحقق من مدخلات البريد الالكتروني في بداية تسشغيل السيرفر و ارسال له المدخلات فا لو طابقة المدخلات الشروط داخل الدالة يتم تمريرها لدالة المسار و لو لم تطابق يتم أقاف البرنامج قبل وصول البيانات التالفة للكود ادناه
    @classmethod # نستخدم هذا الديكريتر لجعل الدالة في الأسفل قادرة على الوصول لمثد او المكونات الأخرى للكلاس
    def _check_email_address(cls, email: str): # داخلها email وتحديد تغير   @field_validator كا برامتر للتحقق من الشروط الموجودة في الدالة يتم تمريره تلفائي عند استعمال email يتم تمرير المتغير 
        # للتحقق من صحة البريد الألكتروني regexنكتب أستعلام 
        value = re.fullmatch("^[A-Za-z0-9\.\_\.\+]+\@[A-Za-z0-9]+\.[A-Za-z\.]+$", email)
        if not value:  # يعني انه هذا ليس بريد ألكتروني صحيح فاب تالي ارجع له خطأ False رجع  fullmatch لو مثد التحقق 
            raise ValueError("البريد الإلكتروني غير صالح")
        return email  # post أرجاع البريد الألكتروني بعد التحقق من صحتها لدالة المسار 

class CheckingTheOutput(BaseModel): # message كلاس يرث من بايدانتك للتحقق من المخرجات تم تعريف داخله متغير المخرجات 
    token: str
    
    #message: str # يقبل نص 
@router.post("/create_account", responses={200: {"model": CheckingTheOutput, "description": "تم حصولك على التوكن"}}) # مسار أنشاء حساب 
async def recording_interface(entries: CheckingInputInformation): #  على انها كائن entries ننمرر لدالة المسار كلاس الذي يحتوي متغيرات المطلوب ادخالها قيمها من المستخدم نتحقق منها ثما نمرر لل
    """
    تستعمل دالة المسار هذه لأنشاء حساب
    """
    if not await no_user_available(entries.email): # نتحقق ان البريد الألكتروني الذي تم أدخاله لم يتم استعماله مسبقاً
        log_message("محاولة انشاء حساب بستخدام بريد ألكتروني موجود مسبقاً", "WARNING") 
        raise HTTPException(409, "البريد الألكتروني مستعمل سابقاً")
    # Logging تمرير تمرير رسالة توضح الخطأ لدالة التسجيل في ملف 

    password_hash = password_encryption(entries.password) # نمرر كلمة السر للخوارزمية لتشفيرها و أرجاع التشفير
    # نمرر جميع بيانات المستخدم تشفير كلمة السر البريد الألكتروني و الأسم و العمر لدالة التي وظيفتها اظافة هذه المعلومات في جدول البيانات الخاص في المستخدمين
    await insort(name=entries.name, age=entries.age, email=entries.email, password=password_hash)
    id = await id_user(entries.email) # اتمريره لأنشاء توكن له id  نستعمل البرمجة الغير متزامنة لأرجاع 
    if not id:
        log_message("مستخدم بستخدام بريد ألكتروني غير موجود id محاولة الوصول ل ", "WARNING")
        raise HTTPException(401, "لايوجد حساب بهذا البريد")

    token = token_creation(id) # دالة أنشاء توكن
    return CheckingTheOutput(token=token) # نرجع لدالة التحقق من المخرجات رسالة نصيت للتحقق منها و اظهارها للمستخدم تعني انه تم أنشاء حسابك

class Recording(BaseModel): # للتحقق من المدخلات BaseModel أنشاء الكلاس الذي يرث من 
    email: str # يستقبل نص 
    password: str # يستقبل نص

@router.post("/recording", responses={200: {"model": CheckingTheOutput, "description": "تم حصولك على التوكن"}}) # مسار تسجيل الدخول
async def search_account(information: Recording): # على انها كائن information ثما تمريرها بعد التحقق من صحتها لل Recording التحقق من المدخلات المعرفة في كلاس
    """
    تستعمل دالة المسار هذه لتسجيل الدخول بحستب مسجل بالفعل
    """
    user_password = await select_user(information.email) # تمرير البريد الألكتروني لدالة التحقق من وجود هذا البريد داخل جدول بيانات المستخدمين
    if user_password is False:
        log_message("محاولة تسجيل دخول ابستخدام بريد ألكتروني غير موجود", "WARNING")
        raise HTTPException(401, "كلمة السر او البريد الألكتروني غير صحيح")
    value = check_password_match(information.password, user_password) # تمرير كلمة السر التي تم تشفيرها و كلمة السر التي ادخلها لخوارزمية التشفير لتشفر كلمة السر التي ادخلها ثما تتحقق من تطاق التشفير القديم مع التشفير الحالي لو تطابقا نسمح بدخول الحساب
    if not value:
        log_message("محاولة تسجيل دخول بستخدام كلمة سر غير صحيحة", "WARNING")
        raise HTTPException(401, "كلمة السر او البريد الألكتروني غير صحيح")
    
    id = await id_user(information.email)
    if not id:
        log_message("مستخدم بستخدام بريد ألكتروني غير موجود id محاولة الوصول ل ", "WARNING")
        raise HTTPException(401, "كلمة السر او البريد الألكتروني غير صحيحة")
    token = token_creation(id)
    return CheckingTheOutput(token=token)

