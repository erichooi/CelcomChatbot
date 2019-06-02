import pymysql
import os

CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')

def connect_to_cloudsql():
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        cloudsql_unix_socket = os.path.join('/cloudsql', CLOUDSQL_CONNECTION_NAME)

        connection = pymysql.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            password=CLOUDSQL_PASSWORD,
            db='question_label',

        )
    else:
        connection = pymysql.connect(
            host='127.0.0.1',
            user='root', # if testing change username and password
            password='!213,hui9845',
            db='question_label',
        )
    return connection

def add_question(question, label):
    connection = connect_to_cloudsql()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `question_label` (`question`, `label`) VALUES (%s, %s)"
            cursor.execute(sql, (question, label))
        connection.commit()
    finally:
        connection.close()