import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = 'a complex string'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	FLASK_MAIL_SUBJECT_PREFIX = '[From Admin]'
	FLASK_MAIL_SENDER = 'ross111@126.com'
	FLASK_ADMIN = 'titian'

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	MAIL_SERVER = 'smtp.126.com'
	MAIL_PORT = 25
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or \
		'sqlite:///'+os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or \
		'sqlite:///'+os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
		'sqlite:///'+os.path.join(basedir, 'data.sqlite')

config = {
	'development':DevelopmentConfig,
	'testing':TestingConfig,
	'production':ProductionConfig,

	'default':DevelopmentConfig
}
