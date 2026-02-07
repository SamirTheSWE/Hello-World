"""
Session-Tokens Handler
"""

from fastapi import Depends, Request
from fastapi.exceptions import HTTPException

import jwt
import os
from datetime import datetime, timedelta, timezone

from ..db import get_db, DataBase, User, Session


class SessionManager:
    """Session-Tokens Handler"""

    SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY environment variable must be set")


    @staticmethod
    async def Create(db: DataBase, user_id: int, *, location: str, device: str) -> str:
        """
        Create a New Session Token
        
        Parameters
        ----------
        db: :class:`DataBase`
            The DataBase Session
        user_id: :class:`int`
            The ID of the User
        location: :class:`str`
            The Location of the User
        device: :class:`str`
            The Device of the User

        Returns
        -------
        :class:`str`
            The Session Token
        """

        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=60) # TODO: TEMPORARY

        data = {
            'sub': user_id,
            'exp': expires
        }
        token = jwt.encode(
            data,
            key=SessionManager.SECRET_KEY,
            algorithm="HS256"
        )

        sesh = await Session.Create(
            db,
            user_id=user_id,
            token=token,
            location=location,
            device=device,
            expires_at=expires
        )
        return str(sesh.token)


    @staticmethod
    async def Validate(db: DataBase, token: str) -> User:
        """
        Validate a Session Token
        
        Parameters
        ----------
        db: :class:`DataBase`
            The DataBase Session
        token: :class:`str`
            The Session Token

        Returns
        -------
        :class:`User`
            The User
        """

        try:
            data = jwt.decode(
                token,
                key=SessionManager.SECRET_KEY,
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            await SessionManager.Delete(db, token=token)
            raise HTTPException(401, "Expired Token")
            
        except jwt.InvalidTokenError:
            await SessionManager.Delete(db, token=token)
            raise HTTPException(401, "Invalid Token")
        else:
            user = await User.GetByID(db, user_id=data['sub'])
            if not user:
                raise HTTPException(401, "Invalid Token")
            return user


    @staticmethod
    async def Delete(db: DataBase, *, token: str) -> None:
        """
        Delete a Session Token
        
        Parameters
        ----------
        db: :class:`DataBase`
            The DataBase Session
        token: :class:`str`
            The Session Token

        Raises
        ------
        :class:`ValueError`
            Session Not Found
        """

        session = await Session.GetByToken(db, token=token)
        if session:
            await session.Delete(db)


async def get_current_user(request: Request, db: DataBase = Depends(get_db)) -> User:
    """
    Get the Current User
    
    Parameters
    ----------
    request: :class:`Request`
        The Request
    db: :class:`DataBase`
        The DataBase Session

    Returns
    -------
    :class:`User`
        The User
    """

    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(401, "Un-Authorised")

    authorization = authorization.split()
    if len(authorization) != 2 or authorization[0].upper() != "BEARER":
        raise HTTPException(401, "Invalid Token Scheme")
    
    return await SessionManager.Validate(db, token=authorization[1])
