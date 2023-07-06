from flask import Flask, render_template, request, redirect, flash, session, url_for, send_file, make_response, jsonify
from werkzeug.utils import secure_filename
from DB_handler import DBHandler
from datetime import datetime, timedelta
import secrets
from pdf2image import convert_from_path
import firebase_admin
from firebase_admin import credentials, storage
import tempfile

cred = credentials.Certificate('FLASK/auth/serviceAccount.json')
firebase_admin.initialize_app(cred, {
    "storageBucket": "ashedb-936cf.appspot.com"
})

app = Flask(__name__, template_folder='template', static_url_path='/static') 
app.secret_key = secrets.token_hex(16)
DB = DBHandler()

app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = set(['pdf'])
# for front page image
ALLOWED_EXTENSIONS = {'pdf', 'jpeg', 'gif', 'png', 'jpg'}
app.config['ALLOWED_EXTENSIONS_FOR_FRONT_PAGE'] = ALLOWED_EXTENSIONS

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# for front page image
def allowed_file_front_page(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS_FOR_FRONT_PAGE']

def generate_secret_key():
    return secrets.token_hex(16)
    
# 기본 페이지들
@app.route('/')
def index():
    user = session.get('uid', 'Login')
    if user != 'Login':
        check_user_admin = DB.check_user_admin(user)
    else:
        check_user_admin = False
    image_url = DB.get_front_page_image_url()
    print(f"image_url from index${image_url}")
    return render_template('index.html', user=user, check_user_admin=check_user_admin, image_url=image_url)

@app.route('/about')
def about():    
    user = session.get('uid', 'Login')
    if user != 'Login':
        check_user_admin = DB.check_user_admin(user)
    else:
        check_user_admin = False
    return render_template('about.html', user=user, check_user_admin=check_user_admin)

@app.route('/articlesOfIncorporation')
def articlesOfIncorporation():
    user = session.get('uid', 'Login')
    if user != 'Login':
        check_user_admin = DB.check_user_admin(user)
    else:
        check_user_admin = False
    return render_template('articlesOfIncorporation.html', user=user, check_user_admin=check_user_admin)

@app.route('/codeOfEthics')
def codeOfEthics():
    user = session.get('uid', 'Login')
    if user != 'Login':
        check_user_admin = DB.check_user_admin(user)
    else:
        check_user_admin = False
    return render_template('codeOfEthics.html', user=user, check_user_admin=check_user_admin)

@app.route('/guideline')
def guideline():
    user = session.get('uid', 'Login')
    if user != 'Login':
        check_user_admin = DB.check_user_admin(user)
    else:
        check_user_admin = False
    return render_template('guideline.html', user=user, check_user_admin=check_user_admin)

@app.route('/regulation')
def regulation():
    user = session.get('uid', 'Login')
    if user != 'Login':
        check_user_admin = DB.check_user_admin(user)
    else:
        check_user_admin = False
    return render_template('regulation.html', user=user, check_user_admin=check_user_admin)

@app.route('/welcome')
def welcome():
    user = session.get('uid', 'Login')
    if user != 'Login':
        check_user_admin = DB.check_user_admin(user)
    else:
        check_user_admin = False
    return render_template('welcome.html', user=user, check_user_admin=check_user_admin)

# 기본페이지 끝


# -----------------------------------------------------------------------------------------
# 로그인
@app.route('/login')
def login():
    user = session.get('uid', 'Login')
    if 'uid' in session:
        return redirect (url_for('index'))
    return render_template('login.html', user=user)

@app.route('/logout')
def logout():
    if 'uid' in session:
        session.pop('uid')
        return redirect (url_for('index'))
    else:
        return redirect(url_for('login'))

@app.route('/login_done', methods = ['GET'])
def login_done():
    uid = request.args.get('id')
    pwd = request.args.get('pwd')
    if DB.login(uid, pwd):
        session['uid'] = uid
        return redirect(url_for('index'))
    else:
        flash('ID or PW is invalid')
        return redirect(url_for('login'))

# 회원가입
@app.route('/signup')
def signup():
    user = session.get('uid', 'Login')
    return render_template('signup.html', user=user)

@app.route('/signup_done', methods = ['GET'])
def signup_done(): 
    email = request.args.get('email')
    uid = request.args.get('id')
    pwd = request.args.get('pwd')
    name = request.args.get('name')
    if DB.signup(email = email, _id_ =  uid, pwd = pwd, name = name):
        return redirect(url_for('login'))
    else:
        flash('This Username is not availble')
        return redirect(url_for('signup'))
# -----------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------
# 관리자 페이지 관련
@app.route('/list_admin')
@app.route('/list_admin/<int:page>')
def post2_list_admin(page=None):
    user = session.get('uid', 'Login')
    if user != 'Login':
        check_user_admin = DB.check_user_admin(user)
    else:
        check_user_admin = False
    if 'uid' in session:
        posts_per_page = 10
        post2_list = DB.post2_list_admin()
        print(post2_list)
        if post2_list is not None:
            check_user_admin = DB.check_user_admin
            total_posts = len(post2_list)
            total_pages = (total_posts - 1) // posts_per_page + 1
            if page is None or page > total_pages:
                page = total_pages
            current_page = page
            start_index = (current_page - 1) * posts_per_page
            end_index = start_index + posts_per_page
            if end_index > total_posts:
                end_index = total_posts
            current_page_posts = post2_list[start_index:end_index]
            print("Current Page:", current_page)
            return render_template('list_admin.html', user=user, post2_list=current_page_posts, check_user_admin=check_user_admin, total_posts=total_posts, total_pages=total_pages, current_page=current_page, posts_per_page=posts_per_page)
        else:
            return "No posts found"
    else:
        return redirect(url_for('login'))

@app.route('/search_admin', methods=['GET'])
def search_admin():
    search_type = request.args.get('type')
    search_text = request.args.get('text')
    print('Search Type:', search_type)
    print('Search Text:', search_text)
    # Search for posts and return the search results
    if search_type == 'title':
        search_results = DB.search_posts_by_title_admin(search_text)
    elif search_type == 'author':
        search_results = DB.search_posts_by_author_admin(search_text)
    else:
        search_results = []
    return jsonify(search_results)

@app.route('/post_admin/<string:post_id>')
def post_admin(post_id):
    print("post function called with post_id_admin:", post_id)
    user = session.get('uid', 'Login')
    post = DB.post2_detail_admin(post_id)
    print("Retrieved post data_admin:", post)
    if user != 'Login':
        check_user_admin = DB.check_user_admin(user)
    else:
        check_user_admin = False
    if post:
        post_list = DB.post2_list_admin()
        file_url = None
        for p in post_list:
            if p[0] == post_id:
                file_url = p[1].get('file_name')
                break
        post['file_name'] = file_url
        post['file_path'] = ""
        if file_url:
            try:
                file_url = DB.storage.child('student').child(post_id).child(file_url).get_url(None)
            except Exception as e:
                print("Error retrieving file URL:", str(e))
                file_url = None
        post['file_url'] = file_url
        print("Retrieved post data:", post)
        print(post['file_name'])
        print("post function called with post_id:", post_id)
        return render_template('post_admin.html', post=post, user=user, post_id=post_id, check_user_admin=check_user_admin)
    else:
        return f"Post {post_id} not found"

@app.route('/download_admin')
def download_admin():
    post_id = request.args.get('post_id')
    print("post_id:", post_id)
    if post_id:
        try:
            # get the file URL from the post details using the post_id
            post = DB.post2_detail_admin(post_id)
            print("post_admin:", post)
            file_name = post.get('file_name')
            print("file_name_admin:", file_name)
            if file_name:
                file_path = f"student/{post_id}/{file_name}"
                # Create a temporary file path to save the downloaded file
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                # Download the file from Firebase Storage
                bucket = storage.bucket()
                blob = bucket.blob(file_path)
                blob.download_to_filename(temp_file.name)
                # Create a response with the file contents
                response = make_response(send_file(temp_file.name))
                response.headers['Content-Disposition'] = f"attachment; filename={file_name}"
                return response
            else:
                return "File not found"
        except Exception as e:
            print(e)
            return "File not found"
    else:
        print("post_id:", post_id)
        return "Invalid request"

# -----------------------------------------------------------------------------------------
# 논문개시 관련 / 
# 쓰기
@app.route('/write2', methods=['GET', 'POST'])
def write2():
    user = session.get('uid', 'Login')
    if user != 'Login':
        check_user_admin = DB.check_user_admin(user)
    else:
        check_user_admin = False
    if 'uid' in session:
        uid = session.get('uid')
        if DB.check_user_admin(uid):
            if request.method == 'POST':
                if 'file' not in request.files:
                    flash("No file selected")
                    return redirect(request.url)
                file = request.files['file']
                if file.filename == '':
                    flash("File name is empty")
                    return redirect(request.url)
                if not allowed_file(file.filename):
                    flash("Only upload .pdf formatted files")
                    return redirect(request.url)
                title = request.form['title']
                content = request.form['content']
                volume = request.form['volume']
                number = request.form['number']
                uid = session.get('uid')
                author = request.form['author']
                date_posted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                DB.write2_post(title, content, volume, number, uid, author, date_posted, file)
                print("volume:", volume)
                print("number:", number)
                print("author:", author)
                return redirect(url_for('havesaved'))
            return render_template('write2.html', user=user, check_user_admin=check_user_admin)
        else:
            flash("You do not have permission to perform this action.")
            return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

@app.route('/write_done', methods=['GET', 'POST'])
def write_done():
    user = session.get('uid', 'Login')
    title = request.form['title']
    volume = request.form['volume']
    number = request.form['number']
    content = request.form['content']
    author = request.form['author']
    uid = session.get('uid')
    date_posted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    post_id = DB.write2_post(title, volume, number, content, uid, author, date_posted, request.files['file'])
    return redirect(url_for('post2_list', post_id=post_id))

# @app.route('/edit')
# def edit():
#     user = session.get('uid', 'Login')
#     return render_template('edit.html', user=user)

@app.route('/list')
@app.route('/list/<int:page>')
def post2_list(page=None):
    user = session.get('uid', 'Login')
    check_user_admin = False
    if user != 'Login':
        check_user_admin = DB.check_user_admin(user)
    if 'uid' in session:
        posts_per_page = 10
        post2_list = DB.post2_list()
        if post2_list is not None:
            total_posts = len(post2_list)
            total_pages = (total_posts - 1) // posts_per_page + 1
            if page is None or page > total_pages:
                page = total_pages
            current_page = page
            start_index = (current_page - 1) * posts_per_page
            end_index = start_index + posts_per_page
            if end_index > total_posts:
                end_index = total_posts
            current_page_posts = post2_list[start_index:end_index]
            print("Current Page:", current_page)

            return render_template('list.html', user=user, post2_list=current_page_posts, check_user_admin=check_user_admin, total_posts=total_posts, total_pages=total_pages, current_page=current_page, posts_per_page=posts_per_page)
        else:
            return "No posts found"
    else:
        return redirect(url_for('login'))

@app.route('/search', methods=['GET'])
def search():
    search_type = request.args.get('type')
    search_text = request.args.get('text')
    print('Search Type:', search_type)
    print('Search Text:', search_text)
    # Search for posts and return the search results
    if search_type == 'title':
        search_results = DB.search_posts_by_title(search_text)
    elif search_type == 'author':
        search_results = DB.search_posts_by_author(search_text)
    else:
        search_results = []

    return jsonify(search_results)

@app.route('/post/<string:post_id>')
def post(post_id):
    print("post function called with post_id:", post_id)
    user = session.get('uid', 'Login')
    post = DB.post2_detail(post_id)
    print("Retrieved post data:", post)
    if user != 'Login':
        check_user_admin = DB.check_user_admin(user)
    else:
        check_user_admin = False
    if post:
        post_list = DB.post2_list()
        file_url = None
        for p in post_list:
            if p[0] == post_id:
                file_url = p[1].get('file_name')
                break
        post['file_name'] = file_url
        post['file_path'] = ""
        if file_url:
            try:
                file_url = DB.storage.child('admin').child(post_id).child(file_url).get_url(None)
            except Exception as e:
                print("Error retrieving file URL:", str(e))
                file_url = None
        post['file_url'] = file_url
        print("Retrieved post data:", post)
        print(post['file_name'])
        print("post function called with post_id:", post_id)
        return render_template('post.html', post=post, user=user, post_id=post_id, check_user_admin=check_user_admin)
    else:
        return f"Post {post_id} not found"

@app.route('/download')
def download():
    post_id = request.args.get('post_id')

    if post_id:
        try:
            # get the file URL from the post details using the post_id
            post = DB.post2_detail(post_id)
            file_name = post.get('file_name')
            if file_name:
                file_path = f"admin/{post_id}/{file_name}"
                # Create a temporary file path to save the downloaded file
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                # Download the file from Firebase Storage
                bucket = storage.bucket()
                blob = bucket.blob(file_path)
                blob.download_to_filename(temp_file.name)
                # Create a response with the file contents
                response = make_response(send_file(temp_file.name))
                response.headers['Content-Disposition'] = f"attachment; filename={file_name}"
                return response
            else:
                return "File not found"
        except Exception as e:
            print(e)
            return "File not found"
    else:
        return "Invalid request"

# -----------------------------------------------------------------------------------------
# 논문투고 관련

# 논문투고 끝나고 메세지
@app.route('/havesaved')
def havesaved():
    return render_template('havesaved.html')

# 논문투고 쓰기 학생들이 업로드 하는곳
@app.route('/write', methods=['GET', 'POST'])
def write():
    user = session.get('uid', 'Login')
    if user != 'Login':
        check_user_admin = DB.check_user_admin(user)
    else:
        check_user_admin = False
    if 'uid' in session:
        if request.method == 'POST':
            if 'file' not in request.files:
                flash("No file selected")
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash("File name is empty")
                return redirect(request.url)
            if not allowed_file(file.filename):
                flash("Only upload .pdf formatted files")
                return redirect(request.url)
            title = request.form['title']
            content = request.form['content']
            uid = session.get('uid')
            author = request.form.get("author")
            date_posted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            DB.write_post(title, content, uid, author, date_posted, file)
            return redirect(url_for('havesaved'))
        return render_template('write.html', user=user, check_user_admin=check_user_admin)
    else:
        return redirect(url_for('login'))
    
@app.route('/post_student/<string:post_id>')
def post_student(post_id):
    print("post function called with post_id_admin:", post_id)
    user = session.get('uid', 'Login')
    post = DB.post2_detail_admin(post_id)
    print("Retrieved post data_admin:", post)
    if post:
        post_list = DB.post2_list_admin()
        file_url = None
        for p in post_list:
            if p[0] == post_id:
                file_url = p[1].get('file_name')
                break
        post['file_name'] = file_url
        post['file_path'] = ""
        if file_url:
            try:
                file_url = DB.storage.child('student').child(post_id).child(file_url).get_url(None)
            except Exception as e:
                print("Error retrieving file URL:", str(e))
                file_url = None
        post['file_url'] = file_url
        print("Retrieved post data:", post)
        print(post['file_name'])
        print("post function called with post_id:", post_id)
        return render_template('post_admin.html', post=post, user=user, post_id=post_id)
    else:
        return f"Post {post_id} not found"

@app.route('/user/<string:uid>')
def user_post(uid):
    user = session.get('uid', 'Login')
    u_post = DB.get_user(uid)
    print(u_post)
    if u_post is None:
        length = 0
    else:
        length = len(u_post)
    return render_template('userDetail.html', post=u_post, length=length, uid=uid, user=user)

# front page update related
@app.route('/user/<string:uid>')
@app.route('/front_page_update', methods=['GET', 'POST'])
def front_page_update():
    user = session.get('uid', 'Login')
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file selected")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("File name is empty")
            return redirect(request.url)

        if not allowed_file_front_page(file.filename):
            flash("Only upload .jpg, .png, or .gif files")
            return redirect(request.url)

        try:
            # Create the "posting" folder in Firebase Storage if it doesn't exist
            DB.create_posting_folder()
            # Upload the file to Firebase Storage in the "posting" folder
            download_url = DB.front_page_upload(file)
            print(f"download_url in front_page_update:${download_url}")
            flash("Front page image updated successfully")
            return redirect(url_for('index', image_url=download_url, user=user))
        except Exception as e:
            print(f"e in front_page_update${e}")
            flash("Error uploading the file")
            return redirect(request.url)
    return render_template('frontPageUpdate.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
