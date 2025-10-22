from enum import Enum


# --- Пользовательские роли ---
class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    BASIC = "basic"
    SILVER = "silver"
    GOLD = "gold"


# --- Результаты сделок ---
class TradeResultEnum(str, Enum):
    WIN = "win"          # сделка успешна
    LOSS = "loss"        # убыток
    BE = "breakeven"     # без убытка / без прибыли


# --- Дополнительно (пригодится позже) ---
class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class ProfessionEnum(str, Enum):
    TRADER = "trader"
    ANALYST = "analyst"
    DEVELOPER = "developer"
    UNEMPLOYED = "unemployed"


# --- Для постов, если будут использоваться ---
class StatusPost(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class RatingEnum(str, Enum):
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
