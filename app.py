import os
import math
import logging
import uuid
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from google.cloud import storage
from pathlib import Path
from datetime import datetime
import firebase_admin
from firebase_admin import auth


app = Flask(__name__)
CORS(app)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

CLOUD_STORAGE_BUCKET = app.config['CLOUD_STORAGE_BUCKET']
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = app.config['GOOGLE_APPLICATION_CREDENTIALS']
APP_PORT = app.config['APP_PORT']
firebase_admin.initialize_app()

db = SQLAlchemy(app)
from models import Posts


@app.route('/')
def index():
    return 'pawty'


@app.route('/lost-found-pets')
def lost_found():
    try:
        PAGE_SIZE = 20

        post_type = request.args.get('post_type')
        post_type = post_type.strip().split(",") if post_type != None and (',' in post_type or len(post_type) > 0) else []

        gender = request.args.get('gender')
        gender = gender.strip().split(",") if gender != None and (',' in gender or len(gender) > 0) else []

        province = request.args.get('province')
        province = province.strip().split(",") if province != None and (',' in province or len(province) > 0) else []

        page = request.args.get('page')
        page = 1 if page == None else int(page)

        #check variable
        if not set(post_type).issubset(set(['Found', 'Lost'])):
            return "type invalid", 400
        if not set(gender).issubset(set( ['Male', 'Female'])):
            return "gender invalid", 400

        query = Posts.query.filter(Posts.is_found == False)

        if len(post_type) > 0:
            query = query.filter(Posts.post_type.in_(post_type))
        if len(gender) > 0:
            query = query.filter(Posts.gender.in_(gender))
        if len(province) > 0:
            query = query.filter(Posts.province.in_(province))

        total_count = query.count()
        page_count = math.ceil(total_count / PAGE_SIZE)
        page_count = 1 if page_count == 0 else page_count

        if page > page_count or page < 1:
            return 'page not found', 404

        offset = page_count*(page-1)
        records = query.order_by(Posts.created_at.desc())[offset:PAGE_SIZE]
        response = {
            'records': [e.card() for e in records],
            "page": page,
            "per_page": PAGE_SIZE,
            "page_count": page_count,
            "total_count": total_count
        }
        return jsonify(response), 200
    except Exception as e:
        logging.exception(e)
        return "Internal server error", 500


@app.route('/add-pets', methods=['POST'])
def add_pet():
    try:
        auth_token = request.headers.get('Authorization')
        firebase_uid = ""
        if auth_token:
            id_token = auth_token.split(" ")[1]
            decoded_token = auth.verify_id_token(id_token)
            firebase_uid = decoded_token['uid']
        else:
            return "Auth invalid", 400
        form = request.form.to_dict()
        # check required key
        req_fields = [
            'name', 'email', 'tel', 'social_account', 'post_type', 'pet_type', 'gender',
            'topic', 'description', 'size', 'missing_found_date', 'breed', 'color', 'address', 'province'
        ]
        for key in form:
            if key in req_fields:
                req_fields.remove(key)
            else:
                return key + ' is not in the required field', 400

        if len(req_fields) != 0:
            return 'Required fields is missing', 400

        if (form['post_type'] not in ['Lost', 'Found']) or (form['size'] not in ["1", "2", "3"]):
            return 'The request is invalid', 400

        # pic upload
        pic = request.files['pic']
        if not pic:
            return 'No picture uploaded.', 400

        elif pic.content_type not in {'image/jpeg', 'image/png'}:
            return 'Only image file type is allow', 400

        gcs = storage.Client()
        bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
        blob = bucket.blob(uuid.uuid4().hex)
        blob.upload_from_string(
            pic.read(),
            content_type=pic.content_type
        )

        post = Posts(
            name=form['name'],
            email=form['email'],
            tel=form['tel'],
            social_account=form['social_account'],
            user_uid=firebase_uid,
            post_type=form['post_type'],
            pet_type=form['pet_type'],
            topic=form['topic'],
            is_found = False,
            pic_url=blob.public_url,
            description=form['description'],
            size=form['size'],
            gender=form['gender'],
            breed=form['breed'],
            color=form['color'],
            address=form['address'],
            province=form['province'],
            missing_found_date=datetime.strptime(
                form['missing_found_date'], '%d/%m/%Y')
        )
        db.session.add(post)
        db.session.commit()
        return 'Post uploaded', 200
    except Exception as e:
        logging.exception(e)
        return "Internal server error", 500


@app.route('/pet-detail/<pet_id>')
def pet_detail(pet_id):
    try:
        auth_token = request.headers.get('Authorization')
        firebase_uid = ""
        is_owner = False
        if auth_token:
            try:
                id_token = auth_token.split(" ")[1]
                decoded_token = auth.verify_id_token(id_token)
                firebase_uid = decoded_token['uid']
            except Exception as e:
                return "Token invalid",401
        
        post = Posts.query.get(pet_id)
        if post.user_uid == firebase_uid:
            is_owner = True
        response = post.detail()
        response.update(is_owner = is_owner)
        return jsonify(response), 200
    except Exception as e:
        logging.exception(e)
        return "Internal server error", 500

@app.route('/found-pet/<pet_id>', methods=['POST'])
def found_pet(pet_id):
    try:
        auth_token = request.headers.get('Authorization')
        firebase_uid = ""
        is_owner = False
        if auth_token:
            try:
                id_token = auth_token.split(" ")[1]
                decoded_token = auth.verify_id_token(id_token)
                firebase_uid = decoded_token['uid']
            except Exception as e:
                return "Token invalid",403
        else:
            return "No authorization",401
        

        post = Posts.query.get(pet_id)
        if post.user_uid != firebase_uid:
            return 'No Authorization',403
        post.is_found = True
        db.session.add(post)
        db.session.commit()
        return 'Ok',200 
    except Exception as e:
        logging.exception(e)
        return "Internal server error",500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=APP_PORT)
