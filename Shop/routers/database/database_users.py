from routers.database.database import engine, Users
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

async def modification_profile_image(id, image_link):
    """
    نستعمل دالة القاعدة هذه لأضافة صورة لبروفايل المستخدم
    """
    async with AsyncSession(engine) as session:
        statement = select(Users).where(Users.id == id["user_id"])
        result = await session.exec(statement)
        my_id_user = result.first()
        if my_id_user:
            link_image_delete = my_id_user.image
            my_id_user.image = image_link
            session.add(my_id_user)
            await session.commit()
            return link_image_delete
        else:
            return False

async def delete_images_database(id):
    """
    نستعمل دالة القاعدة هذه لحذف صورة المستخدم
    """
    async with AsyncSession(engine) as session:
        statement = select(Users).where(Users.id == id["user_id"])
        result = await session.exec(statement)
        my_id_user = result.first()
        if not my_id_user:
            return False 
        elif my_id_user.image:
            link_image_delete = my_id_user.image
            my_id_user.image = None
            session.add(my_id_user)
            await session.commit()
            return link_image_delete
        else:
            return None

async def name_change_database(name, id):
    """
    نستعمل دالة القاعدة هذه لتحديث اسم المستخدم
    """
    async with AsyncSession(engine) as session:
        statement = select(Users).where(Users.id == id["user_id"])
        result = await session.exec(statement)
        my_id_user = result.first()
        if my_id_user:
            my_id_user.name = name
            session.add(my_id_user)
            await session.commit()
            return True
        return None

# عرض الملف الشخصي للمستخدم
async def view_user_profile(id):
    """
    نستعمل دالة القاعدة هذه لعرض الملف الشخصي للمستخدم
    """
    async with AsyncSession(engine) as session:
        statement = select(Users).where(Users.id == id["user_id"])
        result = await session.exec(statement)
        user = result.first()
        if user:
            return user
        return None
async def extraction_password(id):
    """
    نستعمل دالة القاعدة هذه لستخراج كلمة السر المشفرة من القاعدة
    """
    async with AsyncSession(engine) as session:
        user = select(Users.password).where(Users.id == id["user_id"])
        hero = await session.exec(user)
        password = hero.first()
        if password:
            return password
        else:
            return False
        
    
# تغير كلمة سر
async def change_password_user(id, new_password):
    """
    نستعمل دالة القاعدة هذه لتغير كلمة السر بتعية المستخدم
    """
    async with AsyncSession(engine) as session:
        statement = select(Users).where(Users.id == id["user_id"])
        result = await session.exec(statement)
        user = result.first()
        if user:
            user.password = new_password
            session.add(user)
            await session.commit()
            return True
        return None
# تحقق من البريد الألكتروني
async def check_email_address(email):
    """
    نستعمل دالة القاعدة هذه لتحقق من وجود البريد الألكتروني الذي يريد المستخدم تغير به البريد الألكتروني القديم
    """
    async with AsyncSession(engine) as session:
        statement = select(Users.id).where(Users.email == email)
        result = await session.exec(statement)
        user = result.first()
        if user:
            return True
        return None
# تغير البريد الألكتروني 
async def change_email_address(id, change_email):
    """
    نستعمل دالة القاعدة هذه لتحديث البريد الألكتروني
    """
    async with AsyncSession(engine) as session:
        statement = select(Users).where(Users.id == id["user_id"])
        result = await session.exec(statement)
        user = result.first()
        if user:
            user.email = change_email
            session.add(user)
            await session.commit()
            return True
        return None
# حذف حساب المستخدم
async def delete_account_database(id):
    """
    نستعمل دالة القاعدة هذه لحذف حساب المستخدم
    """
    async with AsyncSession(engine) as session:
        statement = select(Users).where(Users.id == id["user_id"])
        result = await session.exec(statement)
        user = result.first()
        if user:
            name_image = user.image
            await session.delete(user)
            await session.commit()
            return name_image
        else:
            return False

