from app import db
import datetime

class Posts(db.Model):
    __tablename__ = 'posts'
    
    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String())
    email = db.Column(db.String())
    tel = db.Column(db.String())
    social_account = db.Column(db.String())
    user_uid = db.Column(db.String())
    post_type = db.Column(db.String())
    is_found = db.Column(db.Boolean)
    topic = db.Column(db.String())
    pic_url = db.Column(db.String())
    description = db.Column(db.String())
    size = db.Column(db.Integer())
    gender = db.Column(db.String())
    breed = db.Column(db.String())
    pet_type = db.Column(db.String())
    color = db.Column(db.String())
    address = db.Column(db.String())
    province = db.Column(db.String())
    missing_found_date = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def __repr__(self):
        return '<id {}>'.format(self.id)

# All data in Database
    def detail(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'tel': self.tel,
            'social_account': self.social_account,
            'user_uid':self.user_uid,
            'post_type': self.post_type,
            'is_found': self.is_found,
            'topic': self.topic,
            'pic_url': self.pic_url,
            'description': self.description,
            'size': self.size,
            'gender': self.gender,
            'breed': self.breed,
            'pet_type': self.pet_type,
            'color': self.color,
            'address': self.address,
            'province': self.province,
            'missing_found_date': self.format_date(self.missing_found_date),
            'created_at': self.format_date(self.created_at)
        }

# Data show only on card (short info.)
    def card(self):
        return {
            'id': self.id,
            'user_uid':self.user_uid,
            'post_type': self.post_type,
            'is_found': self.is_found,
            'topic': self.topic,
            'pic_url': self.pic_url,
            'gender': self.gender,
            'pet_type': self.pet_type,
            'province': self.province,
            'missing_found_date': self.format_date(self.missing_found_date)
        }

# Date format
    def format_date(self,date):
        return date.strftime("%d/%m/%Y")


