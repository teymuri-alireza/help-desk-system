from enum import Enum
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import Base


class Role(Enum):
    STUDENT = "Student"
    EMPLOYEE = "Employee"
    IT_EXPERT = "IT Expert"
    HELP_DESK_MANAGER = "Help Desk Manager"
    IT_MANAGER = "IT Manager"
    SYSTEM_ADMIN = "System Admin"

    @property
    def fa(self):
        return {
            self.STUDENT: "دانشجو",
            self.EMPLOYEE: "کارمند",
            self.IT_EXPERT: "کارشناس فناوری اطلاعات",
            self.HELP_DESK_MANAGER: "مدیر میز خدمت",
            self.IT_MANAGER: "مدیر فناوری اطلاعات",
            self.SYSTEM_ADMIN: "مدیر سیستم",
        }[self]


class UserStatus(Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"

    @property
    def fa(self):
        return {
            self.ACTIVE: "فعال",
            self.INACTIVE: "غیر فعال",
            self.SUSPENDED: "مسدود شده",
        }[self]


class TicketStatus(Enum):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    WAITING_FOR_USER = "Waiting For User"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

    @property
    def fa(self):
        return {
            self.NEW:"جدید",
            self.IN_PROGRESS:"در حال بررسی",
            self.WAITING_FOR_USER:"در انتظار پاسخ کاربر",
            self.RESOLVED:"پاسخ داده شده",
            self.CLOSED:"بسته شده",
        }[self]


class TicketPriority(Enum):
    NORMAL = "Normal"
    WARNING = "Warning"
    CRITICAL = "Critical"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    role: Mapped[str] = mapped_column(SQLEnum(Role), nullable=False, index=True)
    status: Mapped[str] = mapped_column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now, nullable=False)

    created_tickets = relationship("Ticket", foreign_keys="Ticket.creator_id", back_populates="creator", cascade="all, delete-orphan")
    assigned_tickets = relationship("Ticket", foreign_keys="Ticket.assigned_to", back_populates="assignee", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="creator", cascade="all, delete-orphan")
    received_notifications = relationship("Notification", foreign_keys="Notification.receiver_id", back_populates="receiver", cascade="all, delete-orphan")
    created_notifications = relationship("Notification", foreign_keys="Notification.creator_id", back_populates="creator", cascade="all, delete-orphan")


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(SQLEnum(TicketStatus), default=TicketStatus.NEW, nullable=False, index=True)
    priority: Mapped[str] = mapped_column(SQLEnum(TicketPriority), default=TicketPriority.NORMAL, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now, onupdate=datetime.now, nullable=False)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=True)
    assigned_to: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)

    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_tickets")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tickets")
    category = relationship("Category", back_populates="tickets")
    department = relationship("Department", back_populates="tickets")
    responses = relationship("Response", back_populates="ticket", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="ticket")


class Response(Base):
    __tablename__ = "responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    parent_response_id: Mapped[int] = mapped_column(ForeignKey("responses.id"), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now, nullable=False)

    creator = relationship("User", back_populates="responses")
    ticket = relationship("Ticket", back_populates="responses")
    parent = relationship("Response", remote_side=[id], back_populates="children")
    children = relationship("Response", back_populates="parent", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="response")

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    tickets = relationship("Ticket", back_populates="category")

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    tickets = relationship("Ticket", back_populates="department")

class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    response_id: Mapped[int] = mapped_column(ForeignKey("responses.id"), nullable=True)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now, nullable=False)

    ticket = relationship("Ticket", back_populates="attachments")
    response = relationship("Response", back_populates="attachments")
    creator = relationship("User")

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now, nullable=False)

    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_notifications")
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_notifications")
