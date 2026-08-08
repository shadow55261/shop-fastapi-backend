from routers.database.database import engine, Users
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
async def insort(name, age, password, email):
    """
    تستعمل هذه الدالة لأنشاء حساب في القاعدة
    """
    user = Users(name=name, age=age, password=password, email=email)
    async with AsyncSession(engine) as session:
        session.add(user)
        await session.commit()

async def select_user(email):
    """
    تستعمل دالة هذه لستخراج كلمة سر المستخدم عند عملية تسجيل الدخول بناً على البريد الألكتروني للمستخدم
    """
    async with AsyncSession(engine) as session:
        statement = select(Users.password).where(Users.email == email)
        result = await session.exec(statement)
        user_password = result.first()
        if user_password:
            return user_password
        else:
            return False
        
async def no_user_available(email):
    """
    تستعمل دالة المسار هذه للتحقق من وجود بريد الألكتروني عند عمليةأنشاء حساب
    """
    async with AsyncSession(engine) as session:
        statement = select(Users.id).where(Users.email == email)
        result = await session.exec(statement)
        user_email = result.first()
        if not user_email:
            return True
        else:
            return False
async def id_user(email):
    """
    الخاص بالمستخدم لتمريره لدالة أنشاء التوكن id تستعمل دالة هذه لأسخراج ال 
    """
    async with AsyncSession(engine) as session:
        statement = select(Users.id, Users.status).where(Users.email == email)
        result = await session.exec(statement)
        unique_user_id = result.first()
        if unique_user_id:
            return {
                "user_id": unique_user_id.id,
                "status": unique_user_id.status
            }
        else:
            
            return False
