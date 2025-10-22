from datetime import datetime
from sqlalchemy import ForeignKey, text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base, uniq_str_an
from database.sql_enums import UserRoleEnum, TradeResultEnum



class User(Base):
    username: Mapped[uniq_str_an]
    email: Mapped[uniq_str_an]
    password: Mapped[str]
    role: Mapped[UserRoleEnum] = mapped_column(default=UserRoleEnum.BASIC, server_default=text("'basic'"))
    result: Mapped[TradeResultEnum | None]

    # Связь с профилем
    profile: Mapped["Profile"] = relationship("Profile", back_populates="user", uselist=False)

    # Связь с сетапами (сетапы, которые пользователь сам создал)
    setups: Mapped[list["Setup"]] = relationship("Setup", back_populates="owner", cascade="all, delete-orphan")

    # Подписки на трейдеров
    following: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="follower",
        foreign_keys="Subscription.follower_id",
        cascade="all, delete-orphan"
    )

    # Подписчики (те, кто подписаны на этого трейдера)
    followers: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="followed",
        foreign_keys="Subscription.followed_id",
        cascade="all, delete-orphan"
    )

    # Доходность (агрегированные данные)
    stats: Mapped[list["UserStats"]] = relationship("UserStats", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    about: Mapped[str | None]
    photo_url: Mapped[str | None]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    user: Mapped["User"] = relationship(back_populates="profile")


class Setup(Base):
    """Сетап (торговая идея)"""
    title: Mapped[str]
    description: Mapped[str | None]
    entry_price: Mapped[float]
    stop_loss: Mapped[float]
    take_profit: Mapped[float]
    result: Mapped[TradeResultEnum | None]
    pnl: Mapped[float | None]  # Доход/убыток по сделке
    created_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))

    # Автор сетапа
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship("User", back_populates="setups")


class Subscription(Base):
    """Подписки между трейдерами"""
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    followed_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))

    follower: Mapped["User"] = relationship(
        "User", foreign_keys=[follower_id], back_populates="following"
    )
    followed: Mapped["User"] = relationship(
        "User", foreign_keys=[followed_id], back_populates="followers"
    )


class UserStats(Base):
    """Статистика трейдера"""
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    month: Mapped[int]
    year: Mapped[int]
    total_trades: Mapped[int] = mapped_column(default=0)
    wins: Mapped[int] = mapped_column(default=0)
    losses: Mapped[int] = mapped_column(default=0)
    profit_percent: Mapped[float] = mapped_column(default=0.0)
    total_pnl: Mapped[float] = mapped_column(default=0.0)

    user: Mapped["User"] = relationship("User", back_populates="stats")