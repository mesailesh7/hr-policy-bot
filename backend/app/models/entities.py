from datetime import datetime
from enum import Enum
import uuid
from typing import Optional, List
from sqlmodel import Field, Relationship, SQLModel


class UserRole(str, Enum):
    ADMIN = "admin"  # Full access: upload docs, view analytics
    HR_MANAGER = "hr_manager"  # Access to HR-specific docs & flagged queries
    EMPLOYEE = "employee"  # Standard employee access
    CONTRACTOR = "contractor"  # Limited policy access


class Organization(SQLModel, table=True):
    __tablename__ = "organizations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(index=True)
    slug: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    users: List["User"] = Relationship(back_populates="organization")
    documents: List["DocumentMetadata"] = Relationship(back_populates="organization")
    query_logs: List["QueryLog"] = Relationship(back_populates="organization")


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    org_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)
    email: str = Field(unique=True, index=True)
    full_name: str
    role: UserRole = Field(default=UserRole.EMPLOYEE)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    organization: Optional[Organization] = Relationship(back_populates="users")
    query_logs: List["QueryLog"] = Relationship(back_populates="user")


class DocumentMetadata(SQLModel, table=True):
    """
    Tracks policy documents stored in Qdrant.
    Vector payload will filter using org_id and allowed_roles.
    """
    __tablename__ = "document_metadata"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    org_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)
    title: str
    file_path: str
    file_type: str = "pdf"

    # Comma-separated or JSON string for roles allowed to access this document
    # e.g., "employee,hr_manager,admin" or "contractor,employee"
    allowed_roles: str = Field(default="employee,hr_manager,admin")

    chunk_count: int = Field(default=0)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    organization: Optional[Organization] = Relationship(back_populates="documents")


class QueryLog(SQLModel, table=True):
    """
    Tracks employee queries, RAG confidence scores, 
    and flags queries where documentation is missing.
    """
    __tablename__ = "query_logs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    org_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)
    user_id: Optional[uuid.UUID] = Field(foreign_key="users.id", default=None, index=True)

    query_text: str
    response_text: str

    # Metadata for evaluation & HR dashboard flagging
    sources_cited: Optional[str] = Field(default=None)  # JSON-encoded array of citations
    is_unanswered: bool = Field(default=False, index=True)  # True if bot couldn't find answer
    confidence_score: Optional[float] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    organization: Optional[Organization] = Relationship(back_populates="query_logs")
    user: Optional[User] = Relationship(back_populates="query_logs")