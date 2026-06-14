from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserProfileResponse, UserProfileUpdateRequest


class UserService:
    def get_profile(self, user: User) -> UserProfileResponse:
        return UserProfileResponse.model_validate(user)

    def update_profile(
        self,
        db: Session,
        user: User,
        payload: UserProfileUpdateRequest,
    ) -> User:
        updates = payload.model_dump(exclude_unset=True)

        if 'email' in updates and updates['email'] != user.email:
            existing_user = db.scalar(
                select(User).where(
                    User.email == updates['email'],
                    User.user_id != user.user_id,
                )
            )
            if existing_user:
                raise ValueError('该邮箱已被其他用户使用')

        for field, value in updates.items():
            setattr(user, field, value)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user


service = UserService()
