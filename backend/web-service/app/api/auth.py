"""
API для аутентификации и управления пользователями
"""
from datetime import datetime
from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    create_refresh_token, jwt_required, get_jwt_identity,
    create_access_token, get_jwt, set_access_cookies
)
from marshmallow import ValidationError
from app.models.auth import User, Role, UserSession, UserAvatar, UserRole, UserCashbox, get_all_permissions
from app.schemas.auth import (
    UserCreateSchema, UserUpdateSchema, LoginSchema,
    TokenSchema, RoleSchema, PermissionSchema, UserAvatarSchema, UserRoleSchema, UserCashboxSchema
)
from app.utils.auth import (
    create_tokens, set_auth_cookies,
    clear_auth_cookies, permission_required,
    log_action
)
from app.utils.helpers import serialize_value
from app.extensions import db

api = Namespace('auth', description='Операции аутентификации и управления пользователями')

# Модели для Swagger документации
user_model = api.model('User', {
    'username': fields.String(required=False, description='Имя пользователя (опционально)'),
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Пароль'),
    'confirm_password': fields.String(required=True, description='Подтверждение пароля'),
    'first_name': fields.String(description='Имя'),
    'last_name': fields.String(description='Фамилия'),
    'patronymic': fields.String(description='Отчество'),
    'phone_number': fields.String(description='Номер телефона')
})

user_update_model = api.model('UserUpdate', {
    'username': fields.String(description='Имя пользователя (опционально)'),
    'email': fields.String(description='Email (опционально)'),
    'first_name': fields.String(description='Имя (опционально)'),
    'last_name': fields.String(description='Фамилия (опционально)'),
    'patronymic': fields.String(description='Отчество (опционально)'),
    'phone_number': fields.String(description='Номер телефона (опционально)'),
    'current_password': fields.String(description='Текущий пароль (обязателен при изменении пароля)'),
    'new_password': fields.String(description='Новый пароль (требует указания current_password и confirm_new_password)'),
    'confirm_new_password': fields.String(description='Подтверждение нового пароля (требует указания current_password и new_password)')
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Пароль'),
    'remember_me': fields.Boolean(description='Запомнить меня')
})

user_cashbox_model = api.model('UserCashbox', {
    'user_id': fields.Integer(required=True, description='ID-пользователя'),
    'cashbox_id': fields.Integer(required=True, description='ID-кэш-бокса'),
    'balance': fields.Float(required=True, description='Баланс кэш-бокса пользователя'),
    'is_auto_update': fields.Boolean(required=True, description='Включено ли автообновление баланса'),
    'last_synced_at': fields.DateTime(required=True, description='Последняя дата автообновления баланса'),
    'custom_name': fields.String(required=True, description='Кастомное имя кэш-бокса от пользователя'),
    'note': fields.String(required=True, description='Заметка к кэш-боксу от пользователя'),
})


@api.route('/register')
class Register(Resource):
    """Регистрация нового пользователя"""
    
    @api.expect(user_model)
    @api.response(201, 'Пользователь успешно создан')
    @api.response(400, 'Ошибка валидации')
    def post(self):
        """Регистрация нового пользователя"""
        try:
            user_data = UserCreateSchema().load(request.json)
            
            # Проверка существования пользователя
            query_filter = (User.email == user_data.email)
            if user_data.username:
                query_filter = query_filter | (User.username == user_data.username)
                
            if User.query.filter(query_filter).first():
                message = 'Пользователь с таким email уже существует'
                if user_data.username:
                    message = 'Пользователь с таким именем или email уже существует'
                return {
                    'message': message
                }, 400
            
            # Создание пользователя
            user = user_data
            user.is_active = True
            user.set_password(request.json['password'])
            
            db.session.add(user)
            db.session.commit()
            
            # Создание токенов
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            return {
                'message': 'Пользователь успешно зарегистрирован',
                'user': UserCreateSchema(exclude=['password']).dump(user),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 201
            
        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400

# Модели для ролей и разрешений
permission_model = api.model('Permission', {
    'permission': fields.String(required=True, description='Строка разрешения')
})

role_model = api.model('Role', {
    'name': fields.String(required=True, description='Название роли'),
    'description': fields.String(description='Описание роли'),
    'level': fields.Integer(description='Уровень роли'),
    'permissions': fields.List(fields.String, description='Список строк разрешений')
})

@api.route('/permissions')
class PermissionList(Resource):
    """Управление разрешениями"""
    
    @jwt_required()
    #@permission_required('permission.view')
    @api.doc(security='jwt')
    def get(self):
        """Получение списка всех зарегистрированных разрешений"""
        # Получаем разрешения напрямую из глобального реестра, без обращения к БД
        permissions = get_all_permissions()
        # Возвращаем простой словарь с массивом строк
        return {'permissions': permissions}

@api.route('/roles')
class RoleList(Resource):
    """Управление ролями"""
    
    @jwt_required()
    #@permission_required('role.view')
    @api.doc(security='jwt')
    def get(self):
        """Получение списка всех ролей"""
        roles = Role.query.filter_by(deleted=False).all()
        return RoleSchema(many=True).dump(roles)
    
    @jwt_required()
    #@permission_required('role.create')
    @api.doc(security='jwt')
    @api.expect(role_model)
    def post(self):
        """Создание новой роли"""
        try:
            role_data = RoleSchema().load(request.json)
            
            # Проверка существования роли
            if Role.query.filter_by(name=role_data.name).first():
                return {'message': 'Роль с таким названием уже существует'}, 400
            
            # role_data is already a Role instance because load_instance=True in RoleSchema
            role = role_data
            db.session.add(role)
            db.session.commit()
            
            return {
                'message': 'Роль успешно создана',
                'role': RoleSchema().dump(role)
            }, 201
            
        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400

@api.route('/roles/<int:id>')
class RoleDetail(Resource):
    """Управление конкретной ролью"""
    
    @jwt_required()
    #@permission_required('role.view')
    @api.doc(security='jwt')
    def get(self, id):
        """Получение информации о роли"""
        role = Role.query.get_or_404(id)
        return RoleSchema().dump(role)
    
    @jwt_required()
    #@permission_required('role.update')
    @api.doc(security='jwt')
    @api.expect(role_model)
    def put(self, id):
        """Обновление роли"""
        try:
            role = Role.query.get_or_404(id)
            role_data = RoleSchema(load_instance=False).load(request.json)
            
            # Проверка существования названия роли
            existing = Role.query.filter_by(name=role_data['name']).first()
            if existing and existing.id != id:
                return {'message': 'Роль с таким названием уже существует'}, 400
            
            for field, value in role_data.items():
                setattr(role, field, value)
            
            db.session.commit()
            
            return {
                'message': 'Роль успешно обновлена',
                'role': RoleSchema().dump(role)
            }
            
        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400
    
    @jwt_required()
    #@permission_required('role.delete')
    @api.doc(security='jwt')
    def delete(self, id):
        """Удаление роли"""
        role = Role.query.get_or_404(id)
        role.soft_delete()
        return {'message': 'Роль успешно удалена'}

@api.route('/roles/<int:id>/permissions')
class RolePermissions(Resource):
    """Управление разрешениями роли"""
    
    @jwt_required()
    #@permission_required('role.update')
    @api.doc(security='jwt')
    def post(self, id):
        """Добавление разрешений к роли"""
        try:
            role = Role.query.get_or_404(id)
            data = request.json
            
            if not isinstance(data.get('permissions'), list):
                return {'message': 'permissions должен быть списком строк'}, 400
            
            for permission in data['permissions']:
                role.add_permission(permission)
            
            db.session.commit()
            
            return {
                'message': 'Разрешения успешно добавлены к роли',
                'role': RoleSchema().dump(role)
            }
            
        except Exception as e:
            return {'message': str(e)}, 400
    
    @jwt_required()
    #@permission_required('role.update')
    def delete(self, id):
        """Удаление разрешений из роли"""
        try:
            role = Role.query.get_or_404(id)
            data = request.json
            
            if not isinstance(data.get('permissions'), list):
                return {'message': 'permissions должен быть списком строк'}, 400
            
            for permission in data['permissions']:
                role.remove_permission(permission)
            
            db.session.commit()
            
            return {
                'message': 'Разрешения успешно удалены из роли',
                'role': RoleSchema().dump(role)
            }
            
        except Exception as e:
            return {'message': str(e)}, 400
@api.route('/login')
class Login(Resource):
    """Вход в систему"""
    
    @api.expect(login_model)
    @api.response(200, 'Успешный вход')
    @api.response(401, 'Неверные учетные данные')
    def post(self):
        """Аутентификация пользователя"""
        try:
            login_data = LoginSchema().load(request.json)
            
            user = User.query.filter_by(email=login_data['email']).first()
            
            if not user or not user.check_password(login_data['password']):
                return {'message': 'Неверный email или пароль'}, 401
            
            if not user.is_active:
                return {'message': 'Пользователь деактивирован'}, 401
            
            # Обновление времени последнего входа
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Создание токенов
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            return {
                'message': 'Успешный вход в систему',
                'user': UserCreateSchema(exclude=['password']).dump(user),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
            
        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400

@api.route('/logout')
class Logout(Resource):
    """Выход из системы"""
    
    @api.doc(security='jwt')
    def post(self):
        """Выход пользователя из системы"""
        try:
            # Получаем refresh_token из запроса
            #refresh_token = request.json.get('refresh_token')
            #
            ## Если токен предоставлен, деактивируем сессию
            #if refresh_token:
            #    session = UserSession.query.filter_by(refresh_token=refresh_token).first()
            #    if session:
            #        session.is_active = False
            #        db.session.commit()
            
            # Создаем ответ
            response = jsonify({'message': 'Успешный выход из системы'})
            
            # Очищаем куки независимо от наличия токена
            clear_auth_cookies(response)
            
            return response
        except Exception as e:
            return {'message': f'Ошибка при выходе из системы: {str(e)}'}, 400

@api.route('/refresh')
class RefreshToken(Resource):
    """Обновление токена"""
    
    @jwt_required(refresh=True)
    def post(self):
        """Обновление access токена"""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        access_token = create_access_token(identity=str(user_id))
        refresh_token = create_refresh_token(identity=str(user_id))
        
        return {
            'message': 'Токен успешно обновлен',
            'user': UserCreateSchema(exclude=['password']).dump(user),
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200

@api.route('/me')
class UserProfile(Resource):
    """Профиль пользователя"""
    
    @jwt_required()
    @api.doc(security='jwt')
    def get(self):
        """Получение данных текущего пользователя"""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        
        return UserCreateSchema(exclude=['password']).dump(user)
    
    @jwt_required()
    @api.doc(security='jwt')
    @api.expect(user_update_model)
    def put(self):
        """Обновление данных пользователя"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get_or_404(user_id)
            
            user_data = UserUpdateSchema().load(request.json)
            
            # Проверка текущего пароля при изменении
            if 'new_password' in user_data:
                if not user.check_password(user_data['current_password']):
                    return {'message': 'Неверный текущий пароль'}, 400
                user.set_password(user_data['new_password'])
            
            # Обновление остальных полей
            for field in ['username', 'email', 'first_name', 'last_name', 'patronymic', 'phone_number', 'birthday']:
                if field in user_data:
                    setattr(user, field, user_data[field])
            
            db.session.commit()
            
            return {
                'message': 'Профиль успешно обновлен',
                'user': UserCreateSchema(exclude=['password']).dump(user)
            }
            
        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400


# Модель для аватара пользователя
avatar_model = api.model('UserAvatar', {
    'file': fields.Raw(required=True, description='Файл аватара')
})


@api.route('/user-roles')
class UserRoleListResource(Resource):
    """Управление ролями пользователей"""
    
    @jwt_required()
    @api.doc(security='jwt')
    def get(self):
        """Получение списка всех связей пользователей и ролей"""
        user_roles = UserRole.query.filter_by(deleted=False).all()
        return UserRoleSchema(many=True).dump(user_roles)
    
    @jwt_required()
    @api.doc(security='jwt')
    def post(self):
        """Создание новой связи пользователя и роли"""
        try:
            user_role_data = UserRoleSchema().load(request.json)
            
            # Проверка существования пользователя
            if not User.query.get(user_role_data.user_id):
                return {'message': 'Указанный пользователь не существует'}, 400
            
            # Проверка существования роли
            if not Role.query.get(user_role_data.role_id):
                return {'message': 'Указанная роль не существует'}, 400
            
            # Проверка уникальности связи
            existing = UserRole.query.filter_by(
                user_id=user_role_data.user_id,
                role_id=user_role_data.role_id,
                deleted=False
            ).first()
            
            if existing:
                return {'message': 'Такая связь уже существует'}, 400
            
            db.session.add(user_role_data)
            db.session.commit()
            
            return {
                'message': 'Роль успешно назначена пользователю',
                'user_role': UserRoleSchema().dump(user_role_data)
            }, 201
            
        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400


@api.route('/user-roles/<int:id>')
class UserRoleResource(Resource):
    """Управление конкретной связью пользователя и роли"""
    
    @jwt_required()
    @api.doc(security='jwt')
    def get(self, id):
        """Получение информации о связи пользователя и роли"""
        user_role = UserRole.query.get_or_404(id)
        return UserRoleSchema().dump(user_role)
    
    @jwt_required()
    @api.doc(security='jwt')
    def delete(self, id):
        """Удаление связи пользователя и роли"""
        user_role = UserRole.query.get_or_404(id)
        user_role.soft_delete()
        return {'message': 'Роль успешно удалена у пользователя'}


@api.route('/users/<int:user_id>/roles')
class UserRolesResource(Resource):
    """Управление ролями конкретного пользователя"""
    
    @jwt_required()
    @api.doc(security='jwt')
    def get(self, user_id):
        """Получение всех ролей пользователя"""
        user = User.query.get_or_404(user_id)
        user_roles = UserRole.query.filter_by(user_id=user_id, deleted=False).all()
        return UserRoleSchema(many=True).dump(user_roles)


@api.route('/me/avatar')
class UserAvatarResource(Resource):
    """Управление аватаром пользователя"""
    
    @jwt_required()
    @api.doc(security='jwt')
    def get(self):
        """Получение аватара текущего пользователя"""
        user_id = get_jwt_identity()
        avatar = UserAvatar.query.filter_by(user_id=user_id, deleted=False).first()
        
        if not avatar:
            return {'message': 'Аватар не найден'}, 404
        
        return UserAvatarSchema().dump(avatar)
    
    @jwt_required()
    @api.doc(security='jwt')
    @api.expect(avatar_model)
    def post(self):
        """Загрузка или обновление аватара пользователя"""
        try:
            user_id = get_jwt_identity()
            
            # Проверяем наличие файла в запросе
            if 'file' not in request.files:
                return {'message': 'Файл не найден в запросе'}, 400
                
            file = request.files['file']
            if file.filename == '':
                return {'message': 'Файл не выбран'}, 400
            
            # Импортируем утилиты для работы с файлами
            from app.utils.helpers import save_file, delete_file, allowed_file
            
            if not allowed_file(file.filename):
                return {'message': 'Неподдерживаемый тип файла'}, 400
            
            # Проверяем, существует ли уже аватар
            avatar = UserAvatar.query.filter_by(user_id=user_id, deleted=False).first()
            
            # Генерируем имя файла на основе ID пользователя
            subfolder = 'avatars'
            
            if avatar:
                # Удаляем старый файл
                delete_file(avatar.file_path)
                
                # Сохраняем новый файл
                file_path = save_file(file, subfolder)
                avatar.file_path = file_path
            else:
                # Сохраняем файл
                file_path = save_file(file, subfolder)
                
                # Создаем новый аватар
                avatar = UserAvatar(
                    user_id=user_id,
                    file_path=file_path
                )
                db.session.add(avatar)
            
            db.session.commit()
            
            return {
                'message': 'Аватар успешно обновлен',
                'avatar': UserAvatarSchema().dump(avatar)
            }
            
        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400
        except Exception as e:
            return {'message': f'Ошибка при обновлении аватара: {str(e)}'}, 400
    
    @jwt_required()
    @api.doc(security='jwt')
    def delete(self):
        """Удаление аватара пользователя"""
        try:
            user_id = get_jwt_identity()
            avatar = UserAvatar.query.filter_by(user_id=user_id, deleted=False).first()
            
            if not avatar:
                return {'message': 'Аватар не найден'}, 404
            
            # Импортируем утилиту для удаления файла
            from app.utils.helpers import delete_file
            
            # Удаляем файл
            delete_file(avatar.file_path)
            
            # Удаляем запись из БД
            avatar.hard_delete()
            
            return {'message': 'Аватар успешно удален'}
        except Exception as e:
            return {'message': f'Ошибка при удалении аватара: {str(e)}'}, 400


@api.route('/me/cashboxes')
class UserCashboxList(Resource):
    """Управление кэш-боксами пользователя"""

    @jwt_required()
    @api.doc(security='jwt')
    def get(self):
        """Получение списка кэш-боксов текущего пользователя"""
        user_id = get_jwt_identity()
        user_cashboxes = UserCashbox.query.filter_by(user_id=user_id, deleted=False).all()

        return UserCashboxSchema(many=True).dump(user_cashboxes)

    @jwt_required()
    @api.doc(security='jwt')
    @api.expect(user_cashbox_model)
    def post(self):
        """Создание нового пользовательского кэш-бокса"""
        try:
            user_cashbox_data = UserCashboxSchema().load(request.json)
            user_id = get_jwt_identity()

            # Проверка корректности user_id
            if int(user_id) != user_cashbox_data.user_id:
                return {'message': 'Неверно указан ID-пользователя в запросе'}, 400

            # Проверка существования типа кэш-бокса
            if UserCashbox.query.filter_by(user_id=user_id, cashbox_id=user_cashbox_data.cashbox_id).first():
                return {'message': 'Указанный пользовательский кэш-бокс уже существует у указанного пользователя'}, 400


            db.session.add(user_cashbox_data)
            db.session.commit()

            # Логирование действий
            from app.models.auth import UserCashboxHistory
            UserCashboxHistory.log_change(user_cashbox_data, 'create', user_id)

            return {
                'message': 'Новый пользовательский кэш-бокс успешно создан',
                'user_cashbox': UserCashboxSchema().dump(user_cashbox_data)
            }, 201

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400


@api.route('/me/cashboxes/<int:id>')
class UserCashboxDetail(Resource):
    """Управление конкретным пользовательским кэш-боксом"""

    @jwt_required()
    @api.doc(security='jwt')
    def get(self, id):
        """Получение информации о конкретном пользовательском кэш-боксе"""
        user_cashbox = UserCashbox.query.get_or_404(id)
        return UserCashboxSchema().dump(user_cashbox)

    @jwt_required()
    @api.doc(security='jwt')
    @api.expect(user_cashbox_model)
    def put(self, id):
        """Обновление конкретного пользовательского кэш-бокса"""
        try:
            user_cashbox = UserCashbox.query.get_or_404(id)
            user_cashbox_data = UserCashboxSchema().load(request.json)

            user_id = get_jwt_identity()

            # Проверка корректности user_id
            if int(user_id) != user_cashbox_data.user_id:
                return {'message': 'Неверно указан ID-пользователя в запросе'}, 400

            # Сохранение старых данных для истории
            old_data = user_cashbox.to_dict()

            # Проверка корректности изменений
            if user_cashbox.user_id != user_cashbox_data.user_id:
                return {'message': 'К сожалению, вы не можете изменить ID-пользователя'}

            for field, value in user_cashbox_data.__dict__.items():
                if field != '_sa_instance_state':
                    setattr(user_cashbox, field, value)

            db.session.commit()

            # Логирование изменений
            from app.models.auth import UserCashboxHistory
            changes = {k: serialize_value(v) for k, v in user_cashbox.to_dict().items() if old_data.get(k) != v}
            UserCashboxHistory.log_change(user_cashbox, 'update', user_id, changes)

            return {
                'message': 'Пользовательский кэш-бокс успешно обновлен',
                'user_cashbox': UserCashboxSchema().dump(user_cashbox)
            }

        except ValidationError as e:
            return {'message': 'Ошибка валидации', 'errors': e.messages}, 400

    @jwt_required()
    @api.doc(security='jwt')
    def delete(self, id):
        """Удаление конкретного пользовательского кэш-бокса"""
        user_cashbox = UserCashbox.query.get_or_404(id)
        user_id = get_jwt_identity()

        # Проверка корректности user_id
        if int(user_id) != user_cashbox.user_id:
            return {'message': 'Неверно указан ID-пользователя в запросе'}, 400

        # Логирование изменений
        from app.models.auth import UserCashboxHistory
        UserCashboxHistory.log_change(user_cashbox, 'delete', user_id)
        user_cashbox.soft_delete()
        return {'message': f'Пользовательский кэш-бокс с ID = {id} успешно удален'}
