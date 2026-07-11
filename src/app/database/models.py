from sqlalchemy import (
    ForeignKey,
    Text,
    Integer,
    UniqueConstraint,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Questions(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)

    text: Mapped[str] = mapped_column(Text, nullable=False)
    reference_answer: Mapped[str] = mapped_column(Text, nullable=True)

    key_concepts: Mapped[list["KeyConcepts"]] = relationship()


class QuestionDocuments(Base):
    __tablename__ = "question_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    external_document_id: Mapped[str] = mapped_column(String(36), nullable=False)


class KeyConcepts(Base):
    __tablename__ = "key_concepts"

    id: Mapped[int] = mapped_column(primary_key=True)

    text: Mapped[str] = mapped_column(Text, nullable=False)
    importance: Mapped[int] = mapped_column(Integer, nullable=False)

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )


class Answers(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True)

    text: Mapped[str] = mapped_column(Text, nullable=False)

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )

    question: Mapped["Questions"] = relationship()


class Gradings(Base):
    __tablename__ = "gradings"

    id: Mapped[int] = mapped_column(primary_key=True)

    answer_id: Mapped[int] = mapped_column(
        ForeignKey("answers.id", ondelete="CASCADE"), nullable=False
    )
    cosine_similarity: Mapped[int] = mapped_column(Integer, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)

    answer: Mapped["Answers"] = relationship()


class ConceptScores(Base):
    __tablename__ = "concept_scores"
    __table_args__ = (UniqueConstraint("grading_id", "concept_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    grading_id: Mapped[int] = mapped_column(
        ForeignKey("gradings.id", ondelete="CASCADE"), nullable=False
    )
    concept_id: Mapped[int] = mapped_column(
        ForeignKey("key_concepts.id", ondelete="CASCADE"), nullable=False
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)

    concept: Mapped["KeyConcepts"] = relationship()
    grading: Mapped["Gradings"] = relationship()
