from sqlalchemy import select

from app.database import async_session_maker


class BaseDAO:
    model = None

    def __init__(self, session):
        self.session = session

    async def find_all(self):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def find_one_or_none(self, **filters):
        query = select(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()