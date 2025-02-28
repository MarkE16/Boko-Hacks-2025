from extensions import db

class Email(db.Model):
  __tablename__ = "emails"
  
  id = db.Column(db.Integer, primary_key=True)
  subject = db.Column(db.String(200), nullable=False)
  recipient = db.Column(db.String(200), nullable=False)
  sender = db.Column(db.String(200), nullable=False)
  body = db.Column(db.Text, nullable=False)
  
  def __repr__(self) -> str:
    return f"<Email {self.subject}>"
  