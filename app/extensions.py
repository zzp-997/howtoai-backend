"""
Flask 扩展兼容层
为遗留模块提供 Flask-SQLAlchemy 的 db 对象
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
