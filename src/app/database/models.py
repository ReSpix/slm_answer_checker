from sqlalchemy import BigInteger, Identity, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Questions(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)


class KeyConcepts(Base):
    __tablename__ = "key_concepts"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)