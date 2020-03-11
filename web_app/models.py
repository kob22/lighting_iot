from web_app import db


class Device(db.Model):
    """Device model, with name and status (working or not)"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    status = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        return {
            'name': self.name,
            'status': 'on' if self.status else 'off'
        }
