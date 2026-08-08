from sqlmodel import SQLModel, Field
from sqlalchemy.ext.asyncio import create_async_engine
from datetime import datetime, timezone
class Users(SQLModel, table=True):
    __tablename__ = "users"

    id: int| None = Field(default=None, primary_key=True)
    status: str = Field(default="User")
    name: str
    age: int
    password: str
    email: str
    image: str|None = None
    overview: str|None = None
class Products(SQLModel, table=True):
    __tablename__ = "products"

    id: int|None = Field(default=None, primary_key=True) # معرف المنتج 
    name: str # اسم المنتج 
    description: str # وصف المنتج
    price: float # سعر المنتج
    quantity: int # الكمية المتوفرة من المنتج
    time_add: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) # مرنت تضيف اي تحديث يطراء ولا تعتمد قيمة معينة محددت default_factory اضافة الوقت الحالي لكل منتج يتم أضافته ال 
    is_active: bool = True # حالة المنتج أذ كان متوفر يكون صح و اذ كان نفذ يكون خطاء
    category: str # صنف المنتج مثال سياراة ازياء اجهزة كهربائية 
    image_route1: str # رابط صورة للمنتج
    image_route2: str|None = None
    image_route3: str|None = None
    image_route4: str|None = None
    admin_id: str|None = None # أسم الأدمن او المدير الذي أضاف المنتج أختياري
    brand: str | None = None # البرند او الشركة المصنعة أختياري
    discount_price: float | None = None # لو في اي خصومات على المنتج أختياري
    weight: float|None = None # وزن المنتج اختياري
    size: str|None = None # مقاس اختياري لو كان ملابس مثلاً
class ShoppingCarts(SQLModel, table=True):
    __tablename__ = "shopping_carts"
    id: int|None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    product_id: int = Field(foreign_key="products.id", nullable=False)
    quantity: int = Field(default=1, ge=1)
    time_add: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) # مرنت تضيف اي تحديث يطراء ولا تعتمد قيمة معينة محددت default_factory اضافة الوقت الحالي لكل منتج يتم أضافته ال 
class Orders(SQLModel, table=True):
    __tablename__ = "orders"

    id: int|None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    #  هي خاصية تجبر قاعدة البيانات على دمج الوقت المخزن مع المنطقة الزمنية يعني التوقية الحالي للبلد التي انت فيهاtimezone=True ال  SQLAlchemy هو نوع البيانات المخصص للتواريخ و الأوقات في  DateTime كذا نقول للقاعدة سوف نحدد لك نوع البيانات التي عندما تأتي لك احتفظ بها  و تجاهل التخمين التلقائي لنوع البيانات و ترمي الأنواع الغير متوقعة لك  sa_type ال 
    time_add: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) # مرنت تضيف اي تحديث يطراء ولا تعتمد قيمة معينة محددت default_factory اضافة الوقت الحالي لكل منتج يتم أضافته ال 
    is_active: bool = True # حالة المنتج أذ كان متوفر يكون صح و اذ كان نفذ يكون خطاء

class OrdersItems(SQLModel, table=True):
    __tablename__ = "orders_items" # لتحديد الأسم بضبط للجدول داخل قاعدة البيانات __tablename__ تستخدم هذه الدالة 

    id: int|None  = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", nullable=False)
    product_id: int = Field(foreign_key="products.id", nullable=False)
# نظيف بيانات الأرشفة المهمة هذه لكي لو حصل تعديل على جدول المنتجات تفضل هذه البيانات محفوظة و سليمة ولا تتأثر في التعديل
    product_name: str # نخزن اسم المنتج عشان لو حذف المنتج من جدول المنتجات او غير اسمه لا يتأثر اسمه هنا
    unit_price: float # نخزن السعر المنتج تحسباً لو تم رفع سعره في جدول المنتجات لكي لا يتأثر السعر هنا للمعاملة
    quantity: int # نخزن الكمية المطلوبة من المنتج
    subtotal: float # نخزن السعر مروب في الكمية المطلوبة من المنتج يخرج لنا سعره النهائي
engine = create_async_engine("sqlite+aiosqlite:///shop.db")
async def init_db():
    async with engine.begin() as conn: # في حين انشاء جدول و فجاءة حدث خطاء غير متوقع مثل امتلاء مساحة القرص و لم تكمل الجدول بستخدامها يتراجع عن انشاء الجدول ويحذف الجزء الذي تم انشاؤه begin() وظيفة هذه الدالة 
        await conn.run_sync(SQLModel.metadata.create_all) # هذه الدالة توكل عملية انشاء الجدول الذي يأخذ وقت لخيط او عامل داخلي لكي لا يشغل السيرفر بها



      


