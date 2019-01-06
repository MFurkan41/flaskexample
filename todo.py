from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:\\VSCodeFiles\\TodoApp\\todo.db'
db = SQLAlchemy(app)
app.secret_key = "todo_secret"


@app.route("/login",methods =["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data
       
        result = User.query.filter_by(username = username).first()
        if result != []:
            try:
                real_password = result.password
            except AttributeError:
                flash("Parolanızı Yanlış Girdiniz...","danger")
                return redirect(url_for("login"))

            if sha256_crypt.verify(password_entered,real_password):
                flash("Başarıyla Giriş Yaptınız...","success")

                session["logged_in"] = True
                session["username"] = username

                return redirect(url_for("index"))
            else:
                flash("Parolanızı Yanlış Girdiniz...","danger")
                return redirect(url_for("login")) 

        else:
            flash("Böyle bir kullanıcı bulunmuyor...","danger")
            return redirect(url_for("login"))

    
    return render_template("login.html",form = form)

class RegisterForm(Form):
    username = StringField("Kullanıcı Adı",validators=[validators.Length(min = 5,max = 35)])
    password = PasswordField("Parola:",validators=[
        validators.DataRequired(message = "Lütfen bir parola belirleyin"),
        validators.EqualTo(fieldname = "confirm",message="Parolanız Uyuşmuyor...")
    ])
    confirm = PasswordField("Parola Doğrulama")

class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    complete = db.Column(db.Boolean)
    author = db.Column(db.String(15))
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(50))

@app.route("/")
def index():
    author = session["username"]
    todos = Todo.query.filter_by(author=author).all()
    return render_template("index.html",todos = todos,session = session)
@app.route("/add",methods = ["POST"])
def addTodo():
    title = request.form.get("title")
    newTodo = Todo(title = title,complete = False,author = session["username"])
    db.session.add(newTodo)
    db.session.commit()

    return redirect(url_for("index"))
@app.route("/complete/<string:id>")
def completeTodo(id):
    todo = Todo.query.filter_by(id = id).first()
    todo.complete = not todo.complete
    db.session.commit()

    return redirect(url_for("index"))
@app.route("/delete/<string:id>")
def deleteTodo(id):
    todo = Todo.query.filter_by(id = id).first()
    db.session.delete(todo)
    db.session.commit()
    
    return redirect(url_for("index"))

@app.route("/register",methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        username = form.username.data
        password = sha256_crypt.encrypt(form.password.data)

        
        result = User.query.filter_by(username=username).first()
        if result != []:
            newUser = User(username=username, password=password)

            db.session.add(newUser)
            db.session.commit()

            flash("Başarıyla Kayıt Oldunuz...","success")
            return redirect(url_for("login"))
        else:
            flash("Kullanıcı ismi kullanılıyor. Lütfen başka bir kullanıcı ismi kullanınız.")
            return render_template("register.html",form = form)

    
    else:
        return render_template("register.html",form = form)

@app.route("/logout")
@login_required
def logout():
    session["logged_in"] = False
    flash("Çıkış Yaptın!","success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
