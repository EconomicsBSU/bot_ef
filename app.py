from flask import Flask, render_template, request, redirect, flash, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from datetime import timedelta
from io import BytesIO
import mimetypes
import base64
import os


app = Flask(__name__)

# Указываем путь к базе данных в папке instance
db_path = os.path.join(app.instance_path, 'form.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB память для фото

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # Действие сессии 1 час

Session(app)

# Создаем папку instance, если она не существует
os.makedirs(app.instance_path, exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.secret_key = '0123456789'


# База данных

class GeneralInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comandName = db.Column(db.Text, nullable=False)
    schoolName = db.Column(db.Text, nullable=False)
    cityName = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Mentor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mName = db.Column(db.Text, nullable=False)
    mPost = db.Column(db.Text, nullable=False)
    memail = db.Column(db.Text, nullable=False)
    mphoneNumber = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class CaptainInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    captainName = db.Column(db.Text, nullable=False)
    captainClass = db.Column(db.Integer, nullable=False)
    cemail = db.Column(db.Text, nullable=False)
    cphoneNumber = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Participant1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uch1Name = db.Column(db.Text, nullable=False)
    uch1Class = db.Column(db.Integer, nullable=False)
    uch1email = db.Column(db.Text, nullable=False)
    uch1phoneNumber = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Participant2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uch2Name = db.Column(db.Text, nullable=False)
    uch2Class = db.Column(db.Integer, nullable=False)
    uch2email = db.Column(db.Text, nullable=False)
    uch2phoneNumber = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Participant3(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uch3Name = db.Column(db.Text, nullable=False)
    uch3Class = db.Column(db.Integer, nullable=False)
    uch3email = db.Column(db.Text, nullable=False)
    uch3phoneNumber = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text, nullable=False)  # Имя файла
    data = db.Column(db.LargeBinary, nullable=False)  # Содержимое файла
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # username = db.Column(db.Text, nullable=False, unique=True)
    general_information = db.relationship('GeneralInformation', backref='user', lazy=True)
    mentor = db.relationship('Mentor', backref='user', lazy=True)
    captain_info = db.relationship('CaptainInfo', backref='user', lazy=True)
    participant_1 = db.relationship('Participant1', backref='user', lazy=True)
    participant_2 = db.relationship('Participant2', backref='user', lazy=True)
    participant_3 = db.relationship('Participant3', backref='user', lazy=True)
    photo = db.relationship('Photo', backref='user', lazy=True)


# Создание таблиц
with app.app_context():
    try:
        # db.drop_all()
        db.create_all()
        print(f"База данных создана по пути: {db_path}")
    except Exception as e:
        print(f"Ошибка создания базы данных: {e}")


@app.route("/")

@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/selection')
def selection():
    return render_template('selection.html')


@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')


@app.route('/create_user', methods=['POST', 'GET'])
def create_user():
    if 'current_user_id' in session:
        flash("Вы уже зарегистрированы. Для повторной регистрации закройте браузер.")
        return redirect('/general_information')

    # Создаем нового пользователя
    new_user = User()
    db.session.add(new_user)
    db.session.commit()

    # Сохраняем ID нового пользователя в сессии
    session['current_user_id'] = new_user.id

    flash(f"Создан новый пользователь с ID {new_user.id}.")
    return redirect('/general_information')


@app.route('/general_information', methods=['POST', 'GET'])
def general_information():
    current_user_id = session.get('current_user_id')
    if not current_user_id:
        flash("Не удалось определить текущего пользователя. Начните заново.")
        return redirect('/create_user')

    # Проверяем, существует ли запись для текущего пользователя
    existing_info = GeneralInformation.query.filter_by(user_id=session['current_user_id']).first()

    if request.method == 'POST':
        comandName = request.form['comandName']
        schoolName = request.form['schoolName']
        cityName = request.form['cityName']

        if existing_info:
            # Обновляем существующую запись
            existing_info.comandName = comandName
            existing_info.schoolName = schoolName
            existing_info.cityName = cityName
        else:
            # Создаём новую запись
            post = GeneralInformation(
                comandName=comandName,
                schoolName=schoolName,
                cityName=cityName,
                user_id=current_user_id
            )
            db.session.add(post)

        try:
            db.session.commit()
            return redirect('/mentor')
        except Exception as e:
            return f'Ошибка: {e}'

    # Передаём существующие данные в шаблон, если они есть
    return render_template('general_information.html', info=existing_info)


@app.route('/mentor', methods=['POST', 'GET'])
def mentor():
    current_user_id = session.get('current_user_id')
    if not current_user_id:
        flash("Не удалось определить текущего пользователя. Начните заново.")
        return redirect('/create_user')

    existing_mentor = Mentor.query.filter_by(user_id=session['current_user_id']).first()

    if request.method == 'POST':
        mName = request.form['mName']
        mPost = request.form['mPost']
        memail = request.form['memail']
        mphoneNumber = request.form['mphoneNumber']

        if existing_mentor:
            # Обновляем данные
            existing_mentor.mName = mName
            existing_mentor.mPost = mPost
            existing_mentor.memail = memail
            existing_mentor.mphoneNumber = mphoneNumber
        else:
            # Создаём новую запись
            post = Mentor(
                mName=mName,
                mPost=mPost,
                memail=memail,
                mphoneNumber=mphoneNumber,
                user_id=current_user_id
            )
            db.session.add(post)

        try:
            db.session.commit()
            return redirect('/captain_info')
        except Exception as e:
            return f'Ошибка: {e}'

    return render_template('mentor.html', mentor=existing_mentor)


@app.route('/captain_info', methods=['POST', 'GET'])
def captain_info():
    current_user_id = session.get('current_user_id')
    if not current_user_id:
        flash("Не удалось определить текущего пользователя. Начните заново.")
        return redirect('/create_user')

    existing_captain = CaptainInfo.query.filter_by(user_id=session['current_user_id']).first()

    if request.method == 'POST':
        captainName = request.form['captainName']
        captainClass = request.form['captainClass']
        cemail = request.form['cemail']
        cphoneNumber = request.form['cphoneNumber']

        if existing_captain:
            # Обновляем данные
            existing_captain.captainName = captainName
            existing_captain.captainClass = captainClass
            existing_captain.cemail = cemail
            existing_captain.cphoneNumber = cphoneNumber
        else:

            post = CaptainInfo(
                captainName=captainName,
                captainClass=captainClass,
                cemail=cemail,
                cphoneNumber=cphoneNumber,
                user_id=current_user_id
            )
            db.session.add(post)

        try:
            db.session.commit()
            return redirect('/participant_1')

        except Exception as e:
            return f'Ошибка: {e}'

    return render_template('captain_info.html', captain=existing_captain)  # Возвращаем HTML-страницу для GET-запросов


@app.route('/participant_1', methods=['POST', 'GET'])
def participant_1():
    current_user_id = session.get('current_user_id')
    if not current_user_id:
        flash("Не удалось определить текущего пользователя. Начните заново.")
        return redirect('/create_user')

    # Проверка наличия данных участника в базе
    existing_participant_1 = Participant1.query.filter_by(user_id=session['current_user_id']).first()

    if request.method == 'POST':
        uch1Name = request.form['uch1Name']
        uch1Class = request.form['uch1Class']
        uch1email = request.form['uch1email']
        uch1phoneNumber = request.form['uch1phoneNumber']

        if existing_participant_1:
            # Обновляем данные участника
            existing_participant_1.uch1Name = uch1Name
            existing_participant_1.uch1Class = uch1Class
            existing_participant_1.uch1email = uch1email
            existing_participant_1.uch1phoneNumber = uch1phoneNumber
        else:
            # Добавляем нового участника
            post = Participant1(
                uch1Name=uch1Name,
                uch1Class=uch1Class,
                uch1email=uch1email,
                uch1phoneNumber=uch1phoneNumber,
                user_id=current_user_id
            )
            db.session.add(post)

        try:
            db.session.commit()
            return redirect('/participant_2')
        except Exception as e:
            return f"Ошибка: {e}"

    return render_template('participant_1.html', participant_1=existing_participant_1)  # Возвращаем HTML-страницу для GET-запросов


@app.route('/participant_2', methods=['POST', 'GET'])
def participant_2():
    current_user_id = session.get('current_user_id')
    if not current_user_id:
        flash("Не удалось определить текущего пользователя. Начните заново.")
        return redirect('/create_user')

    # Проверка наличия данных участника в базе
    existing_participant_2 = Participant2.query.filter_by(user_id=session['current_user_id']).first()

    if request.method == 'POST':
        uch2Name = request.form['uch2Name']
        uch2Class = request.form['uch2Class']
        uch2email = request.form['uch2email']
        uch2phoneNumber = request.form['uch2phoneNumber']

        if existing_participant_2:
            # Обновляем данные участника
            existing_participant_2.uch2Name = uch2Name
            existing_participant_2.uch2Class = uch2Class
            existing_participant_2.uch2email = uch2email
            existing_participant_2.uch2phoneNumber = uch2phoneNumber
        else:
            # Добавляем нового участника
            post = Participant2(
                uch2Name=uch2Name,
                uch2Class=uch2Class,
                uch2email=uch2email,
                uch2phoneNumber=uch2phoneNumber,
                user_id=current_user_id
            )
            db.session.add(post)

        try:
            db.session.commit()
            return redirect('/participant_3')
        except Exception as e:
            return f"Ошибка: {e}"

    return render_template('participant_2.html', participant_2=existing_participant_2)  # Возвращаем HTML-страницу для GET-запросов


@app.route('/participant_3', methods=['POST', 'GET'])
def participant_3():
    current_user_id = session.get('current_user_id')
    if not current_user_id:
        flash("Не удалось определить текущего пользователя. Начните заново.")
        return redirect('/create_user')

    # Проверка наличия данных участника в базе
    existing_participant_3 = Participant3.query.filter_by(user_id=current_user_id).first()

    if request.method == 'POST':
        # Проверка, что кнопка "Нет участника" была нажата
        no_participant = request.form.get('noParticipant') == 'true'

        if no_participant:
            # Удаляем запись, если она существует
            if existing_participant_3:
                db.session.delete(existing_participant_3)
                try:
                    db.session.commit()
                except Exception as e:
                    return f"Ошибка: {e}"
            return redirect('/photo')  # Переход на страницу "Фото"

        # Иначе обрабатываем обычное обновление данных
        uch3Name = request.form.get('uch3Name', '').strip()
        uch3Class = request.form.get('uch3Class', '0').strip()  # Значение по умолчанию 0 для класса
        uch3email = request.form.get('uch3email', '').strip()
        uch3phoneNumber = request.form.get('uch3phoneNumber', '').strip()

        if existing_participant_3:
            # Обновляем данные участника
            existing_participant_3.uch3Name = uch3Name
            existing_participant_3.uch3Class = int(uch3Class) if uch3Class.isdigit() else 0
            existing_participant_3.uch3email = uch3email
            existing_participant_3.uch3phoneNumber = uch3phoneNumber
        else:
            # Если данных нет, создаем новую запись
            post = Participant3(
                uch3Name=uch3Name,
                uch3Class=int(uch3Class) if uch3Class.isdigit() else 0,
                uch3email=uch3email,
                uch3phoneNumber=uch3phoneNumber,
                user_id=current_user_id
            )
            db.session.add(post)

        try:
            db.session.commit()
            return redirect('/photo')  # Переход на страницу "Фото"
        except Exception as e:
            return f"Ошибка: {e}"  # Отладочные данные в случае ошибки

    return render_template('participant_3.html', participant_3=existing_participant_3)


@app.route('/clear_participant_data', methods=['POST'])
def clear_participant_data():
    current_user_id = session.get('current_user_id')
    if not current_user_id:
        flash("Не удалось определить текущего пользователя. Начните заново.")
        return redirect('/create_user')

    # Проверка наличия данных участника в базе
    existing_participant_3 = Participant3.query.filter_by(user_id=current_user_id).first()

    if existing_participant_3:
        # Очищаем данные участника
        existing_participant_3.uch3Name = ''
        existing_participant_3.uch3Class = 0
        existing_participant_3.uch3email = ''
        existing_participant_3.uch3phoneNumber = ''
        try:
            db.session.commit()
            return '', 200  # Успешное очищение
        except Exception as e:
            return f"Ошибка очистки данных: {e}", 400
    else:
        return "Нет данных для очистки", 404


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Разрешенные форматы файлов

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/photo', methods=['GET', 'POST'])
def photo():
    current_user_id = session.get('current_user_id')
    if not current_user_id:
        flash("Не удалось определить текущего пользователя. Начните заново.")
        return redirect('/create_user')

    # Получаем существующую фотографию для текущего пользователя
    existing_photo = Photo.query.filter_by(user_id=current_user_id).first()

    if request.method == 'POST':
        file = request.files.get('file', None)
        existing_photo_name = request.form.get('existing_photo', None)
        original_file_name = request.form.get('original_file_name', None)

        if file and file.filename != '':
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)  # Имя файла остается оригинальным
                if existing_photo:
                    db.session.delete(existing_photo)
                    db.session.commit()

                new_photo = Photo(filename=filename, data=file.read(), user_id=current_user_id)
                db.session.add(new_photo)
                db.session.commit()

                session['last_uploaded_image'] = filename
                flash("Фото успешно загружено!")
                return redirect('/final_check')

        elif existing_photo_name:
            try:
                if existing_photo_name.startswith("data:image"):
                    # Преобразование base64 в данные изображения
                    header, encoded = existing_photo_name.split(",", 1)
                    img_data = base64.b64decode(encoded)
                    filename = secure_filename(original_file_name) if original_file_name else f"{current_user_id}_image.jpg"

                    if existing_photo:
                        db.session.delete(existing_photo)
                        db.session.commit()

                    new_photo = Photo(filename=filename, data=img_data, user_id=current_user_id)
                    db.session.add(new_photo)
                    db.session.commit()

                    session['last_uploaded_image'] = filename
                    flash("Фото успешно сохранено!")
                    return redirect('/final_check')
                else:
                    flash('Некорректное изображение.')
                    return redirect(request.url)
            except Exception as e:
                flash(f"Ошибка обработки изображения: {e}")
                return redirect(request.url)
        else:
            flash('Файл не был загружен.')
            return redirect(request.url)

    # Передаем сам объект фотографии в шаблон, а не только имя файла
    return render_template('photo.html', existing_photo=existing_photo, user_id=current_user_id)


############# Фото из final_check #############

# @app.route('/photo', methods=['GET', 'POST'])
# def photo():
#     # Получение текущего пользователя
#     current_user_id = session.get('current_user_id')
#     if not current_user_id:
#         flash("Не удалось определить текущего пользователя. Начните заново.")
#         return redirect('/create_user')
#
#     # Загрузка данных фотографии для текущего пользователя
#     photo = Photo.query.filter_by(user_id=current_user_id).first()
#
#     if request.method == 'POST':
#         # Обновление фотографии, если файл был загружен
#         if 'file' in request.files:
#             file = request.files['file']
#             if file.filename != '':
#                 # Удаляем старое фото, если оно есть
#                 existing_photo = Photo.query.filter_by(user_id=current_user_id).first()
#                 if existing_photo:
#                     db.session.delete(existing_photo)
#                     db.session.commit()
#
#                 filename = secure_filename(file.filename)
#                 new_photo = Photo(filename=filename, data=file.read(), user_id=current_user_id)
#                 db.session.add(new_photo)
#                 db.session.commit()
#
#         try:
#             db.session.commit()
#             return redirect('/final_check')
#         except Exception as e:
#             return f'Ошибка сохранения данных: {e}'
#
#     # Передача данных в шаблон
#     return render_template(
#         'photo.html',
#         photo_id=photo.id if photo else None,
#         photo_filename=photo.filename if photo else None
#     )

############# Фото без дозагрузки (изначальное) #############

# @app.route('/photo', methods=['GET', 'POST'])
# def photo():
#     current_user_id = session.get('current_user_id')
#     if not current_user_id:
#         flash("Не удалось определить текущего пользователя. Начните заново.")
#         return redirect('/create_user')
#
#     if request.method == 'POST':
#         file = request.files.get('file', None)
#         existing_photo_name = request.form.get('existing_photo', None)
#         original_file_name = request.form.get('original_file_name', None)  # Получаем оригинальное имя файла
#
#         print("Файл:", file)
#         print("Существующее фото:", existing_photo_name)
#         print("Оригинальное имя файла:", original_file_name)
#
#         # Если файл выбран, сохраняем его
#         if file and file.filename != '':
#             if allowed_file(file.filename):
#                 filename = secure_filename(file.filename)  # Используем оригинальное имя файла
#                 new_photo = Photo(filename=filename, data=file.read(), user_id=current_user_id)
#
#                 try:
#                     db.session.add(new_photo)
#                     db.session.commit()
#                     session['last_uploaded_image'] = filename
#                     flash("Фото успешно загружено!")
#                     return redirect('/final_check')
#                 except Exception as e:
#                     flash(f"Ошибка сохранения изображения: {e}")
#                     return redirect(request.url)
#
#         # Если файл не был выбран, но есть существующее фото (в base64)
#         elif existing_photo_name:
#             try:
#                 if existing_photo_name.startswith("data:image"):
#                     header, encoded = existing_photo_name.split(",", 1)
#                     img_data = base64.b64decode(encoded)
#
#                     # Используем оригинальное имя файла или задаем имя по умолчанию
#                     filename = secure_filename(original_file_name) if original_file_name else "uploaded_image.jpg"
#
#                     # Сохраняем изображение в базе данных
#                     new_photo = Photo(filename=filename, data=img_data, user_id=current_user_id)
#                     db.session.add(new_photo)
#                     db.session.commit()
#
#                     session['last_uploaded_image'] = filename
#                     flash("Фото успешно сохранено!")
#                     return redirect('/final_check')
#                 else:
#                     flash('Некорректное изображение.')
#                     return redirect(request.url)
#             except Exception as e:
#                 flash(f"Ошибка обработки изображения: {e}")
#                 return redirect(request.url)
#         else:
#             flash('Файл не был загружен.')
#             return redirect(request.url)
#
#     # Когда происходит GET-запрос, передаем имя существующего изображения
#     existing_photo = session.get('last_uploaded_image', None)
#     return render_template('photo.html', existing_photo=existing_photo)

@app.route('/photo/<string:photo_id>')
def get_photo_photo(photo_id):
    photo = Photo.query.filter_by(filename=photo_id).first()
    if photo:
        return send_file(BytesIO(photo.data), mimetype='image/jpeg')
    return "Фото не найдено", 404


@app.route('/photo/<int:photo_id>')
def get_photo(photo_id):
    # Извлечение фото по идентификатору
    photo = Photo.query.get(photo_id)
    if photo:
        mimetype = mimetypes.guess_type(photo.filename)[0] or 'image/jpeg'
        return send_file(
            BytesIO(photo.data),
            mimetype=mimetype,
            download_name=photo.filename
        )
    return "Фото не найдено", 404

@app.route('/final_check', methods=['GET', 'POST'])
def final_check():
    # Получение текущего пользователя
    current_user_id = session.get('current_user_id')
    if not current_user_id:
        flash("Не удалось определить текущего пользователя. Начните заново.")
        return redirect('/create_user')

    # Загрузка данных для текущего пользователя
    general_info = GeneralInformation.query.filter_by(user_id=current_user_id).first()
    mentor = Mentor.query.filter_by(user_id=current_user_id).first()
    captain_info = CaptainInfo.query.filter_by(user_id=current_user_id).first()
    participant_1 = Participant1.query.filter_by(user_id=current_user_id).first()
    participant_2 = Participant2.query.filter_by(user_id=current_user_id).first()
    participant_3 = Participant3.query.filter_by(user_id=current_user_id).first()
    photo = Photo.query.filter_by(user_id=current_user_id).first()

    # Проверка, что все данные заполнены
    if not general_info or not general_info.comandName or not general_info.schoolName or not general_info.cityName:
        flash('Не все данные в разделе "Общая информация" заполнены. Пожалуйста, вернитесь и заполните форму.')
        return redirect('/general_information')

    if not mentor or not mentor.mName or not mentor.mPost or not mentor.memail or not mentor.mphoneNumber:
        flash('Не все данные в разделе "Ментор" заполнены. Пожалуйста, вернитесь и заполните форму.')
        return redirect('/mentor')

    if not captain_info or not captain_info.captainName or not captain_info.captainClass or not captain_info.cemail or not captain_info.cphoneNumber:
        flash('Не все данные в разделе "Капитан" заполнены. Пожалуйста, вернитесь и заполните форму.')
        return redirect('/captain_info')

    if not participant_1 or not participant_1.uch1Name or not participant_1.uch1Class or not participant_1.uch1email or not participant_1.uch1phoneNumber:
        flash('Не все данные в разделе "Участник 1" заполнены. Пожалуйста, вернитесь и заполните форму.')
        return redirect('/participant_1')

    if not participant_2 or not participant_2.uch2Name or not participant_2.uch2Class or not participant_2.uch2email or not participant_2.uch2phoneNumber:
        flash('Не все данные в разделе "Участник 2" заполнены. Пожалуйста, вернитесь и заполните форму.')
        return redirect('/participant_2')

    if not photo:
        flash('Не все данные в разделе "Фотография" заполнены. Пожалуйста, загрузите фотографию.')
        return redirect('/photo')

    # Проверка на наличие участника 3 и его данных
    if participant_3:
        if not participant_3.uch3Name or not participant_3.uch3Class or not participant_3.uch3email or not participant_3.uch3phoneNumber:
            flash('Не все данные в разделе "Участник 3" заполнены. Пожалуйста, вернитесь и заполните форму.')
            return redirect('/participant_3')

    if request.method == 'POST':
        # Обновление данных из формы
        general_info.comandName = request.form['comandName']
        general_info.schoolName = request.form['schoolName']
        general_info.cityName = request.form['cityName']

        mentor.mName = request.form['mName']
        mentor.mPost = request.form['mPost']
        mentor.memail = request.form['memail']
        mentor.mphoneNumber = request.form['mphoneNumber']

        captain_info.captainName = request.form['captainName']
        captain_info.captainClass = request.form['captainClass']
        captain_info.cemail = request.form['cemail']
        captain_info.cphoneNumber = request.form['cphoneNumber']

        participant_1.uch1Name = request.form['uch1Name']
        participant_1.uch1Class = request.form['uch1Class']
        participant_1.uch1email = request.form['uch1email']
        participant_1.uch1phoneNumber = request.form['uch1phoneNumber']

        participant_2.uch2Name = request.form['uch2Name']
        participant_2.uch2Class = request.form['uch2Class']
        participant_2.uch2email = request.form['uch2email']
        participant_2.uch2phoneNumber = request.form['uch2phoneNumber']

        # Проверка на наличие участника 3 и обновление его данных
        if participant_3:
            participant_3.uch3Name = request.form.get('uch3Name', '')
            participant_3.uch3Class = request.form.get('uch3Class', '')
            participant_3.uch3email = request.form.get('uch3email', '')
            participant_3.uch3phoneNumber = request.form.get('uch3phoneNumber', '')

        # Обновление фотографии, если файл был загружен
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                # Удаляем старое фото, если оно есть
                existing_photo = Photo.query.filter_by(user_id=current_user_id).first()
                if existing_photo:
                    db.session.delete(existing_photo)
                    db.session.commit()

                filename = secure_filename(file.filename)
                new_photo = Photo(filename=filename, data=file.read(), user_id=current_user_id)
                db.session.add(new_photo)
                db.session.commit()

        try:
            db.session.commit()
            return redirect('/registration_end')
        except Exception as e:
            return f'Ошибка сохранения данных: {e}'

    # Передача данных в шаблон, исключая участника 3, если он пустой
    return render_template(
        'final_check.html',
        general_info=general_info,
        mentor=mentor,
        captain_info=captain_info,
        participant_1=participant_1,
        participant_2=participant_2,
        participant_3=participant_3 if participant_3 and any([participant_3.uch3Name, participant_3.uch3Class, participant_3.uch3email, participant_3.uch3phoneNumber]) else None,
        photo_id=photo.id if photo else None,
        photo_filename=photo.filename if photo else None
    )


@app.route('/registration_end')
def registration_end():
    # Сбрасываем текущего пользователя, вернуть для создания нового пользователя при каждой регистрации
    # session.pop('current_user_id', None)
    # flash("Регистрация завершена! Сессия сброшена.")
    return render_template('registration_end.html')


@app.route('/check_status')
def check_status():
    if 'current_user_id' in session:
        return redirect('/general_information')  # Показываем информацию
    return redirect('/create_user')  # Перенаправляем на регистрацию


if __name__ == '__main__':
    app.run(debug=True)
