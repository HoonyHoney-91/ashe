from flask import request
from datetime import datetime
from werkzeug.datastructures import FileStorage
import pyrebase
import json
import uuid
import firebase_admin
from firebase_admin import storage

class DBHandler:
    def __init__(self):
        with open('/Users/anthonyshin/Documents/ashe/FLASK/auth/firebaseAuth.json') as f:
            config = json.load(f)

        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()
        self.storage = firebase.storage()


    def login(self, uid, pwd):
        users = self.db.child('users').get().val()
        try:
            userinfo = users[uid]
            if userinfo['pwd'] == pwd:
                return True
            else:
                return False
        except:
            return False
    
    def signin_verification(self, uid):
        users = self.db.child('users').get().val()
        # print(users)
        for i in users:
            if uid == i:
                return False
        return True

    def signup(self, _id_, pwd, name, email):
        information = {
            'pwd' : pwd,
            'uname' : name,
            'email' : email,
        }
        if self.signin_verification(_id_):
            self.db.child('users').child(_id_).set(information)
            return True
        else:
            return False
# 논문탑재 관련  
# Information 을 DB로 보내는 공식
    def write2_post(self, title, volume, number,  content, uid, author, date_posted, file):
    # Get the current date and time
        date_posted = datetime.now().strftime("%Y-%m-%d")
        date_posted_file = datetime.now().strftime("%Y%m%d")
        # Generate a unique ID for the post
        post_id = str(uuid.uuid4())[:5]
        if file and isinstance(file, FileStorage):
            # Generate a unique ID for the file
            file_id = str(uuid.uuid4())[:5]
            # Combine the unique ID and file extension to form the file name
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            file_name = f"{date_posted_file}{uid}{file_id}.{file_extension}"
            # Upload the file to Firebase storage
            self.storage.child('admin').child(post_id).child(file_name).put(file)
            # Store the file name under the post ID in the Realtime Database
            self.db.child('final_post').child(post_id).child('file_name').set(file_name)
        else:
            file_name = None

        # Store the post information and the file name under the unique ID in the Realtime Database
        information = {
            'post_id': post_id,
            'title' : title,
            'volume' : volume,
            'number' : number,
            'content' : content,
            'uid' : uid,
            'author' : author,
            'date_posted': date_posted,
            'file_name': file_name
        }

        self.db.child('final_post').child(post_id).set(information)
        return post_id
# DB에서 여기로 가져오는 공식
    def post2_list(self):
        post_list = self.db.child('final_post').order_by_child('date_posted').get().val()
        if post_list:
            sorted_posts = sorted(post_list.items(), key=lambda x: x[1]['date_posted'], reverse=True)
            return list(reversed(sorted_posts))
        else:
            return []
    
    def post2_detail(self, post_id):
        post_dict = self.db.child('final_post').order_by_child('date_posted').get().val()
        print("post_dict:", post_dict)
        post = post_dict.get(post_id)
        print("post:", post)
        if post:
            # order the comments by date_posted
            comments = post.get('comments')
            if comments:
                sorted_comments = sorted(comments.items(), key=lambda x: x[1]['date_posted'])
                post['comments'] = sorted_comments
            return post
        else:
            return None
            
    def search_posts_by_title(self, title):
        try:
            posts = self.db.child('final_post').order_by_child('title').equal_to(title).get()
            post_list = []
            for post in posts.each():
                post_list.append(post.val())
            return post_list
        except Exception as e:
            print('Error:', e)
            return []

    def search_posts_by_author(self, author):
        try:
            posts = self.db.child('final_post').order_by_child('author').equal_to(author).get()
            post_list = []
            for post in posts.each():
                post_list.append(post.val())
            return post_list
        except Exception as e:
            print('Error:', e)
            return []



# 논문투고 관련
    def write_post(self, title, content, uid, author, date_posted, file):
        post_id = str(uuid.uuid4())[:5]
        file_id = str(uuid.uuid4())[:5]
        date_posted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_posted_file = datetime.now().strftime("%Y%m%d")
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        file_name = f"{date_posted_file}{uid}{file_id}.{file_extension}"
        self.storage.child('student').child(post_id).child(file_name).put(file)
        information = {
            'post_id': post_id,
            'title' : title,
            'content' : content,
            'uid' : uid,
            'author' : author,
            'date_posted': date_posted,
            'file_name': file_name
        }
        self.db.child('upload_post').child(post_id).set(information)

    def post_list(self):
        post_list = self.db.child('upload_post').order_by_child('date_posted').get().val()
        if post_list:
            sorted_posts = sorted(post_list.items(), key=lambda x: x[1]['date_posted'], reverse=True)
            return list(reversed(sorted_posts))
        else:
            return None

    def check_user_admin(self, uid):
        user_ref = self.db.child("users").child(uid).get()
        if user_ref.val() is not None and "Admin" in user_ref.val():
            return True
        else:
            return False

    def get_user(self, uid):
        mypost_list = []
        user_posts = self.db.child('upload_post').order_by_child('date_posted').get().val()
        if user_posts:
            for post_id, post_data in user_posts.items():
                if post_data.get('uid') == uid:
                    post_data['post_id'] = post_id
                    mypost_list.append(post_data)
        return mypost_list

# ---------------------------------------------------------------------------------
# 관리자 페이지 관련
    def post2_list_admin(self):
        post_list = self.db.child('upload_post').order_by_child('date_posted').get().val()
        print("post_list_admin:", post_list)
        if post_list:
            sorted_posts = sorted(post_list.items(), key=lambda x: x[1]['date_posted'], reverse=True)
            return list(reversed(sorted_posts))
        else:
            return []


    def post2_detail_admin(self, post_id):
        post_dict = self.db.child('upload_post').order_by_child('date_posted').get().val()
        print("post_dict_admin:", post_dict)
        post = post_dict.get(post_id)
        print("post_admin:", post)
        if post:
            # order the comments by date_posted
            comments = post.get('comments')
            if comments:
                sorted_comments = sorted(comments.items(), key=lambda x: x[1]['date_posted'])
                post['comments'] = sorted_comments
            return post
        else:
            return None

    def search_posts_by_title_admin(self, title):
        try:
            posts = self.db.child('upload_post').order_by_child('title').equal_to(title).get()
            post_list = []
            for post in posts.each():
                post_list.append(post.val())
            return post_list
        except Exception as e:
            print('Error:', e)
            return []

    def search_posts_by_author_admin(self, author):
        try:
            posts = self.db.child('upload_post').order_by_child('author').equal_to(author).get()
            post_list = []
            for post in posts.each():
                post_list.append(post.val())
            return post_list
        except Exception as e:
            print('Error:', e)
            return []
    
# front page image functions
    def create_posting_folder(self):
        bucket = storage.bucket()
        posting_folder = bucket.blob('posting/')
        if not posting_folder.exists():
            posting_folder.upload_from_string('')

    def front_page_upload(self, frontImage):
        filename = frontImage.filename
        storage_path = 'posting/' + filename
        self.storage.child(storage_path).put(frontImage)
        download_url = self.storage.child(storage_path).get_url(None)
        print(f"front_page_upload : ${download_url}")
        return download_url

    def get_front_page_image_url(self):
        storage_path = 'posting/'
        bucket = storage.bucket()

        blobs = bucket.list_blobs(prefix=storage_path)
        sorted_blobs = sorted(blobs, key=lambda blob: blob.updated, reverse=True)

        download_urls = []
        for blob in sorted_blobs:
            download_url = blob.public_url
            print(f"get_front_page_image_url download_url: {download_url}")
            download_urls.append(download_url)

        return download_urls
