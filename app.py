from flask import Flask, render_template, jsonify, request, make_response, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_bcrypt import Bcrypt
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename
import os
import re
import json
import jsonpickle
from json import JSONEncoder

import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:nikolatesla@localhost:5432/postgres'

app.secret_key = "123nikola4tiasxtesla314"

db = SQLAlchemy(app)

migrate = Migrate(app, db)

bcrypt = Bcrypt(app)


class Produkt(db.Model):
    __tablename__ = 'produkt'
    id_produkt = db.Column(db.Integer, primary_key=True)
    ime = db.Column(db.String(30), nullable=False)
    poteklo = db.Column(db.String(30), nullable=True)
    brend = db.Column(db.String(30), nullable=False)

    def __init__(self, id_produkt, ime, poteklo, brend):
        self.id_produkt = id_produkt
        self.ime = ime
        self.poteklo = poteklo
        self.brend = brend


class Admin(db.Model):
    __tablename__ = 'admin'
    id_admin = db.Column(db.Integer, primary_key=True)

    def __init__(self, id_admin):
        self.id_admin = id_admin


class Cena(db.Model):
    __tablename__ = 'cena'
    datum_od = db.Column(db.Date, primary_key=True)
    datum_do = db.Column(db.Date)
    vrednost = db.Column(db.Integer, nullable=False)
    id_produkt = db.Column(db.Integer, nullable=False, primary_key=True)

    def __init__(self, datum_od, datum_do, vrednost, id_produkt):
        self.datum_od = datum_od
        self.datum_do = datum_do
        self.vrednost = vrednost
        self.id_produkt = id_produkt


class Faktura(db.Model):
    __tablename__ = 'faktura'
    faktura_id = db.Column(db.Integer, primary_key=True)
    datum = db.Column(db.Date, nullable=False)
    br_pratka = db.Column(db.Integer, nullable=False, primary_key=True)

    def __init__(self, faktura_id, datum, br_pratka):
        self.faktura_id = faktura_id
        self.datum = datum
        self.br_pratka = br_pratka


class Korisnik(db.Model):
    __tablename__ = 'korisnik'
    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    ime = db.Column(db.String(30), nullable=False)
    prezime = db.Column(db.String(30), nullable=False)

    def __init__(self, id_user, username, password, ime, prezime):
        self.id_user = id_user
        self.username = username
        self.password = password
        self.ime = ime
        self.prezime = prezime


class Klient(db.Model):
    __tablename__ = 'klient'
    id_klient = db.Column(db.Integer, primary_key=True)
    poeni = db.Column(db.Integer)
    grad = db.Column(db.String(30), nullable=False)

    def __init__(self, id_klient, poeni, grad):
        self.id_klient = id_klient
        self.poeni = poeni
        self.grad = grad


class Magacin(db.Model):
    __tablename__ = 'magacin'
    id_magacin = db.Column(db.Integer, primary_key=True)
    grad = db.Column(db.String(20), nullable=False)

    def __init__(self, id_magacin, grad):
        self.id_magacin = id_magacin
        self.grad = grad


class MomentalniPordukti(db.Model):
    __tablename__ = 'momentalni_produkti'
    id_magacin = db.Column(db.Integer, primary_key=True)
    id_produkt = db.Column(db.Integer, primary_key=True)

    def __init__(self, id_magacin, id_produkt):
        self.id_magacin = id_magacin
        self.id_produkt = id_produkt


class NapraveniNarachki(db.Model):
    __tablename__ = 'napraveni_narachki'
    id_produkt = db.Column(db.Integer, primary_key=True)
    br_pratka = db.Column(db.Integer, primary_key=True)

    def __init__(self, id_produkt, br_pratka):
        self.id_produkt = id_produkt
        self.br_pratka = br_pratka


class OdrzuvanjeMagacini(db.Model):
    __tablename__ = 'odrzuvanje_magacini'
    id_magacin = db.Column(db.Integer, primary_key=True)
    id_admin = db.Column(db.Integer, primary_key=True)

    def __init__(self, id_magacin, id_admin):
        self.id_magacin = id_magacin
        self.id_admin = id_admin


class Narachka(db.Model):
    __tablename__ = 'narachka'

    br_pratka = db.Column(db.Integer, primary_key=True)
    pratka_status = db.Column(db.CHAR(1), nullable=False)
    kolicina = db.Column(db.Integer, nullable=False)
    id_user = db.Column(db.Integer, nullable=False)

    def __init__(self, br_pratka, pratka_status, kolicina, id_user):
        self.br_pratka = br_pratka
        self.pratka_status = pratka_status
        self.kolicina = kolicina
        self.id_user = id_user


class napraveni_narachki_od_klienti(db.Model):
    __tablename__ = 'Napraveni narachki od klient'
    ime = db.Column(db.String(30), nullable=False)
    prezime = db.Column(db.String(30), nullable=False)
    datum = db.Column(db.Date,nullable=False)
    br_pratka = db.Column(db.Integer, nullable=False,primary_key=True)
    pratka_status = db.Column(db.CHAR(1), nullable=False)
    kolicina = db.Column(db.Integer, nullable=False)

    def __init__(self, ime, prezime, br_pratka, pratka_status, kolicina):
        self.ime = ime
        self.prezime = prezime
        self.br_pratka = br_pratka
        self.pratka_status = pratka_status
        self.kolicina = kolicina

# @app.route('/')  # root route
# def index():
#    products = Produkt.query.all()
#    return render_template('index.html', data=products)

@app.route("/")
def homepage():
    products = Produkt.query.all()
    my_products = [products[i] for i in range(8, 12)]
    return render_template('homepage.html', products=my_products)


@app.route("/products")
def products():
    result = Produkt.query.all()
    data = []
    for i in range(0, len(result)):
        id_produkt = result[i].id_produkt
        cena = Cena.query.filter_by(id_produkt=id_produkt).first()
        item = {
            'produkt': result[i],
            'cena': cena
        }
        data.append(item)
        i += 1
    return render_template('products.html', products=result, data=data)


@app.route("/products/<int:product_id>")
def product(product_id):
    pr = Produkt.query.filter_by(id_produkt=product_id).first()
    cena = Cena.query.filter_by(id_produkt=product_id).first()
    return render_template('product.html', product=pr, cena=cena)


@app.route("/products/shoes")
def product_shoes():
    result = Produkt.query.all()
    my_products = [result[i] for i in range(1, 17)]
    data = []
    for i in range(0, len(result)):
        id_produkt = result[i].id_produkt
        cena = Cena.query.filter_by(id_produkt=id_produkt).first()
        item = {
            'produkt': result[i],
            'cena': cena
        }
        data.append(item)
        i += 1
    return render_template('products.html', products=my_products, data=data)


@app.route("/products/hoodies")
def product_hoodies():
    result = Produkt.query.all()
    my_products = [result[i] for i in range(17, 22)]
    data = []
    for i in range(0, len(result)):
        id_produkt = result[i].id_produkt
        cena = Cena.query.filter_by(id_produkt=id_produkt).first()
        item = {
            'produkt': result[i],
            'cena': cena
        }
        data.append(item)
        i += 1
    return render_template('products.html', products=my_products, data=data)


@app.route("/admin")
def admin():
    result = napraveni_narachki_od_klienti.query.all()
    return render_template('admin.html', result=result)


@app.route("/profile")
def profile():
    result_wish_list = session['wish_list']
    narachki = Narachka.query.filter_by(id_user=session['user_id']).all()
    data = []
    for narachka in narachki:
        suma = 0
        br_pratka = narachka.br_pratka
        produkti = NapraveniNarachki.query.filter_by(br_pratka=br_pratka).all()
        faktura = Faktura.query.filter_by(br_pratka=br_pratka).first()
        for produkt_order in produkti:
            cena = Cena.query.filter_by(id_produkt=produkt_order.id_produkt).first()
            suma = suma + cena.vrednost

        # datum=datetime.datetime.now()
        # if faktura.datum is not None:
        #    datum=faktura.datum

        item = {
            'narachka': br_pratka,
            'total': suma,
            'date': faktura.datum
        }

        data.append(item)

    decode1 = []
    load1 = []
    for el in result_wish_list:
        decode1.append(jsonpickle.decode(el))

    for el in decode1:
        load1.append(json.loads(el))

    my_user = Korisnik.query.filter_by(username=session['username']).first()

    if session['username'] == 'admin':
        return redirect(url_for('admin'))

    return render_template('profile.html', user=my_user, wish_list=load1, data=data)


@app.route("/profile/<int:user_id>")
def profile_info(user_id):
    user = Korisnik.query.filter_by(id_user=user_id).first()
    klient = Klient.query.filter_by(id_klient=user_id).first()
    if user_id != session['user_id']:
        return render_template('/errors/404.html')

    if session['username'] == 'admin':
        return redirect(url_for('admin'))

    return render_template('/user/user.html', my_user=user, klient=klient)


@app.route("/order", methods=["POST"])
def order():
    # total = request.form['shuma']
    result_shopping_cart = session['shopping_cart']
    decode2 = []
    load2 = []

    for el in result_shopping_cart:
        decode2.append(jsonpickle.decode(el))

    for el in decode2:
        load2.append(json.loads(el))
    # order_date, handling_cost, order_address, user_id
    suma = 0
    for pr in load2:
        suma = suma + pr['cena']['vrednost']

    username = session['username']
    my_user = Korisnik.query.filter_by(username=username).first()
    klient = Klient.query.filter_by(id_klient=my_user.id_user)
    # klient['poeni'] = klient['poeni'] + 5

    last_order = Narachka.query.order_by(Narachka.br_pratka.desc()).first()
    order_number = last_order.br_pratka + 1

    narachka = Narachka(order_number, 'S', 1, my_user.id_user)

    db.session.add(narachka)
    db.session.commit()

    last_faktura = Faktura.query.order_by(Faktura.faktura_id.desc()).first()
    f_id = last_faktura.faktura_id + 1

    date_now = datetime.datetime.now()

    faktura = Faktura(f_id, date_now, order_number)

    db.session.add(faktura)
    db.session.commit()

    for pr in load2:
        nn = NapraveniNarachki(pr['produkt']['id_produkt'], order_number)
        db.session.add(nn)
        db.session.commit()

    session['shopping_cart'] = []

    if session['username'] == 'admin':
        return redirect(url_for('admin'))

    return redirect(url_for('profile'))


@app.route("/order/<int:order_number>/details")
def view_order(order_number):
    nn = NapraveniNarachki.query.filter_by(br_pratka=order_number)

    korisnik = Korisnik.query.filter_by(username=session['username']).first()
    klient = Klient.query.filter_by(id_klient=korisnik.id_user).first()
    products_list = []
    data = []
    for item in nn:
        product = Produkt.query.filter_by(id_produkt=item.id_produkt).first()
        cena = Cena.query.filter_by(id_produkt=item.id_produkt).first()

        qr = {
            'produkt': product,
            'cena': cena
        }
        data.append(qr)

    return render_template('order_products.html', data=data, user=korisnik, klient=klient, order_number=order_number)


@app.route("/shop")
def shop():
    result_shopping_cart = session['shopping_cart']
    decode2 = []
    load2 = []

    for el in result_shopping_cart:
        decode2.append(jsonpickle.decode(el))

    for el in decode2:
        load2.append(json.loads(el))

    suma = 0
    for item in load2:
        suma = suma + item['cena']['vrednost']

    return render_template('shop.html', shopping_cart=load2, total=suma)


@app.route("/remove_item_profile/<int:product_id>")
def remove_item_profile(product_id):
    result_shopping_cart = session['wish_list']
    decode2 = []
    load2 = []
    for el in result_shopping_cart:
        decode2.append(jsonpickle.decode(el))

    for el in decode2:
        load2.append(json.loads(el))

    suma = 0
    i = 0
    index = None
    for product in load2:
        if product['produkt']['id_produkt'] == product_id:
            index = i
        else:
            suma = suma + product['cena']['vrednost']
        i = i + 1

    lista = []
    load2.pop(index)
    for pr in load2:
        prJSON = jsonpickle.encode(pr, unpicklable=False)
        resultJSON = json.dumps(prJSON, indent=4)
        lista.append(resultJSON)

    session['wish_list'] = lista

    if session['username'] == 'admin':
        return redirect(url_for('admin'))

    return redirect(url_for('profile'))


@app.route("/remove_item/<int:product_id>")
def remove(product_id):
    result_shopping_cart = session['shopping_cart']
    decode2 = []
    load2 = []
    for el in result_shopping_cart:
        decode2.append(jsonpickle.decode(el))

    for el in decode2:
        load2.append(json.loads(el))

    suma = 0
    i = 0
    index = 0
    for product in load2:
        if product['produkt']['id_produkt'] == product_id:
            index = i
        else:
            suma = suma + product['cena']['vrednost']
            i = i + 1

    lista = []

    load2.pop(index)
    for pr in load2:
        prJSON = jsonpickle.encode(pr, unpicklable=False)
        resultJSON = json.dumps(prJSON, indent=4)
        lista.append(resultJSON)

    session['shopping_cart'] = lista

    return redirect(url_for('shop'))


@app.route("/add_to_cart_profile/<int:product_id>")
def add_to_cart_profile(product_id):
    pr = Produkt.query.filter_by(id_produkt=product_id).first()
    cena = Cena.query.filter_by(id_produkt=product_id).first()
    data = {
        'produkt': pr,
        'cena': cena
    }
    prJSON = jsonpickle.encode(data, unpicklable=False)
    resultJSON = json.dumps(prJSON, indent=4)
    lista = session['shopping_cart']
    lista.append(resultJSON)
    session['shopping_cart'] = lista

    if session['username'] == 'admin':
        return redirect(url_for('admin'))

    return redirect(url_for('profile'))


@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    pr = Produkt.query.filter_by(id_produkt=product_id).first()
    cena = Cena.query.filter_by(id_produkt=product_id).first()
    data = {
        'produkt': pr,
        'cena': cena
    }
    prJSON = jsonpickle.encode(data, unpicklable=False)
    resultJSON = json.dumps(prJSON, indent=4)
    lista = session['shopping_cart']
    lista.append(resultJSON)
    session['shopping_cart'] = lista
    return redirect(url_for('products'))


@app.route("/add_to_wish_list/<int:product_id>")
def add_to_wish_list(product_id):
    pr = Produkt.query.filter_by(id_produkt=product_id).first()
    cena = Cena.query.filter_by(id_produkt=product_id).first()
    data = {
        'produkt': pr,
        'cena': cena
    }
    prJSON = jsonpickle.encode(data, unpicklable=False)
    resultJSON = json.dumps(prJSON, indent=4)
    lista = session['wish_list']
    lista.append(resultJSON)
    session['wish_list'] = lista
    return redirect(url_for('products'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if not_empty([username, password]):
            if check_user(username):
                my_user = Korisnik.query.filter_by(username=username).first()
                if password == my_user.password:
                    session['is_logged_in'] = True
                    session['username'] = my_user.username
                    session['email'] = ""
                    session['wish_list'] = []
                    session['shopping_cart'] = []
                    session['user_id'] = my_user.id_user
                    if username == 'admin':
                        return redirect(url_for('admin'))
                    return redirect(url_for("profile"))
                    # return "Uspesno logged in"
                else:
                    flash('Password is incorrect!')
            else:
                flash('This username does not exist')
        else:
            flash('Please enter your credentials!')
        return redirect(url_for('login'))
    else:
        try:
            if session['is_logged_in'] == True:
                my_user = Korisnik.query.filter_by(username=session['username']).first()
                if session['username'] == 'admin':
                    return redirect(url_for('admin'))

                return redirect(url_for('profile'))
        except KeyError:
            session['is_logged_in'] = False
            return redirect(url_for('login'))
        return render_template('/auth/login.html')


@app.route("/logout")
def logout():
    session['is_logged_in'] = False
    session['username'] = ""
    session['email'] = ""
    session['wish_list'] = []
    session['shopping_cart'] = []
    session['user_id'] = None
    return redirect(url_for('homepage'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        surname = request.form['surname']
        date = request.form['date_of_birth']
        email = request.form['email']
        telephone = request.form['telephone']
        username = request.form['username']
        password = request.form['password']
        address = request.form['address']
        confirm_password = request.form['confirm_password']
        if not_empty([name, surname, date, email, telephone, username, password, confirm_password]):
            if validate_mail(email):
                if not check_mail(email):
                    if not check_user(username):
                        if check_password(password, confirm_password):
                            if not check_phone(telephone):
                                # password_hash = bcrypt.generate_password_hash(password)
                                last_korisnik = Korisnik.query.order_by(Korisnik.id_user.desc()).first()
                                my_id = last_korisnik.id_user + 1
                                korisnik = Korisnik(my_id, username, password, name, surname)
                                db.session.add(korisnik)
                                db.session.commit()
                                klient = Klient(my_id, 0, address)
                                db.session.add(klient)
                                db.session.commit()
                                session['is_logged_in'] = True
                                session['username'] = korisnik.username
                                session['email'] = ""
                                session['wish_list'] = []
                                session['shopping_cart'] = []
                                session['user_id'] = korisnik.id_user
                                return redirect(url_for("profile", user=korisnik))
                            else:
                                flash("Please enter a valid telephone number!")
                        else:
                            flash("Password don't match!")
                    else:
                        flash("This username already exists")
                else:
                    flash("This mail is already registered!")
            else:
                flash("Please enter a valid mail!")
        else:
            flash("Please fill all fields!")
        return redirect(url_for('register'))
    else:
        if session['is_logged_in']:
            if session['username'] == 'admin':
                return redirect(url_for('admin'))

            return redirect(url_for('profile'))
        return render_template('/auth/register.html')


@app.route("/brands")
def brands():
    return "Brands here..."


def validate_mail(mail):
    return re.search("[\w\.\_\-]+\@[\w\-]+\.[a-z]{2,5}", mail) != None


def not_empty(args):
    for arg in args:
        if len(arg) == 0:
            return False
    return True


def check_password(password1, password2):
    if password1 == password2:
        return True
    else:
        return False


def check_mail(mail):
    return False


def check_user(username):
    user = Korisnik.query.filter_by(username=username).first()
    if user:
        return True
    else:
        return False


def check_phone(number):
    return any(char.isalpha() for char in number)


if __name__ == "__main__":
    app.run(debug=True)
