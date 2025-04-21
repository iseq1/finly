"""
Схемы для аутентификации и управления пользователями
"""
from marshmallow import Schema, fields, validates, ValidationError, validates_schema, post_load, pre_load
from app.extensions import ma
from app.models.auth import User, Role, UserSession, UserAvatar, UserRole, UserCashbox, UserCashboxHistory
from app.schemas.base import BaseSchema, HistorySchema


class PermissionSchema(Schema):
    """Схема разрешений"""
    permission = fields.String(required=True)


class RoleSchema(BaseSchema):
    """Схема ролей"""
    class Meta:
        model = Role
        load_instance = True

    name = fields.String(required=True)
    description = fields.String()
    level = fields.Integer()
    permissions = fields.List(fields.String())


class UserBaseSchema(BaseSchema):
    """Базовая схема пользователя"""
    class Meta:
        model = User
        load_instance = True

    username = fields.String(required=False)
    email = fields.Email(required=True)
    first_name = fields.String()
    last_name = fields.String()
    patronymic = fields.String()
    phone_number = fields.String()
    birthday = fields.DateTime()
    is_active = fields.Boolean(dump_only=True)
    last_login = fields.DateTime(dump_only=True)
    telegram_id = fields.Integer(dump_only=True)
    telegram_username = fields.String(dump_only=True)
    roles = fields.List(fields.Nested(RoleSchema))


class UserCreateSchema(UserBaseSchema):
    """Схема для создания пользователя"""
    password = fields.String(required=True, load_only=True)
    confirm_password = fields.String(required=True, load_only=True)

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        """Проверка совпадения паролей"""
        if data['password'] != data['confirm_password']:
            raise ValidationError('Пароли не совпадают')

    @validates('password')
    def validate_password(self, value):
        """Проверка сложности пароля"""
        if len(value) < 8:
            raise ValidationError('Пароль должен содержать минимум 8 символов')
        if not any(c.isupper() for c in value):
            raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву')
        if not any(c.isdigit() for c in value):
            raise ValidationError('Пароль должен содержать хотя бы одну цифру')

class UserUpdateSchema(BaseSchema):
    """Схема для обновления данных пользователя"""
    class Meta:
        model = User
        load_instance = False
        
    username = fields.String()
    email = fields.Email()
    first_name = fields.String()
    last_name = fields.String()
    patronymic = fields.String()
    phone_number = fields.String()
    birthday = fields.DateTime()
    is_active = fields.Boolean(dump_only=True)
    last_login = fields.DateTime(dump_only=True)
    roles = fields.List(fields.Nested(RoleSchema), dump_only=True)
    current_password = fields.String(load_only=True)
    new_password = fields.String(load_only=True)
    confirm_new_password = fields.String(load_only=True)

    @validates_schema
    def validate_password_update(self, data, **kwargs):
        """Проверка паролей при обновлении"""
        if 'new_password' in data:
            if not data.get('current_password'):
                raise ValidationError('Необходимо указать текущий пароль')
            if not data.get('confirm_new_password'):
                raise ValidationError('Необходимо подтвердить новый пароль')
            if data['new_password'] != data['confirm_new_password']:
                raise ValidationError('Новые пароли не совпадают')


class LoginSchema(Schema):
    """Схема для входа в систему"""
    email = fields.String(required=True)
    password = fields.String(required=True)
    remember_me = fields.Boolean(missing=False)


class TokenSchema(Schema):
    """Схема для JWT токенов"""
    access_token = fields.String(dump_only=True)
    refresh_token = fields.String(dump_only=True)
    token_type = fields.String(dump_only=True, default='bearer')


class UserSessionSchema(BaseSchema):
    """Схема для сессий пользователя"""
    class Meta:
        model = UserSession
        load_instance = True

    user_id = fields.Integer(dump_only=True)
    user_agent = fields.String(dump_only=True)
    ip_address = fields.String(dump_only=True)
    expires_at = fields.DateTime(dump_only=True)
    is_active = fields.Boolean(dump_only=True)


class RoleHistorySchema(HistorySchema):
    """Схема для истории изменений ролей"""
    role_id = fields.Integer(required=True)


class UserHistorySchema(HistorySchema):
    """Схема для истории изменений пользователя"""
    user_id = fields.Integer(required=True)


class UserAvatarSchema(BaseSchema):
    """Схема для аватара пользователя"""
    class Meta:
        model = UserAvatar
        load_instance = True
    
    user_id = fields.Integer(required=True)
    file_path = fields.String(required=True)
    url = fields.String(dump_only=True)


class UserRoleSchema(BaseSchema):
    """Схема для связи пользователя и роли"""
    class Meta:
        model = UserRole
        load_instance = True
    
    user_id = fields.Integer(required=True)
    role_id = fields.Integer(required=True)
    role = fields.Nested(RoleSchema, dump_only=True)
    user = fields.Nested(UserBaseSchema, dump_only=True)


class UserCashboxSchema(BaseSchema):
    """Схема кэш-бокса пользователя"""
    class Meta:
        model = UserCashbox
        load_instance = True

    user_id = fields.Integer(required=True)
    cashbox_id = fields.Integer(required=True)

    balance = fields.Float(required=True)
    is_auto_update = fields.Boolean(required=True)
    last_synced_at = fields.DateTime(required=True)

    # Доп. поля:
    custom_name = fields.String(required=True)
    note = fields.String(required=True)

    # Связи
    user = fields.Nested('UserBaseSchema', only=('username', 'first_name', 'last_name'), dump_only=True)
    cashbox = fields.Nested('CashboxSchema', only=('name', 'currency'), dump_only=True)


class UserCashboxSchemaHistory(HistorySchema):
    """Схема изменений кэш-бокса пользователя"""
    user_cashbox_id = fields.Integer(required=True)


class UserTelegramSchema(BaseSchema):
    telegram_id = fields.Integer(required=True)
    telegram_username = fields.String(required=True)
    secret = fields.String(required=False)

    @pre_load
    def preprocess_username(self, data, **kwargs):
        username = data.get('telegram_username', '')
        if username.startswith('@'):
            username = username[1:]
        data['telegram_username'] = username.lower()
        return data

    @validates('telegram_username')
    def validate_username(self, value):
        if not value.isalnum():
            raise ValidationError("telegram_username может содержать только буквы и цифры")
        if len(value) > 32:
            raise ValidationError("telegram_username не может быть длиннее 32 символов")

    @validates('telegram_id')
    def validate_telegram_id(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValidationError("telegram_id должен быть положительным целым числом")