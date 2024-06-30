from flask import Flask, render_template, request, session, redirect,flash
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import math


local_server = True
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

    # MAIL_SERVER='smtp.gmail.com'
    # MAIL_PORT = 465
    # MAIL_USE_SSN=True
    # MAIL_USERNAME = params['gmail_user'],
    # MAIL_PASSWORD = params['gmail_pass']

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/thereadersblog"
# ye json file bnne k bad commnet out kiya h taqi dhyan rhe and json file non tech ki facility k lie bnayiy otherwise no need!
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER']=params['upload_location']
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)

'''sno, name, email, phone massage'''


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)  # these variables name must be same as database
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    massage = db.Column(db.String(120), nullable=False)
    # date= db.Column(db.String(12)) bina iske b sahi h


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)  # these variables name must be same as database
    title = db.Column(db.String(50), unique=False, nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=False)
    slug = db.Column(db.String(20), nullable=True)
    image = db.Column(db.String(20), nullable=True)
    post_tag = db.Column(db.String(50), nullable=True)


@app.route('/')
def home():
    # flash("welcome to The Reader's Blog", 'success')
    posts = Posts.query.filter_by().all()
    last=math.ceil(len(posts)/int(params['no_of_posts']))
    page= request.args.get('page')
    if not str(page).isnumeric():
        page=1
    page=int(page)

    posts=posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+int(params['no_of_posts'])]
    if page ==1:

        prev="#"
        next= f"/?page={page + 1}"
    elif page==last:
         prev = f"/?page={page - 1}"
         next="#"
    else:
        prev = f"/?page={page - 1}"
        next = f"/?page={page + 1}"

    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)


    # posts=Posts.query.filter_by().all()[0:2] or
    # posts = Posts.query.filter_by().all()[0:params['no_of_posts']]

    # return render_template('index.html', params=params,posts=posts,prev=prev, next=next)  # index.html meain main body h site ki. don't confuse with the name with index.html
    # this yellow params is just a name it could be anything the second param is above one


# When you pass params=params to render_template, you are saying "pass the dictionary params to the template, and within the template, it will be available under the name params."


@app.route('/about')
def about():
    return render_template('about.html', params=params)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # '''Add entry to the database'''
        name = request.form.get('name')  # these(green) name should be same as Sublime name and 'name', email etc.
        email = request.form.get('email')
        phone = request.form.get('phone')
        massage = request.form.get('massage')

        entry = Contacts(name=name, phone=phone, email=email,
                         massage=massage)  # lhs comes from the class which we've created above
        # and RHS from this function's variable
        db.session.add(entry)
        db.session.commit()
        flash("Thanks for submitting your details. We'll get back to you soon!",'success')
    return render_template('contact.html', params=params)


# abhi sirf .../post"/first-post"(which is a slug name) dalkr dekhna h
@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

# my variable name is login instead of dashboard
#and dashboard.html login waala page h

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session and session['user'] == params['admin_user']:
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)
    if request.method == 'POST':
        username = request.form.get('uname')  # request.form.get() post (method:user's input)request se parametes lekr ayega and the parameters in html are uname and pass
        userpass = request.form.get('pass')
        if username == params['admin_user'] and userpass == params['admin_pass']:
            # set the session variable
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)
    return render_template('login.html', params=params)


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            box_title = request.form.get("title")  # green ones  varaibles come from html and python variables are different one! and below in post variable yellows are from class Posts same as db
            tagline   = request.form.get("tline")
            slug      = request.form.get("slug")
            content   = request.form.get("content")
            image_file= request.form.get("img_file")
            date      = datetime.now()
            # print(f"Received data: title={box_title}, tagline={tagline}, slug={slug}, content={content}, image_file={image_file}")
            if sno == '0':
                post = Posts(title=box_title, slug=slug, content=content, image=image_file, post_tag=tagline,date=date,sno=sno)
                db.session.add(post)
                db.session.commit()
                # flash('Your post has been added successfully!', 'success')
                return redirect('/edit/' + str(post.sno))

            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = slug
                post.content = content
                post.image = image_file
                post.post_tag = tagline
                post.date = date
                db.session.commit()
                # flash('Your post has been edited successfully!', 'success')
                return redirect('/edit/'+ sno)
    post = Posts.query.filter_by(sno=sno).first()
    return render_template('edit.html', params=params,post=post,sno=sno)



@app.route('/delete/<string:sno>', methods=['GET', 'POST'])  # 'search bootstrap templates
def delete(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/login')



@app.route('/uploader', methods=['GET','POST'])
def uploader():
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method=='POST':
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
    return "Uploaded Successfully!"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')





if __name__ == '__main__':
    app.run(debug=True)
