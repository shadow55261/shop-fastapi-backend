from routers.database.database import engine, Users 
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

async def user_id_admin(payload):
    async with AsyncSession(engine) as session:
        plan = select(Users.status).where(Users.id == payload["user_id"], Users.status == payload["status"])
        user = await session.exec(plan)
        user_status = user.first()
        if user_status:
            return user_status
        else:
            return None
