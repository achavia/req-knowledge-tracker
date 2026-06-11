from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine("sqlite:///data.db", connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class RequirementGroup(Base):
    __tablename__ = "requirement_groups"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    project_name = Column(String, nullable=True)
    requirements = relationship("Requirement", back_populates="group")

class Requirement(Base):
    __tablename__ = "requirements"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    group_id = Column(Integer, ForeignKey("requirement_groups.id"))
    group = relationship("RequirementGroup", back_populates="requirements")
    trello_card_id = Column(String, nullable=True)  # Store Trello card ID for linking
    trello_card_url = Column(String, nullable=True)  # Store Trello card URL

class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    path = Column(String)
    requirement_id = Column(Integer, ForeignKey("requirements.id"))


def init_db():
    Base.metadata.create_all(bind=engine)
