from sqlalchemy import ForeignKey, Text, Integer, UniqueConstraint, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Questions(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)

    text: Mapped[str] = mapped_column(Text, nullable=False)
    reference_answer: Mapped[str] = mapped_column(Text, nullable=True)

    key_concepts: Mapped[list["KeyConcepts"]] = relationship()


class Documents(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_filename: Mapped[str] = mapped_column(Text, nullable=False)
    stored_filename: Mapped[str] = mapped_column(Text, nullable=False)
    external_document_id: Mapped[str] = mapped_column(String(36), nullable=True)
    vectorized: Mapped[bool] = mapped_column(Boolean, default=False)


class QuestionDocumentLinks(Base):
    __tablename__ = "question_document_links"
    __table_args__ = (UniqueConstraint("question_id", "document_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )


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
    concept_scores: Mapped[list["ConceptScores"]] = relationship(back_populates="grading")


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
    grading: Mapped["Gradings"] = relationship(back_populates="concept_scores")
