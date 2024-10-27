from app.schemas.schema_users import UserSchemaAdd, UserSchema
from app.db.utils.unitofwork import IUnitOfWork


class UsersService:
    async def add_user(self, uow: IUnitOfWork, user: UserSchemaAdd):
        user_dict = user.model_dump()
        async with uow:
            user_id = await uow.users.add_one(user_dict)
            await uow.commit()
            return user_id

    async def get_users(self, uow: IUnitOfWork, clerk_id: str):
        async with uow:
            users = await uow.users.find_all_by(clerkId=clerk_id)
            users = [
                UserSchema.model_validate(user, from_attributes=True) for user in users
            ]
            return users

    async def get_user(self, uow: IUnitOfWork, user_id: int):
        async with uow:
            user = await uow.users.find_one(id=user_id)
            user = UserSchema.model_validate(user, from_attributes=True)
            return user

    async def get_user_by_clerk_id(self, uow: IUnitOfWork, clerk_id: str):
        async with uow:
            user = await uow.users.find_one(clerk_id=clerk_id)
            user = UserSchema.model_validate(user, from_attributes=True)
            return user
