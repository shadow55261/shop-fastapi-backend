from fastapi import Form, Depends, File, Query, UploadFile, Request, HTTPException
from pydantic import BaseModel 
from data_cleaning import distance_cleaner
from routers.token.token_generation import verify_admin_token
from fastapi import APIRouter
from image_file import ImagesProcessing
from routers.database.database_products import adding_products_database, product_update_database, product_delete_database, display_inactive_products_database
from logging_info import log_message
from delete_image import delete_images_product
from datetime import datetime
router = APIRouter(prefix="/api/v1/admin", tags=["Products"])
class Message(BaseModel):
    message: str
class ProductInputs(BaseModel):
    name: str # اسم المنتج 
    description: str # وصف المنتج
    price: float # سعر المنتج
    quantity: int # الكمية المتوفرة من المنتج
    category: str # صنف المنتج مثال سياراة ازياء اجهزة كهربائية
    admin_id: str|None = None # أسم الأدمن او المدير الذي أضاف المنتج أختياري
    brand: str | None = None # البرند او الشركة المصنعة أختياري
    discount_price: float | None = None # لو في اي خصومات على المنتج أختياري
    weight: float|None = None # وزن المنتج اختياري
    size: str|None = None # مقاس اختياري لو كان ملابس مثلاً
class ProductAddOutput(BaseModel):
    id: int # معرف المنتج 
    name: str # اسم المنتج 
    description: str # وصف المنتج
    price: float # سعر المنتج
    quantity: int # الكمية المتوفرة من المنتج
    time_add: datetime  #  ارجاع الوقت الذي تم فيه اضافة المنتج
    is_active: bool  # حالة المنتج أذ كان متوفر يكون صح و اذ كان نفذ يكون خطاء
    category: str # صنف المنتج مثال سياراة ازياء اجهزة كهربائية
    images: list[str] = [] 
    admin_id: str|None # أسم الأدمن او المدير الذي أضاف المنتج أختياري
    brand: str|None  # البرند او الشركة المصنعة أختياري
    discount_price: float|None # لو في اي خصومات على المنتج أختياري
    weight: float|None # وزن المنتج اختياري
    size: str|None  # مقاس اختياري لو كان ملابس مثلاً
    class Config:
        from_attributes = True 
def get_product_data(
    name: str = Form(...), # اسم المنتج 
    description: str = Form(...), # وصف المنتج
    price: float = Form(...), # سعر المنتج
    quantity: int = Form(...), # الكمية المتوفرة من المنتج
    category: str = Form(...), # صنف المنتج مثال سياراة ازياء اجهزة كهربائية
    admin_id: str|None = Form(None), # أسم الأدمن او المدير الذي أضاف المنتج أختياري
    brand: str | None = Form(None), # البرند او الشركة المصنعة أختياري
    discount_price: float | None = Form(None), # لو في اي خصومات على المنتج أختياري
    weight: float|None = Form(None), # وزن المنتج اختياري
    size:  str|None = Form(None) 
    ): # مقاس اختياري لو كان ملابس مثلاً
    return ProductInputs(
       name=distance_cleaner(name), 
        description=distance_cleaner(description),
        price=price,
        quantity=quantity,
        category=distance_cleaner(category),
        admin_id=distance_cleaner(admin_id),
        brand=distance_cleaner(brand),
        discount_price=distance_cleaner(discount_price),
        weight=distance_cleaner(weight),
        size=distance_cleaner(size)
    )
@router.post("/product", responses={200: {"model": ProductAddOutput, "description": "تم اضافة منتج بنجاح"}})
# File() يعمل كا معرف للسيرفر ان القادم ملف و ليس نص عادي
# هو كائن ذكي للتعامل مع الملفات UploadFile  يعمل كا مستقبل للملف يتخرج معلوماته مثل اسمه او حجمه
# Stream و النصوص تذهب للبايدانتك ولا تستطيع الوصول لها بهذه الحالة سواء من هذه الكائنات و اذا لم تمررها لهذه الكائنات تستطيع الوصول لها لمرة واحدة من  UploadFile و اذا ارت استخدامها تستخدم لمرة واحدة فقط اما تسحب لتذهب بالملفات لل Stream بختصار البيانات مثل جوسن و الملفات تعبر من الماسورة المسما Stream هو لايملك البيانات التي يدخلها المستخدم هو فقط يملك البيانات الخام ولاكن يستطيع قراءة البيانات التي يدخلها المستخدم من المخزن المسمى  Request او البيانات التي يدخلها المستخدم ال  body يعني ال  Stream هو يحتوي المعلومات الوصيفة مثل الدومين كما قلنا انما المعلومات التي يدخلها المستخدم لا يملكها ولاكن يمكنه الوصول لها وقرأتها من المخزن بتاعها  Request ولديه أمكانية الوصول للتوكن يعني بختصار ال Domain و عنوان السيرفرPort و المنفذ HTTPS او HTTP هو كائن ذكي للتعامل مع البيانات الخام القادمة مع الطلب فا هي تستقبل بنات مع الطلب القادم مثل البروتوكول  Request ال 
async def add_product(
    request: Request,
    file1: UploadFile  = File(),
    file2: UploadFile|None = File(None), 
    file3: UploadFile|None = File(None), 
    file4: UploadFile|None = File(None), 
    id = Depends(verify_admin_token),
    product_data: ProductInputs = Depends(get_product_data)
    ):
    """
    تستعمل دالة المسار هذه لأضافة منتج للموقع وهي متاحة فقط للأدمن او المدير
    
    """
    if not file1 or not file1.filename:
        log_message("محاولة ارفاق ملف فارغ كا صورة منتج", "INFO")
        raise HTTPException(400, "يجب ارفاق صورة ")
    
    product_images = ImagesProcessing()
    image_route1 = await product_images.validation_product_images(file1)
    image_route2 = await product_images.validation_product_images(file2)
    image_route3 = await product_images.validation_product_images(file3)
    image_route4 = await product_images.validation_product_images(file4)



    product = await adding_products_database( 
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        quantity=product_data.quantity,
        category=product_data.category,
        admin_id=product_data.admin_id,
        brand=product_data.brand,
        discount_price=product_data.discount_price,
        weight=product_data.weight,
        size=product_data.size,
        image_route1= image_route1,
        image_route2=image_route2,
        image_route3=image_route3,
        image_route4=image_route4

    )
    list_image_url = []
    for i in range(1, 5):
        image_route = getattr(product, f"image_route{i}")
        if image_route:
            list_image_url.append(str(request.url_for("static", path=f"products/{image_route}")))

    product_schema = ProductAddOutput.model_validate(product) # اعطاء الصلاحيات للتنفيذ from_attributes = True امر تفيذ التقنية و هذا  model_validate هي تعطي الصلاحيات لقول انا اسمح لك بدخول للكائن القادم من قاعد البينات و استخلاص القيم المطلوبة في كلاس البادانتك من كائن القاعدة فا عنما يجد ما يبحث يطابق البيانات المكتوبة داخل كلاس البايدانتك يعني بختصار هذا  from_attributes = True هذا امر التفيذ الفعلي الذي شرحناه في كلاس البادانتك و قلنا انه 
    product_schema.images = list_image_url
    return product_schema

class ProductUpdate(BaseModel):
    name: str|None = None # اسم المنتج 
    description: str|None = None # وصف المنتج
    price: float|None = None# سعر المنتج
    quantity: int|None = None # الكمية المتوفرة من المنتج
    category: str|None = None# صنف المنتج مثال سياراة ازياء اجهزة كهربائية
    is_active: bool|None = None # تغير حالة المنتج لغير نش بحالة انتها الكمية المتوفرة منه
    admin_id: str|None = None # أسم الأدمن او المدير الذي أضاف المنتج أختياري
    brand: str | None = None # البرند او الشركة المصنعة أختياري
    discount_price: float | None = None # لو في اي خصومات على المنتج أختياري
    weight: float|None = None # وزن المنتج اختياري
    size: str|None = None # مقاس اختياري لو كان ملابس مثلاً

@router.patch("/product/{product_id}", responses={200: {"model": Message, "description": "تم تعديل المنتج بنجاح"}})
async def product_update(product_id: int, product_data: ProductUpdate, id = Depends(verify_admin_token)):
    """
    تستعمل دالة لمسار هذه لتعديل بيانات المنتجات
    """
    dict_product_data = product_data.model_dump(exclude_none=True)
    if not await product_update_database(product_id, dict_product_data):
        log_message("محاولة لتعديل منتج غير موجود", "INFO")
        raise HTTPException(404, "المنتج الذي تحاول تعديله غير موجود")
    
    return Message(message="تم تعديل المنتج بنجاح")
class DisplayInactiveProducts(BaseModel):
    id: int # معرف المنتج 
    name: str # اسم المنتج 
    description: str # وصف المنتج
    price: float # سعر المنتج
    quantity: int # الكمية المتوفرة من المنتج
    time_add: datetime  #  ارجاع الوقت الذي تم فيه اضافة المنتج
    is_active: bool  # حالة المنتج أذ كان متوفر يكون صح و اذ كان نفذ يكون خطاء
    category: str # صنف المنتج مثال سياراة ازياء اجهزة كهربائية
    images: list[str] = [] 
    admin_id: str|None  # أسم الأدمن او المدير الذي أضاف المنتج أختياري
    brand: str|None  # البرند او الشركة المصنعة أختياري
    discount_price: float|None # لو في اي خصومات على المنتج أختياري
    weight: float|None # وزن المنتج اختياري
    size: str|None  # مقاس اختياري لو كان ملابس مثلاً
    class Config:
        from_attributes = True #  وانا اسمح لك بدخول لخصائصه و قرأته يعني هذه الطريقة تريحنا من كتابة القيمة الموجود في ابجكت قاعدة البينات يدوين كالقديم يعني لا داعي ان نمرر القيم يدوي فا هذه تفتح لنا الأذن لهذ
class OfferNotAvailable(BaseModel):
    products: list[DisplayInactiveProducts]
    total_products: int
@router.get("/products/inactive", responses={200: {"model": OfferNotAvailable, "description": "تم عرض المنتجات الغير نشطة و ذات المخزون الفارغ"}})
async def display_inactive_products(
    request: Request,
    limit: int = Query(10, ge=1, le=100, description="عدد المنتجات في الدفعة الواحدة"),
    offset: int = Query(0, ge=0, description="عدد المنتجات المراد تخطيها"),
    id = Depends(verify_admin_token)
):
    """
    تستعمل دالة المسار هذه لعرض للمدير المنتجات الغير نشطة وذات المخزون الفارغ
    """
    result = await display_inactive_products_database(limit, offset)
    Products, total = result
    list_products = []
    for product in Products:
        list_image_url = []
        for i in range(1, 5):
            image_route = getattr(product, f"image_route{i}")
            if image_route:
                list_image_url.append(str(request.url_for("static", path=f"products/{image_route}")))

        product_schema = DisplayInactiveProducts.model_validate(product) # اعطاء الصلاحيات للتنفيذ from_attributes = True امر تفيذ التقنية و هذا  model_validate هي تعطي الصلاحيات لقول انا اسمح لك بدخول للكائن القادم من قاعد البينات و استخلاص القيم المطلوبة في كلاس البادانتك من كائن القاعدة فا عنما يجد ما يبحث يطابق البيانات المكتوبة داخل كلاس البايدانتك يعني بختصار هذا  from_attributes = True هذا امر التفيذ الفعلي الذي شرحناه في كلاس البادانتك و قلنا انه 
        product_schema.images = list_image_url
        list_products.append(product_schema)
    return OfferNotAvailable(products=list_products, total_products=total)

@router.delete("/product/{product_id}", responses={200: {"model": Message, "description": "تم حذف المنتج بنجاح"}})
async def product_delete(product_id: int,  id = Depends(verify_admin_token)):
    """
    تستعمل دالة المسار هذه لحذف منتج 
    """
    delete_images = await product_delete_database(product_id) # نسخرج من القاعدة بعد الحذف الكائن بتاع المنتج لحذف صور المنتج
    if not delete_images:
        log_message("محاولة حذف منتج غير موجود", "INFO")
        raise HTTPException(404, "المنتج الذي تحاول حذفه غير موجود")
    for i in range(1, 5):
        route = getattr(delete_images, f"image_route{i}") # str للصول لأسماء الخصائص التي تحمل صور المنتج نمرر لها الكائن ثما اسم الخاصية كا نص  getattr نستعمل الدالة 
        if route:
            delete_images_product(route) # نمرر لدالة حذف المنتج اسماء الصور في كل عملية لوب للحذف
    return Message(message="تم حذف المنتج بنجاح")
    