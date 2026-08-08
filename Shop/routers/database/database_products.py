from routers.database.database import  engine, Products
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, or_


async def adding_products_database(
        name,
        description,
        price,
        quantity,
        category,
        admin_id,
        brand,
        discount_price,
        weight,
        size,
        image_route1,
        image_route2,
        image_route3,
        image_route4
):
    """
    تستعمل هذه الدالة لأضافة منتج
    """
    # نمرر جميع بيانات المنتج لكلاس جدول المنتجات
    products = Products(
        name=name,
        description=description,
        price=price,
        quantity=quantity,
        category=category,
        admin_id=admin_id,
        brand=brand,
        discount_price=discount_price,
        weight=weight,
        size=size,
        image_route1=image_route1,
        image_route2=image_route2,
        image_route3=image_route3,
        image_route4=image_route4
    )
    # نحفظ المنتج ثما نرجع الكائن الخاص بالمنتج لعرضه بعد الحفظ
    async with AsyncSession(engine, expire_on_commit=False) as session:
        session.add(products)
        await session.commit()
        return products 
    
async def product_update_database(product_id, product_data):
    """
    تستعمل هذه الدالة لتحديث بيانات المنتج
    """
    # نستخرج المنتج الذي نريد تعديله من القاعدة بناء على المعرف الخاص بالمنتج
    async with AsyncSession(engine) as session:
        statement = select(Products).where(Products.id == product_id)
        result = await session.exec(statement)
        product = result.first()
        if product:
            # نعمل لوب على القاموس القادم الخاص بتعديلات و نستخرج المفاتح الذي يمثل اسم الجدول في القاعدة و نستخرج قيمة التعديل الجديد
            for key, value in product_data.items():
                if value is not  None: # يشطرة لأ تكون قيمة التعديل فارغة لدخول شرط التعديل
                    setattr(product, key, value) # لتعديل بيانات كائن المنتج فا هي تأخذ الكائن ثما اسم العمود الذي هو المفتاح في القاموس و تأخذ قيمة التعديل setattr نستعمل الدالة 
            await session.commit()
            return True
        else:
            return False
async def product_delete_database(product_id):
    """
    تستعمل هذه الدالة لحذف منتج
    """
    # نستخرج المنتج المراد حذفه بناء على معرف المنتج
    async with AsyncSession(engine) as session:
        statement = select(Products).where(Products.id == product_id)
        result = await session.exec(statement)
        product = result.first()
        if product: # نتحقق انها قيمة غير فارغة
            delete_image_product =  product # نستخرج كائن المنتج لأرجاعه خارج الدالة بعد حذفه للوصول للأسماء صور المنتج و حذفهم
            await session.delete(product) # نطبق أمر الحذف و نحفظ الحذف
            await session.commit()
            return delete_image_product # نرجع الكائن المستخرج
        else:
            return False # وألا لو لم يجد المنتج في القاعدة نرجع قيمة خطأ
async def display_inactive_products_database(limit: int, offset: int):
    """
    نستخدم هذه الدالة لعرض المنتجات الغير نشطة والمنتهية في القاعدة للمدير
    """
    # نستخرج في البداية عدد المنتجات الغير نشطة لنرجع لمبرمج الفرنت أند العدد الكامل للمنتجت المتوفرة مع البحث ليجهز الصفحة لستقبالهم
    async with AsyncSession(engine) as session:
        # لتحديد شرط العدد بناء عليه ان يكون المنتج غير نشط او مخزونه صفر هاته و عده or_ ثما نحدد الجدول المراد العد منه ثما نستخدم دالة  func نحدد اننا نريد العد بستخدام 
        total_statement = select(func.count()).select_from(Products).where(or_(Products.is_active == False, Products.quantity == 0))
        total_result = await session.exec(total_statement)
        total = total_result.one() # int نستخرج الرقم الراجع بناء على عد المنتجات و تحوله لنوع بيانات رقم في بايثون
        # وهذه تقول للقاعدة ان يتخطى عدد معين من المنتجات التي وجدها تطابق شروط البحث offset و الدالة تقول ارجع ليا عدد معين من المنتجات التي وجتها تطابق شروط البحث مثل عشرة منتجات من أصل خمسين منتج limit تقول ارجع لي هذه المنتجات من أخر منتج أضيف إلى اول منتج اضيف يعني أبداً بي أرجاع من أحدث منتج بناء على معرف المنتجات  order_by(Products.id.desc()) و الدالة  or_ نستخرج المنتجات التي نريد عرضها بما على شرط العرض و الذي يقول هات جميع المنتجات التي في القاعدة التي توافق شرط العرض المكتوب في دالة 
        statement = select(Products).where(or_(Products.is_active == False, Products.quantity == 0)).order_by(Products.id.desc()).limit(limit).offset(offset) 
        result = await session.exec(statement)
        products = result.all() # نستخرج القيم جميعها و نخزنها في لست بايثون

        return products, total # نرجع الليست المستخرجة مع العدد الكلي او الكامل للمنتجات