from fastapi import Depends,  Query, Request, HTTPException
from pydantic import BaseModel, Field 
from fastapi import APIRouter
from routers.database.database_general import product_page_view_database, product_search_database, product_show_database, add_products_basket_database, view_basket_products_database, update_quantity_database, delete_product_basket_database, product_buy_database, cancel_order_database, view_invoices_database
from datetime import datetime
from routers.token.token_generation import verify_token
router = APIRouter(prefix="/api/v1/general", tags=["General"])
class Message(BaseModel):
    message: str
class ProductPageViewDatabase(BaseModel):
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
        from_attributes = True #  وانا اسمح لك بدخول لخصائصه و قرأته يعني هذه الطريقة تريحنا من كتابة القيمة الموجود في ابجكت قاعدة البينات يدوين كالقديم يعني لا داعي ان نمرر القيم يدوي فا هذه تفتح لنا الأذن لهذا ORM يا نظام الكائن القادم لك ليس قاموس عادي بالكائن قاعدة بيانات  Pydantic هذه تقنية ذكية تعطي الأذن لتخبر البايدانتك  from_attributes = True ال 
@router.get("/product/page/{product_id}", responses={200: {"model": ProductPageViewDatabase, "description": "تم عرض المنتج بنجاح"}})
async def product_page_view(request: Request, product_id: int):
    """
    تستعمل دالة المسار هذه لعرض صفحة المنتج
    """    
    product = await product_page_view_database(product_id)
    list_image_url = []
    for i in range(1, 5):
        image_route = getattr(product, f"image_route{i}")
        if image_route:
            list_image_url.append(str(request.url_for("static", path=f"products/{image_route}")))

    product_schema = ProductPageViewDatabase.model_validate(product) # اعطاء الصلاحيات للتنفيذ from_attributes = True امر تفيذ التقنية و هذا  model_validate هي تعطي الصلاحيات لقول انا اسمح لك بدخول للكائن القادم من قاعد البينات و استخلاص القيم المطلوبة في كلاس البادانتك من كائن القاعدة فا عنما يجد ما يبحث يطابق البيانات المكتوبة داخل كلاس البايدانتك يعني بختصار هذا  from_attributes = True هذا امر التفيذ الفعلي الذي شرحناه في كلاس البادانتك و قلنا انه 
    product_schema.images = list_image_url
    return product_schema
class ProductSearch(BaseModel):
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
        from_attributes = True #  وانا اسمح لك بدخول لخصائصه و قرأته يعني هذه الطريقة تريحنا من كتابة القيمة الموجود في ابجكت قاعدة البينات يدوين كالقديم يعني لا داعي ان نمرر القيم يدوي فا هذه تفتح لنا الأذن لهذا ORM يا نظام الكائن القادم لك ليس قاموس عادي بالكائن قاعدة بيانات  Pydantic هذه تقنية ذكية تعطي الأذن لتخبر البايدانتك  from_attributes = True ال 
class SearchResult(BaseModel):
    products: list[ProductSearch]
    total_Products: int
@router.get("/product/search", responses={200: {"model": SearchResult, "description": "تم عرض المنتجات بنجاح"}})
async def product_search(
    request: Request,
    query: str|None = Query(None, description="نص البحث عن المنتجات"), # لسببين ممكن المستخدم يدخل البحث ولاكن ما يدخل شيء و بحث قا بتالي لو مافي قيمة افتراضية حيصل خطاء و بتالي قاعدة البيانات عندما تبحث داخلها بستخدام قيمة فارغة هي ذكية هترجع لك اخر المنتجات التي تم اضافتها و لو ادخل كلمة ليبحث بها سوف يرجع له قيم البحث بناء على الكلمة المدخلةquery في  none نع قمية افتراضية 
    limit: int = Query(10, ge=1, le=100, description="عدد المنتجات في الدفعة الواحدة"), # قيمة افتراضبة 10 لنبدأ اول عملية لجب المنتجات عشان بكون الفرنت إند لسه ما ارسل عدد المنتجات التي نعرضها في كل صفحة limit نخزن في 
    offset: int = Query(0, ge=0, description="عدد عدد المنتجات المراد تخطيها"), # قيمة افراضية 0 السبب انه نحن في اول مرة نعرض مش هنتخطى اي منتحات عرضناها سابقاً عشان لسا ما عرضنا شيء بعد في اول دفعة تكون صفر ثما تزيد للتخطى المنجات التي عرضناها في الدفعات السابقة offset نخزن في 
):
    """
    دالة المسار هذه للبحث عن المنتجات و عرضها
    """
    result = await product_search_database(query, limit, offset)
    products, total_product = result
    list_products = []
    for product in  products:
        list_image_url = []
        for i in range(1, 5):
            image_route = getattr(product, f"image_route{i}")
            if image_route:
                list_image_url.append(str(request.url_for("static", path=f"products/{image_route}")))

        product_schema = ProductSearch.model_validate(product) # اعطاء الصلاحيات للتنفيذ from_attributes = True امر تفيذ التقنية و هذا  model_validate هي تعطي الصلاحيات لقول انا اسمح لك بدخول للكائن القادم من قاعد البينات و استخلاص القيم المطلوبة في كلاس البادانتك من كائن القاعدة فا عنما يجد ما يبحث يطابق البيانات المكتوبة داخل كلاس البايدانتك يعني بختصار هذا  from_attributes = True هذا امر التفيذ الفعلي الذي شرحناه في كلاس البادانتك و قلنا انه 
        product_schema.images = list_image_url
        list_products.append(product_schema)
    return SearchResult(products=list_products, total_Products=total_product)


class ProductShow(BaseModel):
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
        from_attributes = True #  وانا اسمح لك بدخول لخصائصه و قرأته يعني هذه الطريقة تريحنا من كتابة القيمة الموجود في ابجكت قاعدة البينات يدوين كالقديم يعني لا داعي ان نمرر القيم يدوي فا هذه تفتح لنا الأذن لهذا ORM يا نظام الكائن القادم لك ليس قاموس عادي بالكائن قاعدة بيانات  Pydantic هذه تقنية ذكية تعطي الأذن لتخبر البايدانتك  from_attributes = True ال 
class ShowResult(BaseModel):
    products: list[ProductShow]
    total_products: int
@router.get("/products", responses={200: {"model": ShowResult, "description": "تم عرض المنتج بنجاح"}})
async def product_show(
    request: Request,
    limit: int = Query(10, ge=1, le=100, descripion="عدد المنتجات في الدفعة الواحدة"),
    offset: int = Query(0, ge=0, description="عدد المنتجات المراد تخطيها")
    ):
    """
    دالة المسار هذه لعرض المنتجات و تصفحها
    """
    results = await product_show_database(limit, offset)
    producs, total_products = results
    list_products = []
    for product in producs:
        list_image_url = []
        for i in range(1, 5):
            image_route = getattr(product, f"image_route{i}")
            if image_route:
                list_image_url.append(str(request.url_for("static", path=f"products/{image_route}")))

        product_schema = ProductShow.model_validate(product) # اعطاء الصلاحيات للتنفيذ from_attributes = True امر تفيذ التقنية و هذا  model_validate هي تعطي الصلاحيات لقول انا اسمح لك بدخول للكائن القادم من قاعد البينات و استخلاص القيم المطلوبة في كلاس البادانتك من كائن القاعدة فا عنما يجد ما يبحث يطابق البيانات المكتوبة داخل كلاس البايدانتك يعني بختصار هذا  from_attributes = True هذا امر التفيذ الفعلي الذي شرحناه في كلاس البادانتك و قلنا انه 
        product_schema.images = list_image_url
        list_products.append(product_schema)
    return ShowResult(products=list_products, total_products=total_products)
class AddProductsBasket(BaseModel):
    quantity: int = Field(1, ge=1)
@router.post("/products/basket/{product_id}", responses={200: {"model": Message, "description": "تم اضافة منتج للسة"}})
async def add_products_basket(quantity: AddProductsBasket, product_id: int, user_id = Depends(verify_token)):
    """
     أضافة منتج للسلة
    """
    await add_products_basket_database(user_id, product_id, quantity.quantity)
    return Message(message="تم اضافة منتج للسلة")
class ViewBasketProducts(BaseModel):
    id_product: int # معرف المنتج 
    id_product_basket: int
    name: str # اسم المنتج 
    price: float # سعر المنتج
    quantity: int # الكمية المتوفرة من المنتج
    time_add_product_basket: datetime  #  ارجاع الوقت الذي تم فيه اضافة المنتج
    images: list[str] = [] 
class FinalOutput(BaseModel):
    products: list[ViewBasketProducts]
    total_products: int
@router.get("/products/basket", responses={200: {"model": FinalOutput, "description": "تم عرض المنتجات التي في السلة"}})
async def view_basket_products(
    request: Request,
    limit: int = Query(10, ge=1, le=100, descripion="عدد المنتجات في الدفعة الواحدة"),
    offset: int = Query(0, ge=0, description="عدد المنتجات المراد تخطيها"),
    user_id = Depends(verify_token)
):
    """
    وظيفة دالة المسار هذه عرض منتجات في السلة
    """
    list_products_basket = []
    result = await view_basket_products_database(user_id, limit, offset)
    products, total_products = result
    for basket, product in products:
        list_image_url = []
        for i in range(1, 5):
            image_route = getattr(product, f"image_route{i}")
            if image_route:
                list_image_url.append(str(request.url_for("static", path=f"products/{image_route}")))

        price = basket.quantity * product.price
        product_schema = ViewBasketProducts(
            id_product=product.id,
            id_product_basket=basket.id,
            name=product.name,
            price=price,
            quantity=basket.quantity,
            time_add_product_basket=basket.time_add,
            images=list_image_url
        )
        list_products_basket.append(product_schema)
    return FinalOutput(products=list_products_basket,total_products=total_products)
      
class UpdateProductBasket(BaseModel):
    update_quantity: int = Field(..., ge=1)

@router.put("/products/basket/{product_id}")
async def updat_product_basket(product_id: int, update_quantity: UpdateProductBasket, user_id = Depends(verify_token)):
    """
    دالة تعديل المنتج في السلة
    """
    await update_quantity_database(user_id, product_id, update_quantity.update_quantity)
@router.delete("/products/basket/{product_id}")
async def delete_product_basket(product_id: int, user_id = Depends(verify_token)):
    "دالة حذف المنتج من السلة"
    await delete_product_basket_database(user_id, product_id)
class SalesLetter(BaseModel):
    product_name: str
    product_price: float
    product_quantity: int
    product_final_price: float
class InvoiceResponse(BaseModel):
    invoice_id: int
    user_name: str
    user_email: str
    order_time: datetime
    order_list: list[SalesLetter]
    total_price: float
    message: str = "الدفع عند الاستلام"
@router.post("/order", responses={200: {"model": InvoiceResponse, "description": "تم شراء المنتج بنجاح الدفع عند الاستلام"}})
async def product_buyuser_id (id_user = Depends(verify_token)):
    """
    تستخدم دالة المسار هذه لشراء المنتجات
    """
    result  = await product_buy_database(id_user)
    
    if not result:
        raise HTTPException(400, "لا يوجد منتجات سلة التسوق فارغة")
    list_order, user_invoice, user = result
    purchase_invoice = []
    final_price = 0
    for order in list_order:
        final_price += order.subtotal
        sales_letter = SalesLetter(product_name=order.product_name, product_price=order.unit_price, product_quantity=order.quantity, product_final_price=order.subtotal)
        purchase_invoice.append(sales_letter)
   
    return InvoiceResponse (
        invoice_id=user_invoice.id,
        user_name=user.name,
        user_email=user.email,
        order_time=user_invoice.time_add,
        order_list=purchase_invoice,
        total_price=final_price

    )
class ViewInvoices(BaseModel):
    billing_id: int 
    time_purchase: datetime
    is_active: bool
class ListBills(BaseModel):
    list_bills: list[ViewInvoices]
    total_billing: int
@router.get("/order", responses={200: {"model": ListBills, "description": "تم عرض فواتير الشراء بنجاح"}})
async def view_invoices(
    limit: int = Query(10, ge=1, le=100, descripion="عدد المنتجات في الدفعة الواحدة"),
    offset: int = Query(0, ge=0, description="عدد المنتجات المراد تخطيها"),
    user_id = Depends(verify_token)):
    """
    تستخدم هذه الدالة لعرض الفواتير
    """
    orders, total = await view_invoices_database(limit, offset, user_id)
    list_bills = []
    for order in orders:
        list_bills.append(ViewInvoices(billing_id=order.id, time_purchase=order.time_add, is_active=order.is_active))

    return ListBills(list_bills=list_bills, total_billing=total)




@router.delete("/order/{order_id}", responses={200: {"model": Message, "description": "تم إلغاء عملية الشراء بنجاح"}})
async def cancel_order(order_id: int, user_id = Depends(verify_token)):
    """
    تسخدم هذه الدالة لإلغاء عملية الشراء
    """
    await cancel_order_database(order_id, user_id)
    return Message(message="تم إلغاء عملية الشراء بنجاح")
    
    
