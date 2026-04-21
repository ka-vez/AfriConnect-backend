"""
Message model - Direct messages within partnerships.
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Message(SQLModel, table=True):
    """
    Direct message within a partnership.
    
    Attributes:
        id: Unique message identifier
        partnership_id: Reference to the partnership
        sender_id: ID of the message sender
        receiver_id: ID of the message receiver
        content: Message content
        is_read: Whether receiver has read the message
        created_at: When message was sent
    """
    
    __tablename__ = "messages" # type: ignore
    
    id: Optional[int] = Field(default=None, primary_key=True)
    partnership_id: int = Field(foreign_key="partnerships.id")
    sender_id: int = Field(foreign_key="users.id")
    receiver_id: int = Field(foreign_key="users.id")
    content: str = Field(max_length=5000)
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
