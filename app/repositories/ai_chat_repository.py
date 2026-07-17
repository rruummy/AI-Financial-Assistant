from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.ai_chat import AIChat

class AIChatRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, user_id: int, question: str, answer: str) -> AIChat:
        chat = AIChat(user_id = user_id, question = question, answer = answer)

        self.session.add(chat)
        self.session.commit()
        self.session.refresh(chat)
        return chat
    
    def get_by_id(self, chat_id: int) -> AIChat | None:
        return self.session.get(AIChat, chat_id)
    
    def get_history(self, user_id: int) -> list[AIChat]:
        stmt = (select(AIChat)
                .where(AIChat.user_id == user_id)
                .order_by(AIChat.created_at.desc()))
        return self.session.scalars(stmt).all()

    def get_last_messages(self, user_id: int, limit: int = 5) -> list[AIChat]:
        stmt = (select(AIChat).where(AIChat.user_id == user_id)
                .order_by(AIChat.created_at.desc())
                .limit(limit))
        return self.session.scalars(stmt).all()

    def delete(self, chat: AIChat) -> None:
        self.session.delete(chat)
        self.session.commit()
