from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import Integer, String, Float


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


##CREATE DATABASE
class Base(DeclarativeBase):
  pass

# Create the extension
db = SQLAlchemy(model_class=Base)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"

# initialize the app with the extension
db.init_app(app)

class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(50), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)


# Create table schema in the database.
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    result = db.session.execute(db.select(Book).order_by(Book.id))
    all_books = result.scalars()
    return render_template("index.html", list=all_books)


@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == "POST":
        new_book = Book(title=request.form["title"], author=request.form["author"], rating=request.form["rating"])
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('home'))
    else:
        return render_template('add.html')


@app.route("/edit/<int:book_id>", methods=['GET', 'POST'])
def edit(book_id):
    if request.method == "POST":
        book_to_update = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
        book_to_update.rating = request.form["new_rating"]
        db.session.commit()
        return redirect(url_for('home'))
    else:
        book = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
        b_title = book.title
        b_rating = book.rating
        return render_template('edit.html', num=book_id, title=b_title, rating=b_rating)


@app.route("/delete", methods=['GET'])
def delete():
    if request.method == "GET":
        book_id = request.args.get('id')
        book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
        db.session.delete(book_to_delete)
        db.session.commit()
        return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)

