import os

SECRET_KEY = 'e341e6698cb20dd889d040a9be7d5fc129cb06255f349bd6ea3f901afe8d61b4'

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://std_1914_lisafe_project:qwertyUI@std-mysql.ist.mospolytech.ru/std_1914_lisafe_project'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')

ADMIN_ROLE_ID = 1
MODERATOR_ROLE_ID = 2
USER_ROLE_ID = 3