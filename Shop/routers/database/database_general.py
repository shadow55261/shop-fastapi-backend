from routers.database.database import  engine, Products, ShoppingCarts, Orders, OrdersItems, Users
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, or_, func, update, delete
from fastapi import HTTPException
from logging_info import log_message
from datetime import datetime, timezone, timedelta
async def product_page_view_database(product_id):
    async with AsyncSession(engine) as session:
        statement = select(Products).where(Products.id == product_id)
        product = await session.exec(statement)
        product = product.first()
        if product:
            return product
        else:
            log_message("محاولة عرض منتج غير موجود", "INFO")
            raise HTTPException(404, "لا وجود لهذا المنتج")


async def product_search_database(product_search: str, limit: int, offset: int):
    """
    تستعمل هذه الدالة للبحث عن المنتجات
    """
    async with AsyncSession(engine) as session:        # 1. بناء شرط البحث الأساسي (إما مطابقة الاسم أو الفئة أو العلامة التجارية)
        if product_search: # شرط التحقق لو المتغير يحتوي قيمة صحيحة ننفذ الكود التالي
            # الأستعلام الذي سوف يحتوي شروط البحث التالية على الأعمدة المحددة search_filter نخزن في متغير 
            # فيها أمكانيات اوسع للفلترت الأستعلام و التعامل مع شروط اكثر تعقيد or_ ولاكن دالة  or هي دالة ذكية تعمل عمل ال  or_ ال  
            search_filter = or_( 
                # تجاهل حالة الأحرف هات المنتج المطابق لعملية البحث مهمى كانت حالة الحروف كبيرة او صغيرة و علامة النسبة المئوية التي توظع في الدالة قبل كلمة المرابد البحث عنها و بعدها لتجعل عملية البحث اشمل و اكثر توسع فا هي تصبح لتهتم لمكان وجود الكلمة سواء في منتصف حملة كبيرة او لا عادي لا يهتم يأتي في المنتج هتا لو كانت في الكلمة التي يبحث عنها في وسط جملة كبيرة ilike خذها فقط وهذه الكلمة البحث الموجودة بالمتغير عندما تبحث عنها بستخدام  product_search هذه دالة ذكية تمكننا من تحديد شروط البحث التي نريدها هنا  ilike  سوف نبني شرط البحث داخل العمود هذا في المنتج و كذالك باقي اعمدة البراند و الصنف  Products.name هنا 
                Products.name.ilike(f"%{product_search}%"),
                Products.category.ilike(f"%{product_search}%"),
                Products.brand.ilike(f"%{product_search}%"),
            )
        else:
            # لو لم يدخل المستخدم شيئاً، نجلب كل المنتجات أو نترك الشرط فارغاً
            search_filter = True # بنخزن قيمة صحيحة في المتغير عشان القيمة الصحيحة تعني هات كل المنتجات الموجودة لديك في القاعدة 
            # 2. حساب العدد الإجمالي لكل النتائج المطابقة (Total)
            # هذه تفرض شرط البحث الذي كبناه في الأعلى في بداية الدالة الذي يتجاهل حالة الأحرف مهما كانة كبيرة او صغيرة و يبحث عن في جمل لو كانت الكلمة موجودة في اي جملة او كلام اخر في القاعدة where(search_filter) هو دالة نحدد بها الجدول الذي سوف نقوم بعد القيم التي طابقة البحث فيه ال  select_from(Products) هي دالة وظيفتها عد السجلات او عمليات المنتجات التي طابقة البحث كم منتج جميعه ال func.count() هي دالة اساسية لبدأ عملية الأستعلام من قاعدة البيانات و هي تعني تجهيز خطة العمل ال  select هو مجرد متغير نخزن فيه جملة الأستعلام الخاصة بحساب العدد الكلي للمنتجات لكي ننفذه لاحقأ  total_statement ال 
        total_statement = select(func.count()).select_from(Products).where(Products.is_active == True, Products.quantity != 0, search_filter) 
        total_result = await session.exec(total_statement) # لأرسال جملة الأستعلام لقاعدة البيانات و تعود في صندوق يحتوي نتيجة session.exec نقوم بستخدام 
        total = total_result.one() # int تقوم بستخراج قيمة مفردة تسحب هذه الدالة رقم و تحوله لرقم بايثون عادي من نوع  one() ال 

        # 3. جلب الدفعة المحددة باستخدام limit و offset
        # متغير نخزن فيه جملة الأستعلام لجلب المنتجات الفعلية statement ال 
        statement = (
            select(Products) # سجلات جدول المنتجات بالكامل كما نفعل بالعادة select(Products) نطلب هنا
            .where(Products.is_active == True, Products.quantity != 0, search_filter) # اننا نريد تطبيق نفس شروط البحث التي كتبناها في اعلى الدالة والتي تنص على تجاهل حالة الحروف انثناء عملية البحث عن المنتج و الحبث عن المنتج بين النصوص الطويلة .where(search_filter)  هنا 
            .order_by(Products.id.desc())
            .limit(limit) #  الدالة هذه نمرر لها متغير يحمل رقم بناء عليه تجلب لنا عدد المنتجات التي طلبناها يعني تقول له احضر لي عدداً محدداً من المنتجات التي طلبتها يعني لو المتغير قيمته 10 سوف حظر لك عشرة منتجات .limit(limit) هنا 
            .offset(offset) #  تعني احظر المنتجات من مكان ما توقفنا يعني لو متغير الذي داخل الدالة قيمته 10 سوف يتخطى عشرة منتجات و يبدأ يجلب المنتجات من المنتج 11السبب في ذالك عندما نمرر الدفعة الأولى التي مررنا بها عشرة منتجات يكون هذا قيمته 0 يعني لا يوجد شيء لتخطيه في الدفعة الثانية نحن مررنا عشرة منتجات من الكمية كا كل يعني العدد الأجمالي فا لا نمرر العشرة السابقة نتخطى المنتجات التي عرضناها سابقاً بهذه الدالة .offset(offset) ال
        )
        
        result = await session.exec(statement) # ترسل الأستعلام الذي كتبناه في الأعلى عن طريقة البحث و العدد المطلوب من قيم البحث التي وجدها و ننتظر رد قاعدة البينات في صندوق يحتوي مشرأت 
        products = result.all() # من المنتجات لكي نتمكن من أرجاعها list تأخذ الكائنات الموجودة في النتيجة و تجمعها داخل لست all ال 

        return products, total # نرجع قائمة الصفحات الخاصة بالصفحة الحالية لعرضها اي المنتجات التي طلبها الأن لعرضها في الصفحة الحالية products  نرجع العدد الأجمالي لكل المنتجات لرسم ازرار الصفحات في الواجهة الأمامية للموقع  total نقوم بأرجاع النتائج 
async def product_show_database(limit, offset):
    "دالة عرض المنتجات"
    async with AsyncSession(engine) as session:
        total_statement = select(func.count()).select_from(Products).where(Products.is_active == True, Products.quantity != 0)
        total_result = await session.exec(total_statement)
        total = total_result.one() 
        # نستحدمها لترتيب العناصر من الأكبر للأصغر عن ارجاعها لنا بدونها سوف ترجعها لنا القاعدة كما ادلخنا العناصر أول مرة يعني هي التي ترتب و تمنع العشوائية order_by إلى اصغر واحد ال id فاهي تبدأ من اكبر  id وظيفتها ارسال طلب لقاعدة البيانات لطلب ارجاع لنا المنتجات المن أحدث منتج اضيف إلى اقدم منتج بناء على ال  desc ال 
        statement = select(Products).where(Products.is_active == True, Products.quantity != 0).order_by(Products.id.desc()).limit(limit).offset(offset)
        result = await session.exec(statement)
        products = result.all()
        return products, total

async def add_products_basket_database(user_id, product_id, quantity):
    """
    دالة أضافة منتج للسلة
    """
    async with AsyncSession(engine) as session:
        statement = select(Products).where(Products.id == product_id)
        result = await session.exec(statement)
        product = result.first()
        if not product:
            log_message("محاولة أضافة منتج غير موجود للسلة", "INFO")
            raise HTTPException(404, "هذا المنتج غير موجود")
        elif not product.is_active:
            log_message("محاولة اضافة نمنتج غير نشط للسلة", "INFO")
            raise HTTPException(400, "المنتج غير متاح في الوقت الحالي")
        elif product.quantity < quantity:
            log_message("محاولةأضافة للسلة منتج مخزونه اقل من المطلوب من المستخدم", "INFO")
            raise HTTPException(400, "الكمية المطلوبة تتجاوز المخزن المتاح حالياً")

        plan = select(ShoppingCarts).where(ShoppingCarts.product_id == product_id)
        get_result = await session.exec(plan)
        one_result = get_result.first()
        if one_result:
            one_result.quantity = quantity
            session.add(one_result)
            await session.commit()
        else:
            add_product = ShoppingCarts(user_id=user_id["user_id"], product_id=product_id, quantity=quantity)
            session.add(add_product)
            await session.commit()


async def view_basket_products_database(user_id, limit, offset):
    """
    دالة لعرض منتجات السلة
    """
    async with AsyncSession(engine) as session:
        total_statement = select(func.count()).select_from(ShoppingCarts).where(ShoppingCarts.user_id == user_id["user_id"])
        total_result = await session.exec(total_statement)
        total = total_result.one()

        statement = (
            select(ShoppingCarts, Products)
            .join(Products, ShoppingCarts.product_id == Products.id)
            .where(ShoppingCarts.user_id == user_id["user_id"])
            .order_by(ShoppingCarts.id.desc())
            .limit(limit)
            .offset(offset)
            
        )

        products_merge = await session.exec(statement)
        list_merge = products_merge.all()
        if not list_merge:
            log_message("طلب عرض منتجات السلة وهي فارغةاساساً", "INFO")
            raise HTTPException(404, "لا يوجد منتجات  تمة اضافتها للسة")
        return list_merge, total
async def update_quantity_database(user_id, product_id, update_quantity):
    """
    تستخدم هذه الدالة لتعديل كمية المطلوبة من المنتج في السلة
    """
    async with AsyncSession(engine) as session:
        statement = select(Products).where(Products.id == product_id)
        result = await session.exec(statement)
        product = result.first()
        if not product:
            log_message("محاولةتعديل كمية منتج في السلة غير موجود فيها", "INFO")
            raise HTTPException(404, "هذا المنتج غير موجود")
        elif not product.is_active:
            log_message("محاولة تعديل كمية منتج بسلة غير نشط", "INFO")
            raise HTTPException(400, "المنتج غير متاح في الوقت الحالي")
        elif product.quantity < update_quantity:
            log_message("محاولة تعديل كمية منتج في السلة الكمية المطلوبة تتجاوز المخزون", "INFO")
            raise HTTPException(400, "الكمية المطلوبة تتجاوز المخزن المتاح حالياً")
        
        statement = select(ShoppingCarts).where(ShoppingCarts.user_id == user_id["user_id"], ShoppingCarts.product_id == product_id)
        basket = await session.exec(statement)
        product_basket = basket.first()
        if not product_basket:
            log_message("محاولة تعديل منتج غير موجود في السلة", "INFO")
            raise HTTPException(404, "لا يوجد منتجات  تمة اضافتها للسة")
        product_basket.quantity = update_quantity
        session.add(product_basket)
        await session.commit()
        return True

async def delete_product_basket_database(user_id, product_id):
    """
    تستخدم هذه الدالة لحذف المنتجات من السلة
    """
    async with AsyncSession(engine) as session:
        statement = select(ShoppingCarts).where(ShoppingCarts.user_id == user_id["user_id"], ShoppingCarts.product_id == product_id)
        basket = await session.exec(statement)
        product_basket = basket.first()
        if product_basket:
            await session.delete(product_basket)
            await session.commit()


            return True
        else:
            log_message("محاولة حذف منتج من السلة غير موجود في السلة", "INFO")
            raise HTTPException(404, "لا يوجد منتجات  تمة اضافتها للسة")
async def product_buy_database(user_id):
    """
    تستخدم هذه الدالة لشراء منتجات
    """
    async with AsyncSession(engine, expire_on_commit=False) as session:
        order = Orders(user_id=user_id["user_id"])
        session.add(order)
        await session.flush() # فا لو حفظنا عملية الخصم من المخزون وحدث خطاء اثناء تسجيل الأردر في الجداول و تراجع الكود عنل اتمام عملية التسجيل في الجدول سوف تبقى عملية الخصم من مخزون مفوظة و هكذا يخزم من المخزون قبل تسجيل في جداول و يسبب خطاء بخصم لعمليات وهمية OrderItems بحالة نريد من القاعدة الوصول للبيانات التي ممرناها ولاكن بدون حفظها السبب انها لا تحفظ ولاكن تجعل القاعدة قادرة على الوصول للبيانات في الجلسة السبب لا نريد الحفظ قبل انتهاء الكود لتجنب حدوث مشكلة اثناء تسجيل الطلبات في جدول  commit هذه الدالة نستخدمها بدالة 
       
        basket_statement = select(ShoppingCarts).where(ShoppingCarts.user_id == user_id["user_id"])
        basket_result =   await session.exec(basket_statement)
        list_basket = basket_result.all()
        if not list_basket:
            await session.rollback()
            raise HTTPException(400, "لا يوجد منتجات سلة التسوق فارغة")
        list_products_ids = [basket.product_id for basket in list_basket] # نخزن جميع المعرفات للمنتجات التي في سلة المستخدم بناء عليهم سوف نستخرج هذه المنتجات من جدول المنتجات
        products_statement = select(Products).where(Products.id.in_(list_products_ids)) # موجود في لست المعرفات المستخرجة من المنتجات التي في السلة id الخاص بها اي id نستخرج المنتجات التي التي يطابق ال
        products_result =   await session.exec(products_statement)
        list_product = products_result.all()
        product_dict = {product.id: product for product in list_product} # للوصول لخصائص المنتج عند البحث عنه و أجاده value لكل منتج و مخزنه كا مفتاح لتسهيل البحث عنه عنا نحتاجه للمطابقة مع عناصر الموجودة في السلة و نخزن الكائن بتاع كل منتج كا قيمة  id نعمل لوب على لست المنتجات الراجعة ونستخرج ال
        for product_basket in list_basket: # نعمل لوب على لسة التي تحوي منتجات السلة
            product = product_dict.get(product_basket.product_id) # المنتج الموجود في السلة عن المنتج الذي استخرجناه من جدول المنتجات هنا نرى اهمية القاموس لولاه لكنا احتجنا لعمل لوبين للبحث عن المنتج في قائمة المنتجات التي رجعة لنا و هذه الخوارزمية تسمى بتقنية الهاش تابل و التي تعد من اهم و اقوى الخوارزميات في العمل  id نبحث بناء على ال 
            
            if not product:
                await session.rollback() # وهذا مهم تحسباً لأي عطل محتمل يمنع لكي نفرغ الذاكرة ولا يفضل حافظ الجلسة به session.add(order_item) او الجللسة التي سجلة في الذاكرة بسبب سطر session ويعيد قاعدة البيانات لحالتها الأصلية يفرغ ذاكرة بايثون ال  async with ترسل امر لقاعدة البيانات بألغاء اي اي عملية اشتراك حصلت مع القاعدة منذ بداية  rollback وظيفة الدالة 
                log_message("محاولة عشراء منتج غير موجود في جدول المنتجات", "INFO")
                raise HTTPException(404, "هذا المنتج غير موجود")
            elif not product.is_active:
                log_message("محاولة شراء منج غير نشط", "INFO")
                raise HTTPException(400, f" غير متاح في الوقة الحالي {product.name, product.id} المنتج")
            elif product.quantity < product_basket.quantity:
                log_message("محاولة شراء منتج مخزونه اقل من المطلوب", "INFO")
                raise HTTPException(400, f" غير متوفرة في المخزون {product.name, product.id} الكمية من منتج")
            update_statement = ( #  Inventory Race Condition التحديث الذري لمنع ثغرة 
            update(Products) # تحديد الجدول الذي سوف يتم عليه التديث 
            .where(Products.id == product_basket.product_id, Products.quantity >= product_basket.quantity, Products.is_active == True) # يتم التحديث اذا كان المعرفات في المنتج و السلة متطابقى و كمان يجب ان يكون الكمية المطلوبة لا تفوق المخزون عدداً
            .values(quantity=Products.quantity - product_basket.quantity) # لتمرير العملية الناتج عنها قيمة الجديدة للمخزون للمنتج الذي تطابقة المعرف الخاص به مع معرف السلة values الأن نستخدم دالة 
            
                        )
            update_result = await session.exec(update_statement)
            if update_result.rowcount == 0:
                await session.rollback()
                log_message("محاولة شراء منتج غير نشط او مخزونه غير كافي", "INFO")
                raise HTTPException(400, "المخزون غير كافي او المنتج غير متاح")
                
            total_price = product_basket.quantity * product.price
        

            order_item = OrdersItems(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                unit_price=product.price,
                quantity=product_basket.quantity,
                subtotal=total_price
                )
            session.add(order_item)
          
        delete_basket = delete(ShoppingCarts).where(ShoppingCarts.user_id == user_id["user_id"]) # المستخدم الحالي id نستعملها هنا و نمرر لها جدول السلة لحذف جميع المنتجات التي تحمل  delete دالة 
        await session.exec(delete_basket)
        statement = select(OrdersItems).where(OrdersItems.order_id == order.id)  
        result = await session.exec(statement)
        list_order = result.all()
        user_statement = select(Users).where(Users.id == order.user_id)  
        user_result = await session.exec(user_statement)
        user = user_result.first()
        await session.commit()
        if list_order:
            return list_order, order, user
async def  view_invoices_database(limit, offset, user_id):
    """
    تستخدم هذه الدالة لعرض الفواتير
    """
    async with AsyncSession(engine) as session:
        total_statement = select(func.count()).select_from(Orders).where(Orders.user_id == user_id["user_id"])
        total_result = await session.exec(total_statement)
        total = total_result.one()

        order_statement = (
            select(Orders)
            .where(Orders.user_id == user_id["user_id"])
            .order_by(Orders.id.desc())
            .limit(limit)
            .offset(offset)
            
        )
    
        statement = await session.exec(order_statement)
        orders = statement.all()
        if not orders:
            log_message("محاولة عرض  فواتير غير موجودة", "INFO")
            raise HTTPException(404, "لا يوجد فواتير شراء")
        return orders, total
    
async def cancel_order_database(order_id, user_id):
    """
    تستخدم هذه الدالة لحذف الفواتير
    """
    async with AsyncSession(engine) as session:
        # المستخدم id طلب الفاتورة الخاصة في طلب البيع من جدول الفواتير بناء على 
        order_result = select(Orders).where(Orders.id == order_id, Orders.user_id == user_id["user_id"])
        order_statement = await session.exec(order_result)
        order = order_statement.first()

        if not order:
            log_message("محاولة إلغاء عملية شراء غير موجودة", "INFO")
            raise HTTPException(404, "لا يوجد معاملة شراء للمستخدم")
        order_time = order.time_add.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - order_time > timedelta(hours=24):
            log_message("محاولة إلغاء الطلب مر عليه اربع و عشرين ساعة فا اكثر", "INFO")
            raise HTTPException(422, "لا يمكن إلغاء الطلب لقد مر عليه 24 ساعة بالفعل")

        # الفاتورة من جدول الفاواتير id طلب جميع المنتجات التي تم اضافتها في جدول البع بناء على 
        order_item_result = select(OrdersItems).where(OrdersItems.order_id == order.id)
        order_item_statement = await session.exec(order_item_result)
        orders_items = order_item_statement.all()
        if not orders_items:
            log_message("محاولة حذف إلغاء طلبات غير موجودة لهذه الفاتورة الشراء", "INFO")
            raise HTTPException(404, "لا يوجد طلبات  لهذه الفتورة")
        
        products_ids = [item.product_id for item in orders_items]
        product_result = select(Products).where(Products.id.in_(products_ids))
        product_statement = await session.exec(product_result)
        products =  product_statement.all()
        product_dict = {product.id: product for product in products}
        for item in orders_items:
            product = product_dict.get(item.product_id)
            if product:
                product.quantity += item.quantity
                session.add(product)
            else:
                log_message("محاولة ارجاع منتج لتحديث المخزون و هذا المنتج غير موجود في جدول المنتجات", "INFO")

            await session.delete(item)
        await session.delete(order)
        await session.commit()

        
                







    



    
