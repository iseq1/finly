"""
Скрипт для заполнения базы данных начальными данными
"""
from datetime import datetime, timezone
from app import create_app
from app.extensions import db



def seed_categories():
    from app.schemas.settings.categories import CategorySchema, SubcategorySchema
    categories = [
        {
            'name': 'Здоровье',
            'code': 891,
            'color': '#ASDFAS',
            'logo_url': 'url',
        },
        {
            'name': 'Кафе и рестораны',
            'code': 892,
            'color': '#ASDFAS',
            'logo_url': 'url',
        },
        {
            'name': 'Продукты',
            'code': 893,
            'color': '#ASDFAS',
            'logo_url': 'url',
        },
        {
            'name': 'Транспорт',
            'code': 894,
            'color': '#ASDFAS',
            'logo_url': 'url',
        },
        {
            'name': 'Зарплата',
            'code': 215,
            'color': '#ASDFAS',
            'logo_url': 'url',
        },
        {
            'name': 'Дарение',
            'code': 216,
            'color': '#ASDFAS',
            'logo_url': 'url',
        },
    ]
    subcategories = [
        {
            'name': 'Массаж',
            'code': 8911,
            'logo_url': 'url',
            'category_id': 1,
        },
        {
            'name': 'Бады',
            'code': 8912,
            'logo_url': 'url',
            'category_id': 1,
        },
        {
            'name': 'Терапевт',
            'code': 8913,
            'logo_url': 'url',
            'category_id': 1,
        },
        {
            'name': 'Столовая',
            'code': 8924,
            'logo_url': 'url',
            'category_id': 2,
        },
        {
            'name': 'ФастФуд',
            'code': 8925,
            'logo_url': 'url',
            'category_id': 2,
        },
        {
            'name': 'Кофейня',
            'code': 8926,
            'logo_url': 'url',
            'category_id': 2,
        },
        {
            'name': 'Доставка',
            'code': 8937,
            'logo_url': 'url',
            'category_id': 3,
        },
        {
            'name': 'Мясо',
            'code': 8938,
            'logo_url': 'url',
            'category_id': 3,
        },
        {
            'name': 'Бакалея',
            'code': 8939,
            'logo_url': 'url',
            'category_id': 3,
        },
        {
            'name': 'Метро',
            'code': 89410,
            'logo_url': 'url',
            'category_id': 4,
        },
        {
            'name': 'Автобус',
            'code': 89411,
            'logo_url': 'url',
            'category_id': 4,
        },
        {
            'name': 'Трамвай',
            'code': 89412,
            'logo_url': 'url',
            'category_id': 4,
        },
        {
            'name': 'Оклад',
            'code': 21513,
            'logo_url': 'url',
            'category_id': 5,
        },
        {
            'name': 'КПИ',
            'code': 21514,
            'logo_url': 'url',
            'category_id': 5,
        },
        {
            'name': 'Отпускные',
            'code': 21515,
            'logo_url': 'url',
            'category_id': 5,
        },
        {
            'name': 'Иждивение',
            'code': 21616,
            'logo_url': 'url',
            'category_id': 6,
        },
        {
            'name': 'Праздники',
            'code': 21617,
            'logo_url': 'url',
            'category_id': 6,
        },
        {
            'name': 'Другое',
            'code': 21618,
            'logo_url': 'url',
            'category_id': 6,
        },
    ]
    for item in categories:
        category_data = CategorySchema().load(item)
        db.session.add(category_data)
    for item in subcategories:
        subcategory_data = SubcategorySchema().load(item)
        db.session.add(subcategory_data)
    db.session.commit()
    print("Данные о категориях успешно загружены")


def seed_cashboxes():
    from app.schemas.settings.cashboxes import CashboxSchema, CashboxTypeSchema, CashboxProviderSchema
    types = [
        {
            'name': 'Дебетовый счет',
            'code': 'debit',
        },
        {
            'name': 'Кредитный счет',
            'code': 'credit',
        },
        {
            'name': 'Инвестиционный счет',
            'code': 'invest',
        },
        {
            'name': 'Наличные',
            'code': 'cash',
        },
        {
            'name': 'Крипто-кошелек',
            'code': 'crypto',
        },
    ]
    providers = [
        {
            'name': 'Т-Банк',
            'full_name': 'АО ТБанк',
            'logo_url': 'https://cdn.tbank.ru/static/pfa-multimedia/images/de8a4fa0-0b29-4901-a678-35f93d358cdf.png',
            'alt_logo_url': 'alt_logo_url',
            'color': '#f8d81c',
            'second_color': '#2c3844',
            'alt_color': '#cccac3',
            'second_alt_color': '#2c3844',
        },
        {
            'name': 'Альфа-Банк',
            'full_name': 'АО Альфа-Банк',
            'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Alfa-Bank.svg/1280px-Alfa-Bank.svg.png',
            'alt_logo_url': 'alt_logo_url',
            'color': '#EF3124',
            'second_color': '#000000',
            'alt_color': '#505759',
            'second_alt_color': '#D9D9D6',
        },
        {
            'name': 'СберБанк',
            'full_name': 'ПАО Сбербанк',
            'logo_url': 'https://free-png.ru/wp-content/uploads/2020/09/sberbank__-01.png',
            'alt_logo_url': 'alt_logo_url',
            'color': '#276EB5',
            'second_color': '#003B85',
            'alt_color': '#A0E720',
            'second_alt_color': '#42E3B4',
        },
        {
            'name': 'Наличка',
            'full_name': 'Наличные средства',
            'logo_url': 'https://w7.pngwing.com/pngs/963/501/png-transparent-money-others-stack-presentation-logo.png',
            'alt_logo_url': 'alt_logo_url',
            'color': '#276EB5',
            'second_color': '#003B85',
            'alt_color': '#A0E720',
            'second_alt_color': '#42E3B4',
        },
        {
            'name': 'Binance',
            'full_name': 'Binance DEX',
            'logo_url': 'https://download.logo.wine/logo/Binance/Binance-Logo.wine.png',
            'alt_logo_url': 'alt_logo_url',
            'color': '#f3ba2f',
            'second_color': '#f3ba2f',
            'alt_color': '#f3ba2f',
            'second_alt_color': '#f3ba2f',
        },
    ]
    cashboxes = [
        {
            'name': 'Tinkoff Black',
            'type_id': 1,
            'provider_id': 1,
            'currency': 'RUB',
            'description': 'Дебетовая карта Black c кэш-беком рублями на всё',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Tinkoff Платинум',
            'type_id': 2,
            'provider_id': 1,
            'currency': 'RUB',
            'description': 'Шедевральная кредитка с бесплатным обслуживанием навсегда',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Tinkoff Инвестиции',
            'type_id': 3,
            'provider_id': 1,
            'currency': 'RUB',
            'description': 'Простой способ сохранить и приумножить сбережения. Понятные тарифы и удобное приложение с торговлей с 7:00 мск',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Альфа-Карта',
            'type_id': 1,
            'provider_id': 2,
            'currency': 'RUB',
            'description': 'Бесплатное обслуживание и суперкэшбэк каждый месяц',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'СберКарта',
            'type_id': 1,
            'provider_id': 3,
            'currency': 'RUB',
            'description': 'Получайте кешбэк в категориях на выбор с картой СберБанка, переводите деньги без комиссии и оплачивайте покупки со SberPay',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Карта Молодёжная',
            'type_id': 2,
            'provider_id': 3,
            'currency': 'RUB',
            'description': 'Для тех, кому от 18 до 23 лет. Стильный дизайн, 120 дней без процентов и бесплатная доставка в тот же день',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Наличные средства',
            'type_id': 4,
            'provider_id': 4,
            'currency': 'RUB',
            'description': 'Моя наличка',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Кошелек Binance',
            'type_id': 5,
            'provider_id': 5,
            'currency': 'RUB',
            'description': 'Некастодиальный криптовалютный кошелек в приложении Binance, расширяющий возможности пользователей в сфере децентрализованных финансов',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Alfa Travel',
            'type_id': 1,
            'provider_id': 2,
            'currency': 'RUB',
            'description': 'Дебетовая карта, которая копит на ваши путешествия',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Tinkoff Drive',
            'type_id': 1,
            'provider_id': 1,
            'currency': 'RUB',
            'description': 'Всё для тех, кто за рулем — за счет банка: услуги и товары на АЗС, парковки, запчасти, ремонт и страховка',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Детская СберКарта',
            'type_id': 1,
            'provider_id': 3,
            'currency': 'RUB',
            'description': 'Выберите дизайн вместе с ребенком',
            'icon': 'url',
            'is_active': True,
        },
    ]
    for item in types:
        cashbox_type_data = CashboxTypeSchema().load(item)
        db.session.add(cashbox_type_data)
    for item in providers:
        cashbox_provider_data = CashboxProviderSchema().load(item)
        db.session.add(cashbox_provider_data)
    for item in cashboxes:
        cashbox_data = CashboxSchema().load(item)
        db.session.add(cashbox_data)
    db.session.commit()
    print("Данные о кэш-боксах успешно загружены")


def seed_user():
    from app.schemas.auth import UserCreateSchema
    user_data = UserCreateSchema().load({
        'username': 'atlantiee',
        'email': 'string@gmail.com',
        'first_name': 'Yegor',
        'last_name': 'Mironov',
        'patronymic': 'Petrson',
        'phone_number': '89600880899',
        'birthday': '2003-06-12 05:59:40.991136',
        'password': '123456Q!',
        'confirm_password': '123456Q!',
    })
    user = user_data
    user.set_password('123456Q!')
    user.is_active = True
    user.last_login = datetime.now(timezone.utc)

    db.session.add(user)
    db.session.commit()
    print("Данные о пользователе успешно загружены")


def seed_user_cashbox():
    from app.schemas.auth import UserCashboxSchema
    user_cashboxes = [
        {
            'user_id': 1,
            'cashbox_id': 1,
            'balance': 34650.0,
            'is_auto_update': False,
            'last_synced_at': '2025-04-14 13:57:54.053179',
            'custom_name': 'Основная карта',
            'note': 'Много кэш-беков тута',
        },
        {
            'user_id': 1,
            'cashbox_id': 3,
            'balance': 5000.0,
            'is_auto_update': False,
            'last_synced_at': '2025-04-14 13:57:54.053179',
            'custom_name': 'ИИС',
            'note': 'Надо продать фарму',
        },
        {
            'user_id': 1,
            'cashbox_id': 4,
            'balance': 15000.0,
            'is_auto_update': False,
            'last_synced_at': '2025-04-14 13:57:54.053179',
            'custom_name': 'Доп.карта',
            'note': 'на покушать тута',
        },
        {
            'user_id': 1,
            'cashbox_id': 5,
            'balance': 36000.0,
            'is_auto_update': False,
            'last_synced_at': '2025-04-14 13:57:54.053179',
            'custom_name': 'Зарплатная карта',
            'note': 'чисто кошель',
        },
        {
            'user_id': 1,
            'cashbox_id': 7,
            'balance': 2000.0,
            'is_auto_update': False,
            'last_synced_at': '2025-04-14 13:57:54.053179',
            'custom_name': 'Кеш',
            'note': 'Все в картхолдере',
        },
        {
            'user_id': 1,
            'cashbox_id': 8,
            'balance': 0.0,
            'is_auto_update': False,
            'last_synced_at': '2025-04-14 13:57:54.053179',
            'custom_name': 'крипта',
            'note': 'тихо двигаюсь',
        },
    ]
    for item in user_cashboxes:
        user_cashbox_data = UserCashboxSchema().load(item)
        db.session.add(user_cashbox_data)
    db.session.commit()
    print("Данные о кэш-боксах пользователя успешно загружены")


def seed_transaction():
    from app.schemas.transaction import IncomeSchema, ExpenseSchema
    incomes = [
        {
            'user_cashbox_id': 4,
            'category_id': 5,
            'subcategory_id': 13,
            'amount': 15000.0,
            'comment': 'Премиальная выплата',
            'transacted_at': '2025-04-14 13:57:54.053179',
            'source': 'ИП "DevMark"',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 5,
            'subcategory_id': 15,
            'amount': 45000.0,
            'comment': 'На отпуск',
            'transacted_at': '2025-04-14 13:57:54.053179',
            'source': 'ИП "DevMark"',
        },
        {
            'user_cashbox_id': 3,
            'category_id': 5,
            'subcategory_id': 14,
            'amount': 13000.0,
            'comment': 'проценты с зп',
            'transacted_at': '2025-04-14 13:57:54.053179',
            'source': 'ИП "DevMark"',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 5,
            'subcategory_id': 13,
            'amount': 15000.0,
            'comment': 'Вторая часть зп',
            'transacted_at': '2025-04-14 13:57:54.053179',
            'source': 'ИП "DevMark"',
        },
    ]
    expense = [
        {
            'user_cashbox_id': 1,
            'category_id': 1,
            'subcategory_id': 2,
            'amount': 5000.0,
            'comment': 'Ежовик от Арсенчика',
            'transacted_at': '2025-04-14 13:57:54.053179',
            'vendor': 'ИП Маркарян',
            'location': 'База в ТГК',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 2,
            'subcategory_id': 6,
            'amount': 349.9,
            'comment': 'Флэт Уайт на кокосовом',
            'transacted_at': '2025-04-14 13:57:54.053179',
            'vendor': 'Skuratof Coffee',
            'location': 'Кремлевская 35',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 7,
            'amount': 1236,
            'comment': 'Самокат доставка',
            'transacted_at': '2025-04-14 13:57:54.053179',
            'vendor': 'Самокат',
            'location': 'Из дома заказал',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 4,
            'subcategory_id': 10,
            'amount': 42,
            'comment': 'Проезд до дома',
            'transacted_at': '2025-04-14 13:57:54.053179',
            'vendor': 'МУП ПАД туда сюда',
            'location': 'метро',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 1,
            'subcategory_id': 1,
            'amount': 2500.0,
            'comment': 'Массаж спины',
            'transacted_at': '2025-04-14 13:57:54.053179',
            'vendor': 'Массаж клиник',
            'location': 'Раскольникова 17',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 2,
            'subcategory_id': 4,
            'amount': 300,
            'comment': 'Кушал',
            'transacted_at': '2025-04-14 13:57:54.053179',
            'vendor': 'Добрая Столовая',
            'location': 'Ожегова 12',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 8,
            'amount': 1000,
            'comment': '3 кило шашлыка',
            'transacted_at': '2025-04-14 13:57:54.053179',
            'vendor': 'Лавашок',
            'location': 'Парина 10',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 4,
            'subcategory_id': 12,
            'amount': 36,
            'comment': 'проезд до уника',
            'transacted_at': '2025-04-14 13:57:54.053179',
            'vendor': 'МУПП ПАД чето',
            'location': 'остановка',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 2,
            'subcategory_id': 6,
            'amount': 349,
            'comment': 'Флэт Уайт',
            'transacted_at': '2025-04-14 13:57:54.053179',
            'vendor': 'Бинхартс',
            'location': 'Пушкина 10',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 4,
            'subcategory_id': 11,
            'amount': 36,
            'comment': 'маршрутка',
            'transacted_at': '2025-04-14 13:57:54.053179',
            'vendor': 'МУП ПАД',
            'location': 'Лермонтова 11',
        },
    ]
    for item in incomes:
        income_data = IncomeSchema().load(item)
        db.session.add(income_data)
    for item in expense:
        expense_data = ExpenseSchema().load(item)
        db.session.add(expense_data)
    db.session.commit()
    print("Данные о транзакция пользователя успешно загружены")


def seed_db():
    app = create_app('development')
    with app.app_context():
        seed_categories()
        seed_cashboxes()
        seed_user()
        seed_user_cashbox()
        seed_transaction()


if __name__ == '__main__':
    seed_db()
