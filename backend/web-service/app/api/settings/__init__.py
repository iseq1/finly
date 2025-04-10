"""
API для управления системными настройками и справочниками
"""
from flask_restx import Namespace

api = Namespace('settings', description='Управление настройками и справочниками')

from app.api.settings.categories import *
from app.api.settings.cashboxes import *

