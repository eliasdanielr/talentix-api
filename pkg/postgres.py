from typing import Optional, Tuple, Union, Any, TypeAlias
from psycopg import sql
import psycopg
from pydantic import BaseModel
from typing_extensions import LiteralString

from pkg.error import Error, ReturnType

ExecuteReturn: TypeAlias = ReturnType[Union[list[Any], int]]

class Postgres:
    """
    A class to handle PostgresSQL database operations.
    """

    def __enter__(self) -> 'Postgres':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __init__(self, host: str = 'localhost', port: int = 5432, user: str = 'postgres', password: str = '', database: str = 'postgres') -> None:
        self.host: str = host
        self.port: int = port
        self.user: str = user
        self.password: str = password
        self.database: str = database
        self.connection: Optional[psycopg.Connection] = None

    def connect(self) -> Optional[Error]:
        """
        Establishes a connection to the PostgresSQL database.

        :return: None if the connection is successful, an Error instance if an exception occurs.
        """
        try:
            self.connection = psycopg.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.database
            )
            return None
        except Exception as e:
            return Error(mesage=str(e))

    async def execute(self, query: psycopg.cursor.Query, params: Optional[tuple] = None) -> ExecuteReturn:
        """
        Executes a given SQL query on the PostgresSQL database.

        :param query: The SQL query to be executed.
        :param params: The parameters to be passed with the query, if any.
        :return: A tuple containing the result of the query and None, or None and an Error instance in case of failure.
        """
        if not self.connection:
            return None, Error(mesage="No connection established.")

        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query, params)
                if cursor.description:
                    return cursor.fetchall(), None
                self.connection.commit()
                return cursor.rowcount, None
            except Exception as e:
                self.connection.rollback()
                return None, Error(mesage=f"Error executing the query: {e}")

    def close(self) -> Tuple[bool, Optional[Error]]:
        """
        Closes the current database connection.

        :return: A tuple indicating if the connection was successfully closed and None, or False and an Error instance if no connection exists.
        """
        if self.connection:
            self.connection.close()
            self.connection = None
            return True, None
        return False, Error(mesage="Connection is already closed or does not exist.")


def prepare(query: LiteralString) -> sql.SQL:
    """
    Prepares a SQL query string for execution by psycopg.

    :param query: The raw SQL query string.
    :return: A psycopg SQL query object ready for execution.
    """
    return sql.SQL(query)


def prepare_with_model(query: LiteralString, model: BaseModel) -> sql.Composed:
    """
    Builds a SQL query by formatting the query string with the model's values.

    :param query: The raw SQL query string with placeholders.
    :param model: The Pydantic model whose data will be used to format the query.
    :return: A formatted SQL query object.
    """
    model_data: dict[str, Any] = vars(model)
    query_composed = sql.SQL(query).format(
        **{key: sql.Placeholder() for key in model_data.keys()}
    )
    return query_composed
