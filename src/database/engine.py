from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.database.base import Base


class DatabaseEngine():
    """
    Encapsulate database engine creation and initialization logic.

    Attributes:
        path (str): Path to the database file.
    """

    def __init__(self, path) -> None:
        """
        Create a SQLAlchemy engine, session factory, and all the tables
        from the `Base` class metadata for the given database.

        Args:
            path (str): Path to the database file.
        """
        self.engine = create_engine(f"sqlite:///{path}", echo=False, future=True)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False)

        from src.database import tables # noqa: F401

        Base.metadata.create_all(bind=self.engine)

    def get_session_factory(self) -> sessionmaker[Session]:
        """
        Return the SQLAlchemy session factory used to create sessions.
        """
        return self.SessionLocal
