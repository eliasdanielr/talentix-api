from typing import Optional

from pydantic import BaseModel

import pkg.postgres as postgres
from pkg.error import Error, ReturnType, Cerror
from . import types


async def save(user: types.User) -> ReturnType[types.User, Error]:
    """
    Asynchronously saves a user to the database.

    :param user: The User object to save.
    :return: A tuple with the saved User object and None, or None and an Error if there was an issue.
    """
    query = """
        INSERT INTO users (id, username, display_name, email, phone_number, country, lang, hashed_password)
        VALUES ({id}, {username}, {display_name}, {email}, {phone_number}, {country}, {lang}, {hashed_password})
        RETURNING id, username, display_name, email, phone_number, country, lang, hashed_password;
    """

    prepared_query = postgres.prepare_with_model(query, user)

    with postgres.Postgres() as conn:
        error = conn.connect()
        if error:
            return None, error

        result, error = await conn.execute(prepared_query, tuple(vars(user).values()))  # Execute the query

        if error:
            return None, error

        user = result[0]
        if user is None:
            return None, Cerror()
        return types.User(**dict(zip(user.keys(), user))), None
