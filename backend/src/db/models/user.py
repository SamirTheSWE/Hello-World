"""
The Model for the Users Table
"""

from sqlalchemy import func, Integer, String, TIMESTAMP, desc, asc
from sqlalchemy.orm import mapped_column, MappedColumn
from sqlalchemy.sql.expression import select

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

from ..connector import Base, AsyncSession as DataBase


class User(Base):
    """User Model"""

    __tablename__ = "Users"

    id: MappedColumn[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    display_name: MappedColumn[str] = mapped_column(String(30), nullable=False)
    username: MappedColumn[str] = mapped_column(String(30), nullable=False, unique=True)
    password: MappedColumn[str] = mapped_column(String(255), nullable=False)
    avatar: MappedColumn[str] = mapped_column(String(255))
    bio: MappedColumn[str] = mapped_column(String(100))
    country: MappedColumn[str] = mapped_column(String(56), nullable=False)
    points: MappedColumn[int] = mapped_column(Integer, default=0, nullable=False)
    last_seen: MappedColumn[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at: MappedColumn[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)


    def as_dict(self, *, ignore: list[str] = []) -> dict[str, Any]:
        """
        Override the Method

        Parameters
        ----------
        ignore: List[:class:`str`]
            The Columns to Ignore

        Returns
        -------
        :class:`dict`
            The Dictionary
        """

        with open(str(Path(__file__).parents[2]) + "/" + "utils" + "/" + "countries.json", "r") as File:
            COUNTRIES = json.load(File)

        out = super().as_dict(ignore=ignore)
        out['country'] = COUNTRIES[self.country]
        return out


    @classmethod
    async def Create(cls, db: DataBase, *, display_name: str, username: str, password: str, country: str) -> 'User':
        """
        Create a User

        Parameters
        ----------
        db: :class:`DataBase`
            The DataBase Session
        display_name: :class:`str`
            The Display Name of the User
        username: :class:`str`
            The Username of the User
        password: :class:`str`
            The Password of the User
        country: :class:`str`
            The Country of the User

        Returns
        -------
        :class:`User`
            The User
        """

        user = cls(display_name=display_name, username=username, password=password, country=country)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


    @staticmethod
    async def GetByName(db: DataBase, *, username: str) -> 'User | None':
        """
        Get a User by their Username

        Parameters
        ----------
        db: :class:`DataBase`
            The DataBase Session
        username: :class:`str`
            The Username of the User

        Returns
        -------
        Optional[:class:`User`]
            The User
        """

        result = await db.execute(select(User).where(User.username == username))
        return result.scalar() if result else None


    @staticmethod
    async def GetByID(db: DataBase, *, user_id: int) -> 'User | None':
        """
        Get a User by their ID

        Parameters
        ----------
        db: :class:`DataBase`
            The DataBase Session
        user_id: :class:`int`
            The ID of the User

        Returns
        -------
        Optional[:class:`User`]
            The User
        """

        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar() if result else None
    
    
    @staticmethod
    async def GetAll(db: DataBase, *, limit: Optional[int], sort_by: Optional[str] = "id", order: Optional[str] = "desc") -> list['User']:
        """
        Get All Users

        Parameters
        ----------
        db: :class:`DataBase`
            The DataBase Session
        limit: Optional[:class:`int`]
            The Limit of Users to Get
        sort_by: Optional[:class:`str`]
            The Column to Sort By
        order: Optional[:class:`str`]
            The Order to Sort By

        Returns
        -------
        List[:class:`User`]
            The Users
        """

        # Whitelist allowed columns to prevent SQL injection
        allowed_columns = {'id', 'username', 'points', 'created_at', 'last_seen', 'display_name'}
        if sort_by not in allowed_columns:
            raise ValueError(f"Invalid sort_by column: {sort_by}")

        # Whitelist order direction
        if order.lower() not in {'asc', 'desc'}:
            raise ValueError(f"Invalid order: {order}")

        # Use SQLAlchemy column object instead of string interpolation
        column = getattr(User, sort_by)
        order_func = desc if order.lower() == 'desc' else asc

        result = await db.execute(select(User).order_by(order_func(column)).limit(limit))
        return list(result.scalars().all())


    async def Update(self, db: DataBase) -> 'User':
        """
        Update the User

        Parameters
        ----------
        db: :class:`DataBase`
            The DataBase Session

        Returns
        -------
        :class:`User`
            The Updated User
        """

        await db.commit()
        await db.refresh(self)
        return self


    async def Delete(self, db: DataBase) -> bool:
        """
        Delete the User

        Parameters
        ----------
        db: :class:`DataBase`
            The DataBase Session

        Returns
        -------
        :class:`bool`
            The Result of the Deletion
        """
       
        await db.delete(self)
        await db.commit()
        return True
