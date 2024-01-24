from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound


class AsyncCRUD:
    def __init__(self, model, session):
        self.model = model
        self.session = session

    async def create(self, **kwargs):
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def read(self, id):
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        try:
            return result.scalars().one()
        except NoResultFound:
            return None

    async def update(self, id, **kwargs):
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        try:
            instance = result.scalars().one()
            for attr, value in kwargs.items():
                setattr(instance, attr, value)
            await self.session.commit()
            return instance
        except NoResultFound:
            return None

    async def delete(self, id):
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        try:
            instance = result.scalars().one()
            await self.session.delete(instance)
            await self.session.commit()
        except NoResultFound:
            return None
