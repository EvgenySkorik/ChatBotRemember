from app.models.db_models import UserModel
from app.models.shemas import UserCreate
from app.services.loging import get_logger

loger = get_logger("utils_logger")

def create_user_model(data: UserCreate) -> UserModel:
    return UserModel(
        telegram_id=data.id,
        first_name=data.first_name,
        last_name=data.last_name,
        username=data.username
    )
