"""
CRUD operations for Message model.
"""

from sqlmodel import Session, select
from app.models import Message


def get_messages_in_partnership(session: Session, partnership_id: int) -> list[Message]:
    """Get all messages in a partnership"""
    return session.exec(
        select(Message).where(Message.partnership_id == partnership_id)
    ).all()


def create_message(
    session: Session,
    partnership_id: int,
    sender_id: int,
    receiver_id: int,
    content: str,
) -> Message:
    """Create a new message"""
    message = Message(
        partnership_id=partnership_id,
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message
