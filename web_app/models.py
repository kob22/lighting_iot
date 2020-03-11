from web_app import db
from datetime import datetime

class Device(db.Model):
    """Device model, with name and status (working or not)"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    status = db.Column(db.Boolean, default=False, nullable=False)
    light_stats = db.relationship('LightStat', backref='device', lazy='dynamic', cascade="all, delete-orphan", order_by="desc(LightStat.pub_date)")
    pub_date = db.Column(db.DateTime, index=True, default=datetime.utcnow, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        return {
            'name': self.name,
            'light': 'on' if self.light_stats[0].light else 'off' ,
            'status': 'on' if self.status else 'off'
        }


class LightStat(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    light = db.Column(db.Boolean, default=False, nullable=False)
    pub_date = db.Column(db.DateTime, index=True, default=datetime.utcnow, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        return {
            'id': self.id,
            'device_id': self.device_id,
            'light': 'on' if self.light else 'off'
        }
