class Config:
    SECRET_KEY = "looking-dapper"
    SQLALCHEMY_DATABASE_URI = "sqlite:///users.sqlite3"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = "localhost"
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = ("QA Potions", "no-reply@example.com")
    MAIL_SUPPRESS_SEND = True
