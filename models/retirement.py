from extensions import db
from datetime import datetime
from typing import Dict, Any

class RetirementAccount(db.Model):
    """
    Model representing a user's retirement account.
    
    Stores information about the user's personal funds and 401k balance.
    """
    __tablename__ = 'retirement_accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    personal_funds = db.Column(db.Float, nullable=False, default=10000.0)
    retirement_balance = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the retirement account to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary containing the account data
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'funds': self.personal_funds,
            '401k_balance': self.retirement_balance,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }