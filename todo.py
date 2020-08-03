from flask import Flask, render_template, redirect, request,session, flash
from passlib.hash import sha256_crypt
from wtforms import StringField, PasswordField, Form, validators
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from time import sleep

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////your_sqlile_file'
db = SQLAlchemy(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" in session:
            sleep(1)
            return f(*args, **kwargs)
            flash("Başarıyla giriş yaptınız","success")
        else:
            sleep(1)
            flash("Öncelikle giriş yapmalısınız","danger")
            return redirect("/login")
    return decorated_function

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String(80))
    title = db.Column(db.String(80))
    complete = db.Column(db.Boolean)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String(80))
    password = db.Column(db.String())

class LoginForm(Form):
    user = StringField("Kullanıcı Adınız :",validators=[validators.Length(min=4
    ,message="En az 4 karakter giriniz.")
    ,validators.DataRequired("Doldurulması zorunludur.")])

    password = PasswordField("Şifreniz :",validators=[validators.Length(min=8
    ,message="En az 8 karakter giriniz.")
    ,validators.DataRequired("Doldurulması zorunludur.")])



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    form = LoginForm(request.form)
    user = form.user.data.strip(" ")
    password = sha256_crypt.hash(form.password.data)

    if request.method == "POST" and form.validate():

        usertable = Users.query.filter_by(user = user).first()
        if not usertable:
            newUser = Users(user = user, password = password)
            db.session.add(newUser)
            db.session.commit()
            sleep(1)
            flash("Kullanıcı başarıyla eklendi","success")
            return redirect("/")
        else:
            sleep(1)
            flash("Bu kullanıcı sistemde zaten kayıtlı","danger")
            return redirect("/register")

    return render_template("register.html",form = form)

@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm(request.form)
    user = form.user.data
    password = form.password.data

    usertable = Users.query.filter_by(user = user).first()

    if request.method == "POST":
        if usertable:
            if sha256_crypt.verify(password,usertable.password):
                session["user"] = usertable.user
                sleep(1)
                flash("Başarıyla giriş yaptınız","success")
                return redirect("/todo")
            else:
                sleep(1)
                flash("Şifrenizi yanlış giriniz","danger")
                return redirect("/login")
        else:
            sleep(1)
            flash("Kullanıcı adınızı yanlış girdiniz","danger")
            return redirect("/login")

    return render_template("login.html",form = form)
        
@app.route("/logout",methods = ["POST"])
def logout():
    if request.method == "POST":
        session.clear()
        sleep(1)
        flash("Başarıyla çıkış yapıldı","success")
        return redirect("/")

@app.route("/todo")
@login_required
def todo():
    todos = Todo.query.all()
    logged_user = session["user"]
    return render_template("todo.html",todos = todos,logged_user = logged_user)

@app.route("/add",methods = ["POST"])
def add():
    if request.method == "POST":
        title = request.form.get("title")
        logged_user = session["user"]
        newTodo = Todo(user = logged_user, title = title, complete = False)
        db.session.add(newTodo)
        db.session.commit()
        return redirect("/todo")

@app.route("/update",methods=["POST"])
def update():
    if request.method == "POST":
        todos = Todo.query.filter_by(user = session["user"])
        for todo in todos:

            get_id = request.form.get("complete"+str(todo.id))
            if get_id:
                todo.complete = True
                db.session.commit()
            else:
                todo.complete = False
                db.session.commit()
        

            get_del = request.form.get("delete"+str(todo.id))
            if get_del:
                get_del_id = int(get_del)
                todo = Todo.query.filter_by(id = get_del_id).first()
                db.session.delete(todo)
                db.session.commit()

        flash("Güncelleme başarılı","success")
        return redirect("/todo")



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
