from fastapi import File, Depends, UploadFile, APIRouter, Request, HTTPException
from pydantic import BaseModel, HttpUrl, Field, field_validator
from image_file import ImagesProcessing
from routers.token.token_generation import verify_token
from routers.database.database_users import modification_profile_image, delete_images_database, name_change_database, view_user_profile, extraction_password, change_password_user, check_email_address, change_email_address, delete_account_database
from delete_image import delete_images_user
import string
from password_encryption import check_password_match, password_encryption
import re
from logging_info import log_message 
router = APIRouter(prefix="/api/v1/users", tags=["Users"])
class AddImage(BaseModel):
    message: str 
    avatar_url: HttpUrl # قبل ارياله للبايدانتك str لذى يجب علينا تجويله ل  http ليتحقق من صحة الرابط و انه يحمل بروتوكول صحيح مثل  str ان يتم تمريره له على انه  URL يتوقع الرابط من نوع  HttpUrl في الأصدارات الحديثة من بايدانتك ال 
@router.post("/profile/image", responses={200: {"model": AddImage, "description": "تم أضافة صورة بروفايل"}})
async def add_image(request: Request, file: UploadFile = File(), id = Depends(verify_token)):
    """
    تستخدم دالة المسار هذه لأضافة صورة للمستخدم
    """
    if not file or not file.filename:
        log_message("محاولة رفع ملف فارغ", "INFO")
        raise HTTPException(400, "يجب ارفاق صورة ")
    users_images = ImagesProcessing() 
    image_route = await users_images.validation_users_images(file=file) # لمعلجة الصورة و ضغطها و تغير اسمها و حفظها validation_users_images نستعمل دالة 
    if not image_route: # بحالة معالجة ملف فارغ على انه صورة ترجع الخطاء التالي
        log_message("محاولة ضغط ملف فارغ", "INFO")
        raise HTTPException(401, "ملف فارغ")
    value = await modification_profile_image(id, image_route) # نستعمل دالة قاعدة البيانات لنمرر لها الصورة بعد معالجتها لأضافتها لحساب المستخدم في القاعدة
    if value is False: # لو حساب المستخدم غير موجود نرجع له الخطاء التالي
            log_message("قد يكون تم التلاعب في التوكن انتبه ID لم يتم أجاد المستخدم حامل ال", "WARNING")
            HTTPException(404, "المستخدم غير موجود")
    if value is not None:
        if not delete_images_user(value): # لو القيمة الراجعة من القاعدة غير فارغة نحذف الصورة القديمة يلي المستخدم كان حاطها 
            log_message("ملف صور غير موجود", "INFO")
    
    image_url = str(request.url_for("static", path=f"users/{image_route}")) # نرجع رابط الصورة للفرنت إند لعرض  ها للمستخدم
    return AddImage(message="تم أضافة الصورة", avatar_url=image_url)

    
class Message(BaseModel):
    message: str
@router.delete("/profile/image", responses={200: {"model": Message, "description": "تم حذف صورة البروفايل"}})
async def delete_image_profile(id = Depends(verify_token)):
    """
    تستخدم دالة المسار هذه  لحذف صورة البروفايل للمستخدم
    """
    value = await delete_images_database(id) # نمررلدالة القاعدة معرف المستخدم لحذف الصورة من لاقعدة و نستخرج اسم الصورة ونمررها لدالة حذف الصور لنحذفها من التخزين المحلي في ملف الصور
    if value is False: # لو ارجع قيمة خطاء يعني المستخدم غير موجود في القاعدة و نرجع الخطاء التالي
        log_message("قد يكون تم التلاعب في التوكن انتبه ID لم يتم أجاد المستخدم حامل ال", "WARNING")
        raise HTTPException(404, "مستخدم غير موجود")

    if value is None: # لو الراجع من القاعدة قيمة خطاء يعني انه لا يوجد صورة للمستخدم اساساً فا نرجع الخطاء التالي
        log_message("محاولة حذف صورة و المستخدم لا يملك صورة أساساً", "INFO")
        raise HTTPException(404, "الصورة غير موجودة")
    delete_images_user(value) # نمرر اسم الصورة المستخرج من القاعدة لدالة الحذف لحذفها من الجهاز بشكل نهائي
    return Message(message="تم حذف صورة الملف الشخصي")
        
class UpdateName(BaseModel):
    name: str 
@router.put("/name", responses={200: {"model": Message, "description": "تم تعديل اسم المستخدم"}})
async def update_name(name: UpdateName, id = Depends(verify_token)):
    """
    تستخدم دالة المسار هذه  لتعديل اسم المستخدم
    """
    if not await name_change_database(name.name, id): # نمرر للقاعدة معرف المستخدم و اسمه الجديد لو ارجع قيمة خطاء يعني المستخدم غير موجود نرجع الخطاء التالي
        log_message("قد يكون تم التلاعب في التوكن انتبه ID لم يتم أجاد المستخدم حامل ال", "WARNING")
        raise HTTPException(404, "مستخدم غير موجود")
    return Message(message="تم تغير الأسم بنجاح")
class UseProfileMe(BaseModel):
    image: HttpUrl|None
    name: str
    status: str|None
    age: int
    email:str
@router.get("/profile/me", responses={200: {"model": UseProfileMe, "description": "تم عرض الملف الشخصي"}})
async def user_profile_me(request: Request, id = Depends(verify_token)):
    """
    تستخدم دالة المسار هذه لعرض الملف الشخصي للمستخدم
    """
    user_profile = await view_user_profile(id) # نمرر للقاعدة معرف المستخدم المستخرج من التوكن لترجع لنا جميع بيانات المستخدم لعرض ملفه الشخصي عند الطلب
    if not user_profile: # لو ارجعة قيمة فارغة يعني ان المستخدم غير موجود نرجع الخطاء التالي
        log_message("قد يكون تم التلاعب في التوكن انتبه ID لم يتم أجاد المستخدم حامل ال", "WARNING")
        raise HTTPException(404, "مستخدم غير موجود")
    elif user_profile.status == "User": # ولو كان احد الأدارة نعرض حالة مسمى الحساب User نتحقق من حالة الحساب في القاعدة لو كان مستخدم نستبعد عرض كلمة 
        user_profile.status = None
    if user_profile.image:
        image_url = str(request.url_for("static", path=f"users/{user_profile.image}")) # نجهز رابط صورة الملف الشخصي بتاع المستخدم
    else:
        image_url = None
    return UseProfileMe(image=image_url, name=user_profile.name, status=user_profile.status, age=user_profile.age, email=user_profile.email)
        

class UpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=16)
    new_password: str  = Field(min_length=8, max_length=16)
        
    @field_validator("new_password") # نستدخم هذا الدوكريتر للتحقق من مدخلات كلمة السر في بداية تسشغيل السيرفر و ارسال له المدخلات فا لو طابقة المدخلات الشروط داخل الدالة يتم تمريرها لدالة المسار و لو لم تطابق يتم أقاف البرنامج قبل وصول البيانات التالفة للكود ادناه
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

@router.put("/password", responses={200: {"model": Message, "description": "تم تحديث كلمة السر المستخدم"}})
async def update_password(password: UpdatePassword, id = Depends(verify_token)):
        """
        تستعمل هذه الدالة لتغير كلمة سر المستخدم
        """
        password_database = await extraction_password(id) # لجلب كلمة السر الحالية للسمتخدم id دالة نمرر لها ال 
        if not password_database:
            log_message("قد يكون تم التلاعب في التوكن انتبه ID لم يتم أجاد المستخدم حامل ال", "WARNING")
            raise HTTPException(404, "المستخدم غير موجود") # لو متغير ارجع قيمة خطأ او فارغة نرجع رسالة الخطاء المناسبة
        if not check_password_match(password.current_password, password_database): # نمرر كلمة السر المشفرة التي تم استخراجها من قاعدة البيانات و الكلمة التي ادخلها نشفرهم و نطابق التشفير
            log_message("محاولة تغير كلمة السر ولاكن السمتخدم يدخل كلمة السر خطأ", "WARNING")
            raise HTTPException(401, "كلمة سر غير صحيحة") # نرجع خطأ لو ادخل كلمة سر غير متطابقة من الكلمة الحالية للمستخدم
                    
        hash_password = password_encryption(password.new_password) # ولو صح التشفير و تطابقى نمرر كلمة السر الجديدة ليتم تشفيرها و ارجاعها لنا 
        if not await change_password_user(id, hash_password): # نخزن كلمة السر التي تم تشفيرها بدال الكلمة القديمة اي نبدلهم
            log_message("قد يكون تم التلاعب في التوكن انتبه ID لم يتم أجاد المستخدم حامل ال", "WARNING")
            raise HTTPException(404, "المستخدم غير موجود") # ID. نرجع رسالة الخطأ المناسبة لو لم يتم العثور على المستخدم حامل 

        return Message(message="تم تغير كلمة السر بنجاح") # نرجع رسالة تأكيد على تغير كلمة السر بنجاح

class UpdateEmail(BaseModel):
    password: str = Field(min_length=8, max_length=16)
    new_email: str
    
    @field_validator("new_email") # نستدخم هذا الدوكريتر للتحقق من مدخلات البريد الالكتروني في بداية تسشغيل السيرفر و ارسال له المدخلات فا لو طابقة المدخلات الشروط داخل الدالة يتم تمريرها لدالة المسار و لو لم تطابق يتم أقاف البرنامج قبل وصول البيانات التالفة للكود ادناه
    @classmethod # نستخدم هذا الديكريتر لجعل الدالة في الأسفل قادرة على الوصول لمثد او المكونات الأخرى للكلاس
    def _check_email_address(cls, email: str): # داخلها email وتحديد تغير   @field_validator كا برامتر للتحقق من الشروط الموجودة في الدالة يتم تمريره تلفائي عند استعمال email يتم تمرير المتغير 
        # للتحقق من صحة البريد الألكتروني regexنكتب أستعلام 
        value = re.fullmatch("^[A-Za-z0-9\.\_\.\+]+\@[A-Za-z0-9]+\.[A-Za-z\.]+$", email)
        if not value:  # يعني انه هذا ليس بريد ألكتروني صحيح فاب تالي ارجع له خطأ False رجع  fullmatch لو مثد التحقق 
            raise ValueError("البريد الإلكتروني غير صالح")
        return email  # post أرجاع البريد الألكتروني بعد التحقق من صحتها لدالة المسار 

@router.put("/email", responses={200: {"model": Message, "description": "تم تحديث البريد الألكتروني الخاص بالمستخدم بنجاح"}})
async def Update_email(email_address: UpdateEmail, id = Depends(verify_token)):
    """
    تستعمل دالة المسار هذه لتغير البيرد الألكتروني للمستخدم
    """
    password_database = await extraction_password(id) # نستعمل دالة القاعدة هذه لستخراج كلمة سر المستخدم من القاعدة
    if not password_database: # لو ارجعة قيمة فرغة يعني انه لم يتم أجاد المستخدم نرجع له الخطاء التالي
        log_message("قد يكون تم التلاعب في التوكن انتبه ID لم يتم أجاد المستخدم حامل ال", "WARNING")
        raise HTTPException(404, "المستخدم غير موجود")
    if not check_password_match(email_address.password, password_database): # نمرر لدالة فك التشفير كلمة سر المستخدم المشفرة في القاعدة و الكلمة اليت ادخلها الأن لتشفيرها و مطابقة التشفيران لو لم يتطابقى و ارجع خطاء نرجع الخطاء التالي
        raise HTTPException(401, "كلمة السر غير صحيحة")

    if await check_email_address(email_address.new_email): # نمرر البريد الألكتروني الجديد للقاعدة للتحقق هل هو مستعمل او لا لو مستعمل نرجع الخطاء التالي
        log_message("محاولة تغير بريد الألكتروني لبريد مستعمل مسباً", "WARNING")
        raise HTTPException(409, "البريد الألكتروني مستعمل  بالفعل")
            
    if not await change_email_address(id, email_address.new_email): # نمرر للقاعدة البريد الألكتروني الجديد و معرف المتخدم لتغير بريده من القديم للجديد لو ارجع خطاء يعني لم يجد المستخدم في القاعدة وبتالي نرجع الخطاء التالي
        log_message("قد يكون تم التلاعب في التوكن انتبه ID لم يتم أجاد المستخدم حامل ال", "WARNING")
        raise HTTPException(404, "المستخدم غير موجود")

    return Message(message="تم تغير البريد الألكتروني بنجاح")
   
class DeleteAccount(BaseModel):
    password: str
@router.delete("/account", responses={200: {"model": Message, "description": "تم حذف حساب المستخدم بنجاح"}})
async def delete_account(password: DeleteAccount, id = Depends(verify_token)):
    """
    تستعمل دالة المسار هذه لحذف حساب المستخدم من الموقع بشكل نهائي مع جميع بياناته
    """
    password_database = await extraction_password(id) # نمرر للقاعدة معرف المستخدم لستخراج كلمة السر الخاصة به من لقاعدة
    if not password_database: # لو ارجع قيمة خطاء يعني انه المستخدم غير موجود نرجع الخطاء التالي
        log_message("قد يكون تم التلاعب في التوكن انتبه ID لم يتم أجاد المستخدم حامل ال", "WARNING")
        raise HTTPException(404, "المستخدم غير موجود")
    if not check_password_match(password.password, password_database): # نمرر كلمة السر المشفرة التي استخرجة من القاعدة و معها الكلمة التي ادخلها المستخدم الأن نشفرها و نقارن التشفيران لو ما تطابقى نرجع الخطاء التالي
        log_message("محاولة حذف حساب المستخدم بأدخال كملة سر غير صحيحة", "WARNING")
        raise HTTPException(401, "كلمة السر غير صحيحة")
    image = await delete_account_database(id)
    if image is False: # نمرر لدالة القاعدة معرف المستخدم لحذف حسابه بشكل نهائي مع جميع بياناته بحال ارجع قيمة خطاء يعني المستخدم غير موجود نرجع الخطاء التالي
        log_message("قد يكون تم التلاعب في التوكن انتبه ID لم يتم أجاد المستخدم حامل ال", "WARNING")
        raise HTTPException(404, "المستخدم غير موجود")
    delete_images_user(image)
    return Message(message="تم حذف حسابك بنجاح")







            


        