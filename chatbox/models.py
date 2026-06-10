from extensions import db
from database.baseModel import BaseModel

class Conversation(BaseModel):
    __tablename__='conversations'
    title=db.Column(db.String(),nullable=True)
    user_id=db.Column(db.Integer(),db.ForeignKey("users.id"),nullable=False)

    user=db.relationship("User",back_populates="ai_conversations")
    messages=db.relationship(
        "AIMessage",
        back_populates='conversation', 
        cascade="all, delete-orphan",
        order_by="AIMessage.created_at.asc()")

    def to_dict(self):
        return {
            "id":self.id,
            "title":self.title,
            "user_id":self.user_id,
            "created_at":self.created_at,
            "updated_at":self.updated_at
        }
    

class AIMessage(BaseModel):
    __tablename__='ai_messages'
    conversation_id=db.Column(db.Integer(),db.ForeignKey("conversations.id"),nullable=False)
    content=db.Column(db.Text(),nullable=False)
    model=db.Column(db.String(),nullable=True)
    tokens_used=db.Column(db.Integer(),default=0)
    topic=db.Column(db.String())
    role=db.Column(db.String(),nullable=False)
    conversation=db.relationship("Conversation",back_populates="messages",)

    def to_dict(self):
         return {
            "id":self.id,
            "conversation_id":self.conversation_id,
            "content":self.content,
            "model":self.model,
            "tokens_used":self.tokens_used,
            "role":self.role,
            "topic":self.topic,
            "created_at":self.created_at,
            "updated_at":self.updated_at
        }
    def update_tokens_used(self,tokens):
        return self.tokens_used+(tokens or 1)
