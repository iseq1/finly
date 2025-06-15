"""
Скрипт для заполнения базы данных начальными данными
"""
from datetime import datetime, timezone
from app import create_app
from app.extensions import db



def seed_categories():
    from app.schemas.settings.categories import CategorySchema, SubcategorySchema

    # Подготовка категорий и подкатегорий на основе структуры
    expense_categories = [
        ('Продукты питания', ['Овощи и зелень', 'Фрукты и ягоды', 'Мясо и птица', 'Рыба и морепродукты', 'Хлеб и выпечка',
                                    'Молочные продукты', 'Бакалея', 'Сладости и снеки',
                                    'Вода и напитки', 'Полуфабрикаты', 'Для детей']),
        ('Еда вне дома', ['Кафе и рестораны', 'Доставка еды', 'Фастфуд', 'Кофе на вынос', 'Столовые']),
        ('Проезд', ['Метро', 'Автобус', 'Электричка', 'Такси', 'Трамвай', 'Троллейбус', 'Поезд', 'Самолет', 'Паром']),
        ('Личный транспорт', ['Топливо', 'Мойка', 'Обслуживание', 'Парковка', 'Штрафы ГИБДД']),
        ('Жильё и коммунальные', ['Аренда', 'Ипотека', 'Коммунальные услуги', 'Интернет и ТВ', 'Ремонт']),
        ('Дом и быт', ['Посуда и столовые приборы', 'Хозяйственные товары', 'Электроприборы для дома',
                       'Инструменты и мелкий ремонт', 'Текстиль для дома', 'Организация хранения', 'Освещение и лампы',
                       'Батарейки, удлинители, зарядки', 'Декор и украшения', 'Прочее ']),
        ('Уход за домом', ['Средства для мытья посуды', 'Стиральные порошки и капсулы', 'Чистящие и моющие средства',
                           'Освежители воздуха', 'Салфетки и бумажные изделия', 'Перчатки, губки, тряпки',
                           'Средства от насекомых', 'Уход за обувью', 'Пластиковые изделия', 'Прочее']),
        ('Одежда и обувь', ['Верхняя одежда', 'Повседневная одежда', 'Обувь', 'Нижнее бельё и носки',
                            'Аксессуары', 'Химчистка и уход']),
        ('Красота и уход', ['Парикмахерская', 'Косметика', 'Маникюр и педикюр', 'SPA и массаж',
                            'Уход за кожей и волосами', 'Парфюмерия']),
        ('Здоровье', ['Аптека', 'Врачи', 'Анализы', 'Стоматология', 'Массаж лечебный', 'Медстраховка', 'БАДы']),
        ('Дети', ['Одежда', 'Питание', 'Игрушки', 'Образование', 'Мед. обслуживание', 'Кружки и спорт', 'Подарки']),
        ('Образование', ['Курсы', 'Онлайн-обучение', 'Книги', 'Вебинары', 'Репетиторы']),
        ('Домашние животные', ['Корм', 'Ветврач', 'Аксессуары', 'Уход и груминг']),
        ('Развлечения и досуг', ['Кино', 'Театр', 'Концерты', 'Путешествия', 'Хобби', 'Подписки', 'Игры',
                                 'Бары и алкоголь', 'Подарки другим', 'Встречи с друзьями']),
        ('Финансовые расходы', ['Комиссии и переводы', 'Штрафы', 'Страховки', 'Банковские сборы', 'Налоги',
                                'Кредитные платежи', 'Донаты и пожертвования'])
    ]

    income_categories = [
        ('Зарплата', ['Основная работа', 'Подработка', 'Бонусы', 'Надбавки', 'Премии и вознаграждения', 'Отпускные',
                      'Больничные выплаты',]),
        ('Бизнес и фриланс', ['Доход от ИП', 'Самозанятость и фриланс', 'Доход с проектов или контрактов',
                              'Вознаграждение по сделке', 'Партнёрские программы', 'Онлайн продажи и маркетплейсы']),
        ('Пассивный доход',
         ['Аренда недвижимости', 'Проценты по вкладам', 'Инвестиции', 'Кэшбэк и бонусы', 'Авторские отчисления',
          'Доход с платформ']),
        ('Государственные выплаты', ['Пособия', 'Пенсии', 'Материальная помощь', 'Социальные выплаты',
                                     'Возврат подоходного налога', 'Субсидии и дотации']),
        ('Личное или подарки', ['Денежный подарок', 'Перевод от родственников', 'Возврат долга', 'Продажа личных вещей',
                              'Случайный доход или находка', 'Сдача вторсырья или макулатуры']),
    ]

    def generate_data():
        categories = []
        subcategories = []
        cat_id = 1

        for cat_list, prefix in [(expense_categories, '89'), (income_categories, '21')]:
            for name, subcats in cat_list:
                cat_code = int(f"{prefix}{str(cat_id).zfill(2)}")
                categories.append({
                    # 'id': cat_id,
                    'name': name,
                    'code': cat_code,
                    'color': '#CCCCCC',
                    'logo_url': 'url'
                })

                for i, sub in enumerate(subcats, 1):
                    sub_code = int(f"{prefix}{str(cat_id).zfill(2)}{i}")
                    subcategories.append({
                        'name': sub,
                        'code': sub_code,
                        'logo_url': 'url',
                        'category_id': cat_id
                    })

                cat_id += 1
        return categories, subcategories

    categories_data, subcategories_data = generate_data()
    for item in categories_data:
        category_data = CategorySchema().load(item)
        db.session.add(category_data)
    for item in subcategories_data:
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
        {
            'name': 'Электронный кошелёк',
            'code': 'e_wallet',
        },
        {
            'name': 'Валютный счёт',
            'code': 'foreign',
        },
        {
            'name': 'Мультивалютный счёт',
            'code': 'multi',
        },
        {
            'name': 'Бонусный счёт',
            'code': 'bonus',
        },
        {
            'name': 'Подарочная карта',
            'code': 'giftcard',
        },
        {
            'name': 'Накопительный счёт',
            'code': 'savings',
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
            "name": "ВТБ",
            "full_name": "ПАО ВТБ",
            "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/VTB_Logo_2018.svg/960px-VTB_Logo_2018.svg.png",
            "alt_logo_url": "alt_logo_url",
            "color": "#002d72",
            "second_color": "#000000",
            "alt_color": "#DDEEFF",
            "second_alt_color": "#A2B0C2"
        },
        {
            'name': 'Альфа-Банк',
            'full_name': 'АО Альфа-Банк',
            'logo_url': 'https://fbm.ru/wp-content/uploads/2025/04/alfabank.png',
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
            'color': '#046A38',
            'second_color': '#003B85',
            'alt_color': '#A0E720',
            'second_alt_color': '#42E3B4',
        },
        {
            "name": "Райффайзенбанк",
            "full_name": "АО Райффайзенбанк",
            "logo_url": "https://adindex.ru/news/adyummy/315689/img/photo_2023-09-08_11-57-12.jpg",
            "alt_logo_url": "alt_logo_url",
            "color": "#f8d81c",
            "second_color": "#000000",
            "alt_color": "#FAFAFA",
            "second_alt_color": "#333333"
        },
        {
            'name': 'Наличка',
            'full_name': 'Наличные средства',
            'logo_url': 'https://images.wallpaperscraft.ru/image/single/evro_dengi_nalichnye_211993_300x168.jpg',
            'alt_logo_url': 'alt_logo_url',
            'color': '#3f403f',
            'second_color': '#003B85',
            'alt_color': '#A0E720',
            'second_alt_color': '#42E3B4',
        },
        {
            "name": "Газпромбанк",
            "full_name": "АО Газпромбанк",
            "logo_url": "data:image/png;base64,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",
            "alt_logo_url": "alt_logo_url",
            "color": "#1E90FF",
            "second_color": "#000000",
            "alt_color": "#C2D4E9",
            "second_alt_color": "#879AB3"
        },
        {
            "name": "Совкомбанк",
            "full_name": "ПАО Совкомбанк",
            "logo_url": "data:image/png;base64,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",
            "alt_logo_url": "alt_logo_url",
            "color": "#ef3340",
            "second_color": "#000000",
            "alt_color": "#C2D4E9",
            "second_alt_color": "#879AB3"
        },
        {
            "name": "Ozon Банк",
            "full_name": "ООО Озон Банк",
            "logo_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARMAAAC3CAMAAAAGjUrGAAAApVBMVEX///8AWv8AWP8AT/8AVv8AU/8AUv8ATf8AS/8ATv/y+P+2xf/r8v8scf4TY//k6f+hvf/N3v8TYP9NhP9Tfv82d/9hh/8cZ//L1f+Bpv/L2P8ASP8AXf/2+v+rxf/k7f+4zP97nP9rlv+/0v/W4/8rbP+MrP9ci/+fuf+XtP/a5v9+o/+wyP8xbv9ejv6Rr/8AQv9wmf/Czv+xwf85dv87e/4AN//1n7ZhAAAM/klEQVR4nO1daYOiuhLFLAgM2uLStgvivnbb3dP6/v9PeyKSqkDQcR5wfdecTzMklMkhS6VSVW0YGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhr/CrhB4DoPIjZ8Kf+m3IX5z/TQbQ6HzfpHqzfLrTXzn/2hWw/FLlrL2Z8Ss920FmFbuofJuIBv9EcIlnWTckbOYOz07+M4WWe5qN3AYpZ4xV12QSw5iWWtlFjDeOkKAaPzg3HNNOO2cMp3/8RweZlaJqlIIKxa+ZFrTUx2A9ZYFrsaKMQOR6mfH8QCqo3Tf93WgEnvmNa6wM6rsbR4RQFSrXm42kRZC8Meo+r+0laLtWSxJ06suIyeOPFY6jVirYpnAWN7sLP6yOgnqngfJ9saJRnVmPkptUDipK98jZZKijdkijbEH6i6h5p3cTK7Ktbe4yYgTn6Cpvo9S6axUHj8SttPMOED3cNJ37wulraUnJiNVsaPEB6URcmWZA1w0frpX3ASWDfFTlSckG4mlfy1JEr8hdyGcB9mie5Yjfs5ad4hFnNSIZkvkEpJA2VC8c8ymywOnUOdSjsooZfGTAfVNExc07roJxNTEkvJRyctlok+Ik4u7ahEL3D8Ai1nQ57b6EcZbb0Hoc7ozpddvPizdlR720/DG6HBQ3tRRY9LYlfjwI/EDjFXXKxUMieEvsYvTPCqxFqp9heBFvpJvuhDgb/EpAz6mRLcOtSr7pRikTLi9LBYKy6ROCEMKcNbNLdJtwwlf4sGs9nypbIxKsv+QnjnFJTM0WjgHfmFMVWIxZwQc4vru02oT8tYUNC0Zx/Jwne08GXtg5gS5f7EOslX3tEKNricYzAndkOu34D6VvZwzQ3+QnwDwrep4il0jTYUr58oqaso8bsglvyRWMQJOyQbCdJo6qCUP+YwPcxdutiFlZIpdQM1JcYcemj2FGIRAZdVFnGSZn/PssvyBwzLxCS+AOYA6frpYmniIF0diWUqsXsQO4yeIJ2NvSSrb8QEL4MT6HN62oeYVa91TqIEL8JIbHIinDG2k2IRJx8p8n+L6mVw8io6xb9V5S7MrWpqeXPRxDGlfQl2Yj5JvhXCQXMrEgucKCbpm/gyZXDSEY03lSqig5a390SZiw4mpnyO/7i1AMD2av8+PwBOFB+nVE78j+wuRzhk9u4KJUY32eUkaiA2suQhTtKLcrmcwFZsJ+2oEdpZA+kaJelhkMThgTlB30u58/uHjAoSJakVAM24sfKH4VvQX+cHj8OJcYRhsFGVo/VEMrQa6BBitlOvHW6INcAIQKPx+UCcrGCDmKrKA1Cr6Rwe+wfQRBWUoO2M7dOlJ7EDeD06BT4QJz1QnhYKncwYgfKF7DlOB1GiOhxisaqfRTodiQ48D8QJKE8VqjpegaKBToh+Bw6OybN0BKAy1j9kgApA6tGTB+LkBSY2U1wVbEG34jAJ0MThNaVBA025W2IvU/aBOEGKQqWa3o07SHcX+ssRRglfZNh4DujFq2LjlfuRONnAFyUseSe7w4XxHGkji4vqXJgSmzIs70ACsS/PHokTt4KMXs25VIYoEZYEX6Ik0xIYYLGJ0+OuisTGBDwSJ/ijhReW0EvviCghVlTgtxAlhyvGUSyW2J8wAmWxwnr3UJw42MBOaH063gbB1tu0bXw/Qy/DpI27eli9KtA+rx8uvkgjZnMyngfBy0kslcSK/j8UJ0ZDvkXgNq80CZXvNVk3qut8SXXVzhbRGWBtJ8UOhymxsEQ/FidGS7qdCtWo5GUpsS9KhjOo3ER8Lkrd+qbFIpXowTgxajcuPIloyT2cGNn3vhex2D7/aJwEi6ukECrOcXdx4t4QW8WuE4/GieEeqbrdIRj6nHdxYgQdM7sak+9+H44Tw5hYWQPdbKIDy32cGP4k09/CrMvnoAfkxJh1q4rmE259YyXkTk4Mo1/PELtL6DaPyMlpT65XubQzEEare1kvd77oTXzJBrtR3U6KNe196l7kRUgepO/e3kThV9nej/1pnVOTn7UMTmmls0kegPyfXzfxk+xvJJaB2LXC19UByV6qMPjJFF4C5uPetH1C63vdz9FLd/6rt2+dxL5+r9/+aV9xDQ0NDY2Hh6/3ijN8N5h7s9FmN31t1yrPTUrQ/+lNV51Ft3k6ptknFS7U4QbPy4n/vh+eNM1QlSWSZcl6Vk686YBydTzCk3KybakjvZ6Yk0062uzZOVmpzBxPzYl/uGIkfFJOkrcZmpNEVJOMc/g1/3o2TmaWgokTEdykVYs1F4fXadJ6+q/HUFpew+h5y6zX2vvdZ+NtW0g6h4fHBs8cVmWvn+9bx8lyLHkOoNhMVm2rPYefDGvkjleb367/DIBwAVPpIfuEmAuXnL8J8vaD+Qnbf9lO/Rmra8gVb9t/+/X7zbvV05f16qNiWpbN651lfFHlCIhVWvEoXeTcqu0o6hYEEXcRO/HNpnVi2tSmfPixS1/JCXgrRllkWQiz3/CPaHWmzQuGsV+s2x1eHlWSrrLOIi4aCm/sihBwxFVFzWaTF3w/KmJ3LzFo6wrc7hLGq92MO2t3ZSVyCTDrGA6swSVHEOFxL916nDcoNTudrkgpJJz2zViAFDW3F48JLXrZ8+Ib+7Pr+PaQPB6T6kLlGz4jCssCH56qCscDBpzEMlNRbRD1AZyI9Q0HKDbAfVQdt5gnxE4c+niPVQlL2CDt+zBSp79hfF4MJyj5ARsWvqCLAE9zY7wnk0FdYO8Ta+PIzjC2sLoBoY75ceJAsBAxryxxOUHEXdC3eTI7iUAiHMXLTvZiQpBKjpzswZRhlREjGXPC+7VsN0WKQzmd4RWTHMjIjxPkaWsrYuXzBurfMf7CoZ0gab23UFDpt2yAOu1OpsnTYyw3TjzwF+NlpD9xUZxN1ENOh4uPjy6RXMBxyMZcSlxD6LC926x3r3WaGGZ5cYJ836/EPOSIbcKcxMn3LMxP47y8v0qdhLPQFO/CZrdxIcuZdeTNKC9OwB2bmKUcUb0q7kbFmiKXPu+IJ0lskcVBKKcdCX+4jTSCcuJkiXKfqKPC88ZMChRILupTHL+zjJ6h/Czy0mvIeXVy4mQGg89a5tr1TOCMNYp9Dm2C5BKZAVGyihUPE5YLJwHsAalY96KA4juVAcYQcX2JA/Zh6qiSpbXu24v9W5wcQd1RB2MWAMQJIYqEScikH7nHowQ4qiwec7SPpTkhtVFDwrp5nRMIviPD0hxjESfqOPRFIqAcxWBz1S4AVjsFJ6edWwasPypOjuiLKGJaiwLiRBHyekJPrCisFv5fmKAyAswhy4+Kk2woOCE1WEwsddaDQvCOQu9TWYxCoCQ/Z4UJJQVSJiKAzf1/5qQCyrR6DBcE3GXljU4AaY6aoYayv5Gwwr12Lr6TE4Bd/GEYAEtmOmHdGZBPiQzDNRg2FvqjfOGa/eSvOcn4YMXAFeMkWi7SFbI5+aV8IU9OUIoV5UQtBo7YDNVLJiItmjuQL0UdXeTnxwk7tlEuhRJjmUQ2hajLKXgo/a+8xirCsQx8qFRyQhK4zokLij1h5V1RQh+pch1bw956NqMvzXQvMGBzV+on3JTAr+onHZyDM2NuFwHogyovo5R87rwfogQ3Q5Wy3bqms6Wz0d3S7adw4KLK5HdFAHLCKHMH4cyU530G5lLFVCTqwjkz8zgDOihuO/EHFgoEJN5KZm0NAUvqRZXHVi9FJkecNjYfW4GJVLiyMrlv0GRI/SY6cLDLvgQcKhJme9iXJR+b0g7nFsmr0zcQwOKfynqDyirxn3L4RCaV5F0LzmOXm+0RJYKzlUteAfhGw13ej2cMJceuXh6iJLyn+SSdG+d1bMHNixP8pwPKOh0HOGM2X4vNxJ3gu2MqDH84ITmxJoJFZylb7nO7y9iAfTRDicofPZzLhza/R9uXF6+xYlIm/6aYVjPJmdZk+8b85WU7mg4Td8j53XmhRCqlXPCEkPKUEE6r3LSpfIlVHUP1o3zzE9bnNk0d3fLjBF8V0JIMKV7mH8mJIV1JetfCFXLfd0K8o9mjVrfzx+jGX0BJ3KF/pv2uRZPBqJ2nrwVSZ1mzJLNB4+pIoclJvM/yzyfW9pqd7a858dH05mXdaTSy/yoRsdKGv5WaFGJtCvJT6iOPl9LMBv16hkMOr6iaMFF55ZAw21oxnOAr0vLMBv5E9RfamLVSHzJGw1TID+fhobAgTtAlSYXVSrNEBtOBtAMTRgerzFXeneDahJhfUUqd/1gXDGJXTpeJR0mTizMUReIsMxCPJMvf1rYEvko04zuNNgkT5fAwdMdkR1U+G4C/7jDzXJtSXu9dxpMnIC7uFI/SRfMrj87YQoHXLzVqxJ+P173v791m7P3B77r9n8/Jd2/9+x/I6KOhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGhofF/j/8Coa7xyzHl66wAAAAASUVORK5CYII=",
            "alt_logo_url": "alt_logo_url",
            "color": "#005BFF",
            "second_color": "#F1117E",
            "alt_color": "#001A34",
            "second_alt_color": "#00A2FF"
        },
        {
            "name": "PayPal",
            "full_name": "PayPal Holdings, Inc.",
            "logo_url": "data:image/png;base64,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",
            "alt_logo_url": "alt_logo_url",
            "color": "#0079C1",
            "second_color": "#009cde",
            "alt_color": "#E6F0FA",
            "second_alt_color": "#005EA6"
        },
        {
            "name": "ЮMoney",
            "full_name": "ООО НКО ЮМани",
            "logo_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAATUAAACjCAMAAADciXncAAAAxlBMVEX///+LP/0AAACELP3IyMiKPf379/8qKir+/f+HNv3S0tL7+/v29vbl5eWCKf2QkJBaWlp/f39BQUGGM/3w8PDu4/+np6cdHR22kP51dXV8fHxqamqBJf2zs7Pf399lZWXk1f/Vvv7q3v+QSP328P+lb/6bm5sMDAygZf7Msf6XVf2JiYm8vLyUT/3Gp/46OjpVVVWxhP7Bn/6cXv7l1//cyP9JSUm7lv4mJiY8PDytra0YGBjPtP7ZxP/38//EpP6rev6ja/5P6n37AAAI1klEQVR4nO2daUPiPBDHC6VIAQtukUMOUbSKgBcuPqurrt//Sz30mJwTWthdkXV+r5a0SZs/M8lkElyrYRHrQpoRBEEQBEEQBEEQBEEQBEEQBEEQBEEQBEEQBEEQBEEQBEEQBEEQBEEQBEH8+5yO2xI/D7f9Rp+e4Z3j+a6E740eSTgzpfGo5zo5DcftzU+2/XKflWvfRyRLhLNzpBvCcGQbNYt08+bkpwqlu95KzSLdevfbfs3PxenIT9MsxJ6fbftNPxEvXqqhxbju6bbf9WMoGinBLSe9bJqFXmoPt9iXj+OqZ6N4Hqi2hmjhpPCw1e58EGPDiOU4iWrf1xEtlO0rOOmZt1q1U8N1s2zu65a79BHM8ZE+Ua2YyzgRcNyrbXfpA7jGXTRR7dxdV7Rczm9vu09/n0PcBWPVXtb1z4jeF5gRrlAfjFQrOWv7Z1T3C/joG+qikWr3mZYEOva/v5THXTRUrWhvJlrOGZkf14iphP8uN2udWrMsXt7vB0HQHxgqVwvBUbd7FBQq6oWE6MPgaXIw6Zf16skjprVOtzsJpBsqUgt6w+oDrRnmhqFqholiiev7tr0ic2S/mF65kI85sKzmcx4+wDsVbqBosq/Xnd7mGV1ZlIukuGJVa/DvfAcTv8kekb8IuBbwXvmadHcNirU/i4j6YaiaIepwfO/87WQ4PHl7t00x8jxNtUmFv/2SuH/HYlFTqdnPy9TFjuwlhbz3sbaaZkojfa2FvHQ/FB5pHTnFon/HsYb4BOr610Wo+npvyLr1TMk26FW3pb1+ZU8umoj1qou8xlRXTVXlRnp444fWRl3TU2jVmkIhYrUjLK3tWG00VrPfi2Ldszlqbv51imoaBdn4lPdvXGB1uDnuYZdDjoVnD7AbfiQXK1DwTajxLSlbID15RORxciXUQe1HtfYdNmcYXdSoGsIFq1V9xu9gDmZULV9gjezjN4AiR1DA7YrJLNof8IC4opNDV6D+nV4dXT/YRf1GTbWW3tkbsYj1GHFPuYdm1biZmO45UCTqsBpMSLQriFU5o5+I66HxawnzcFPGSFDtKZzlC/+JKobfaTVQ+2OxkotgUK00Cl0usqZIa9qwKoMmHzZh0piwkttmuVwIeJWy8tXAzMqcNkC7goxgzuwOMSE8DfQd8VF/nKYahBZ8ONtLXpd96wvl7dkgVWYeO1VUY6bFlE28uMGUh5jlCUqSoY0N/TBcsgkC/2vMyGzpzJBkiHuOS4EsylzDEp6pxoYKPtywEIy9f/wRTK3Om2FTx42iGo9SoSgJwMDUWvwO9i7Jg9m3p7SgxS8JyObwDAl+TcErEg67v1JU40UQu/LBnxlXbHwt6VNMFW4ZSB0UohUwpa4siRg9w9eRRGMspI1VLGvfpgLijaOR7naeIeGITBymSRRUEyICGHMFUwIRItcAY5SjdnCfQKogdHAgNQuf5Ng5iWee40/MieOXg5hbjvkEsJFJx3EN1c/06qalqLCiAuAr5nMXM7/IMMBf5UgTuliXVBNGoH3pBrC8byKLllyNrU0aooZ9y0BJdzHE1pycqbqeUVpGyStVE1wJVBOErIuqgVUpLT2LdgKqCU4sq8ZnUIyC/HKRWbOJ2ySaZf3SXBRTzSnhtYvIHPznVEuuXygt/RA79ZuqgTmxMMjiCYGJZeRF87ERNhsYQlck2WSyy81VU79z6GE1k2pspEfRYo0pn8eR5AugpdKcGRJOmPaIT5BxzZDP3UA1cBUl9SWYRQbV1GW9DNgam5kXbGitWytQl0XO7BIJwrRFaIzu36mRxxqqQYqoIDXEwrxsqq1e/7Km2RqqoF3CUM0FXRs4LjqwIVOoUeANVIOgoSM1BLXkOdSoGnx6KmMwM9bSIv+tEk1zUXwd6qNaIKaW8w1bBxuohgaoLC6Q4zWjajDlytLrQG4IUHOjCu9y153REIvhsEU5uv1nSktuotoBfO9cE56Mi29JVw2eogT6NWWwZ5NAgrqPoKC4qJMroolxV1PjAc2vmUK7TVTjK1UYtQcsREhW6+mqMeMUg+XGQktoyKLpmW+ZV9lilvEWmjdzXMXahmgO3DQZbKSa1eHd6AbN5oGQ9S1nVY3HHmyPpREHcTfSokMOUUybZQx5zlyqhsQT4QXvXojaXh/xE4H29z+pWiVvAprJoJqQg6sH/Wm/ttBaEatFYJlvGflM1nIdgLroEt9vD6MapWHbN50SMT1lI9V4+kFBU2SVag1DI0r4XxcuYJlvGflMVrh6wubG6Jpru/PLyyvXM52dwefazVUzhFs8As2imrWPbtmo2giPUhdxGFIaMlQN3fKDy86qMyCe8VjzhqpZA2S/RWgjk2pW9VZvJH+sTpM8eY5nvmWk3GK0Un/f4BxWiIvsySiqCRLBwlqYr3TVhLA9oSXGEDCnrlZtGVioWy63esqRL75Swo4IaQ0eqXa43ulShm0+QQ+qCSnGabcT0hXyWJDokhL2+xPBw/aepGZvnlshsmpR0cWxdKNVPuC2tKdGaxFsMWrKfMuI6/U4K9Te6FCRbdpC/m0GTwfHi9tObboiEZFOo9wParV+wWBKbBY1nq+REM9kxarhO8kp7PrxNYgOjZlvGdEhkwzkmifAI4xnPHaD9My3gpCIhLxte+0zbJ5hJ3RXYFnfrBWEM1ks23255jxqm+fPnYDNBbX0e2OEAI2pVrpaSzbfsNG8M7BNluz//TEf/PnOylqy7bxoLOdxnH4r0O55Cb0eT9teZo4/vB13T+FEZrawI6J4yBGK77L97MDpvf3xXnw0sMjYS781lXH6T5HDo6em9NDuwFK5T+n3pnN6tfpn72He7f0f+CXytJmgnZTfjLFjPigf/px2tvuG9jcojXMme3O92b//a5ZNKf2ce5rBOa5tn5OdreRsPPc923WjrKTr+rbnnp8YTn8QAsWHk8df75dLzu/uX77C77UJgiAIgiAIgiAIgiAIgiAIgiAIgiAIgiAIgiAIgiAIgiAIgiAIgiAIgiAIgiCIv0aWvzdJyFT/B8zfnySwWSNLAAAAAElFTkSuQmCC",
            "alt_logo_url": "alt_logo_url",
            "color": "#3d0c6e",
            "second_color": "#000000",
            "alt_color": "#EEE6FF",
            "second_alt_color": "#3A2B64"
        },
        {
            'name': 'Binance',
            'full_name': 'Binance DEX',
            'logo_url': 'data:image/png;base64,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',
            'alt_logo_url': 'alt_logo_url',
            'color': '#f3ba2f',
            'second_color': '#f3ba2f',
            'alt_color': '#f3ba2f',
            'second_alt_color': '#f3ba2f',
        },
        {
            'name': 'Bybit',
            'full_name': 'Bybit Global',
            'logo_url': 'data:image/png;base64,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',
            'alt_logo_url': 'alt_logo_url',
            'color': '#000000',
            'second_color': '#f3ba2f',
            'alt_color': '#f3ba2f',
            'second_alt_color': '#f3ba2f',
        },
        {
            'name': 'Telegram Wallet',
            'full_name': 'Telegram Messenger Inc.',
            'logo_url': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAATYAAACjCAMAAAA3vsLfAAAA21BMVEUVyP901PEAmOoAAAD///941fAAlup22PYVyf8Alep31vFYobgZLTQAk+l32vhtuvBUma5gsMhu0/IVzP8oSVNpv9lZ0Pah1PYSISVCrO4YoOtY0PZj0fREzfk6zPtPzvgWz/8QmMIHRFcJp/EPuPggOkLl9f0PkLgxWmZwzOhcxu8Lr/QHpO8RvvrB5PkkQkt5w/NKhpmv2/gMcZDP6vtOve47su1Tsu9Rv+44ZnRPkKMTtumMyPMMdpYNGRwIDg8FNkUSqthCeYkJWHERZoE1YG4OgaULpNMGOkqUJ/PcAAANbklEQVR4nO2dCVfbOBeG7QTHimlciAslC0lalrKEUhgopQu0TOfr/P9f9HmTJVmyrfheTZycvOfMGZImtvX4Xt3FsmNZOgocm4lofWUjy+ozaM5k2QezMhoxY3NGyz6YldGEc9H+sg9mdcS76GZi0xXvoofLPpiVEe+i42UfzOqIc1F72ceyOppyLrrJPXRFNi5aR+ONi9bQZOOidWRvXLSGuHiwqeC1RTaJbh1x8WBTi2prEw9qiasP9pd9LKujySYe1BEzNme67GNZHR0yY9vEA30xD13TeECm4/54hDy2dTe2yb4Tj9AZo87ba21sZNrn4l2At2HO2NauGJ2MHf66L2aewBkb4slogIKRLTLDNIx1NbbDscQMcxricrb1MbbJvmxoqKYxWT9jE6NA3txwZre1MzYpCpjw0jUztmBa5JyZUKpH1mdbA2NTR4GcMDo8wfoYW3EUwMc2Qvb5Zak0CojCWH7GtrbK1ehkrGdosXkgXClhqe7qXnch1VFAwIYwhXO9cPjGlqKJThQQhLBPZmwr2dRVFZ1VQoh8XPaxelcQyKF2FOCFEBFWOPtYJArwQkgYuICwWtnHAumGhA3uViwgrFT2UVF0Vgi8+2AVA0KdKMALPhtNs22tTECoFwU4IRgI5in4LwRzzhQbeBKfrFRAWLAWKJIH9itWxTe/QsAwtFjw2Me21fA1RoFmR0hH4KGuio+CowAveMNin20MY3RmpNt61MYGthCW6zbVRwG1QKGgxxQY81HCBNnM4lHAscdVHwFHBJbrYvpohOrq+PIo1OXl8ZVVF93itYBjj4Jw/xWfAjuWAR8NER1fDjuhWqHi/88vr2qAqxEF0uy/Ahs4IhB0HyXk6qiVEOPU6QyPrYXA1YkCzn66iwovBTfEufUywC0lCqHN88goudalNrhaUcDp0zM/rfoydJjstKDUo8Q6KoCWgDvWctV6tQB7gEQlNfBY2U4xrliR41YJtQjcvNLgNJYhKKFlplZNDbyOgUs/4D0jQi7LocW6Kt2R1jIEFTVGonoL4GmcnRh4bUusoQa1Vue4kNtk36sJrc+2qcEdbCJsagNfyNGkFnK7VB41pBbgJph+9afhJsJOANRuiaXFrIgboCPEL5cnOtTAEYFb1Aae2oba2CQ/rRkFEmg2d8IDva9AIwLe1EbKEg+ZGx8X6kaBBAFf20w0vwP1LDa1AU8AOV6EWij6RVjrkcs6LPH2xNJvwcaKN7WRq8WgtTpHsbkBO0Kitx3qbgvsWVhZGzlaEFvopuDrAk5fqCyrk1wqaM9igjS1kSvRRTsqdcXPDAXndAskfMQPX7q+T99Msg4SRCLWviNtrQg3tB5i16xgJ4AIUbTbenit0lFP+NQXj43kfLtAe4zE3s7j9atX149fd12fZR3k27tI3/iw4u4mXy7CBm1/ZBEBdgJEY+t9Ot1S66OQDw+5cW63C/Q1MRnX3r5mb57s2C6di4MP8VuveNP1k88eFJkbkBpbnwU7AWTOW9GnAmihTnlz611ku3d3i7DtxEP3d1+Jbx+8mxEBW/vM57C9SVAWYIMmu9yiehA1wdiGxdS2tt5yftoZZF5agc2/kf/hr4AI2No3jFsFNmiyixQRhL5H53VI53aQ6jZ88ZD+/RCZmxAWskKoHJuKWrv9OxCxtXczbuXY4O2PbFOgiCD66PeQzqCbBM/e2/DFMI2kvY/hC7WXlmLzv6r/6cdMxNY+p5gqsKG1P4AhWQiQkVHdpr6YYOO8V7C2zmfqpe7u80Gip4TAU/ryecflkJ683Nz8/pm9fBeI2E40nRRIjfVYQHabT9qiOWzQkbDFxvZWyEHmLAXxU6WMtunrcOQ0Gpzs+v54Npv9ep++8RQ1iqc7zP4efR1s4IY4To2QK0fjSHrXy2PrDPKRlJ/cqKhp7WQjdqmLPobpa3x2g+Av5qYjj8PW/upXYwO3P7ACaa4T3o3StodODlvvLvzzU1f4ZEe6LCdjsw+oJXm0kUpmKbfnsDRweWztXbcaGzQisEAKslshIkQw4pDZE7HFAfZOpMZnbkXY6BsHfK+DkHSC2/ZsEdvTeSU2cGOR1b6ghjjJ9yfjWSw2LIYtNsFBDlv3SzW2NPnYEVwreJe8++LnsLXfuFXYwA3xbIUWzN0lbJ0hncYybPGEd9tr5bF5uTFJ2Pyz5A3RRIj1HL97wrDR3C4kWY4NvGSD5R8gd5ewJbSioMmsbYvLRBi2+0psaRz9ORP3OUui6bOdYTt/Sblt+6XY4JeDWf4Bq0gVFxFOE0oUW/z/73lj08KWmNXfM3Gfs98prAzbXsoq/MstxQa+HZLlH6DNKLBRn0yxMa9deG6z27rY3PM05r4qd1LQWC3hkaew7cwVQO7inDfFFseI113pUxqR1ElYvJ+J+5yeSdhYhXZWhg0cEdBau4oVDN1BnPOmNemAJcCCOhf5QeWwOX06iYmuNfUOKBiGzfZpUP16VowNcYU4rNxQLvzoxb2PBFvvjpVboqqqhMPMG//w3EbeLrUrHpvtP6bcDgqxwSPCIU7aJtWkiYaxhcXYHlTJR/yZfEQQsMVtb5qh8V46dmhasiNYW/j1kzYnJTbEm19gVdpkX4WtFzWQHiJsrTtV8tHiOyBKbHFWRKyUwYcZ3V9IjfbQz+0ctvMqbPC1jyzbBRhutAzBU17t64RJyF2E7bUy+WipIgLD5tE5iNafbdoG79u0TdL+x89hExt3KmzwtY8I2W6yDMG7l4NkGBUiXKfJf6fqS/byMpcMW3ZI5Bul8MOaBSRwfTtr9kaoRGxCJ1iFDX47JLTbxpYkj1XYkp5HogcVNu5agoTtA4sAwf8ohqcff77t7d480ddRHZXHllVjamwIy7phRcKEW4ZQ4KWD7EKfykVVPqrCRsj7tlJJMzePjbU1ldjgS0ZB2xIWCXlf1OZ2m2JTL0YaSoNSYgujwk8VtYPk0oGEzd0rwYbwKACGbeGvkvyKF/XatqF8lY+DKhWkBdhCbgp7O0kvuMjWlsVZBTaE1fCAkjQ/l3tf1GS+x9iUSJXG5ri/FNgsEvzIU3vMQEvYbP+lCBvCDfKAknQkTUqe2g+jJCTfCadIL2Rjc0bBHxU2i7DrLrGu2TVRBbbiUh4hIpD6Jak8lTsXSmzdwenWRyU1RRiN2t7k17/vQ/37Jx+lyHjvJS0BTl72fAbE3b5+E+qax2afR2+9+UfGBqYGwKZatOjdK9200xoqqSlytsSBkmVXgRSkwsnUdc/3Qp3nVmApF2UVLNRCiAikdiWvXLXoKWv1InXzLlr+cHS99d/VQriHsT429RLZvuZdCTE1KYqW1nd667+rhXF/VFAbG1Fic/ra1Hq5Gr7iOfya6781sCE8H7A+toJVss644ja1Amriam9Zuuu/NbDVhsUEwKbIQJLxF83/pdQqcint9d/Vwrj1s/7cZhXdwu7YA2U8FSVEg9xqb1n667+rhfG4MBA2K+q09eX18d69dLe3qO5w7C0yErVd1xPKXe1QbJaSnDfOr1gQoLXueSut/kkWyG1FMjaMp6whYIu2cph/NKR3MS8A12197nOmJtxjphYqNZyHAeBgs2Ryjn0xyN+7EdYLOWjcne2FQkpykcaZjhYLWyTx4ROON74fDLvdbvockPCP+ecLWwwFlaaGVRpku0R5gCSglFdqIgRXz7PHX+4/H83n88Hn+4u+J97NrTEErNKA7RPlOSfY2CwpRDgeVW6K0vl1LrwkNxPKczcNYLPiH3urvm1PozQ0QA1pmMiPm8kkB1dBjk4bArE0yIT0CCc2EJzt8Sp8YrVG1mHhlgbZnpF+0MAkNqvgyU4aWUeofQPU0H7hhm3Q1DOKJyOxiqgsQBMhJ7lUSINil5cNPtqZD66abmKIGlbgw7l1qFppcNX8TVDsJDcT1kP9kBaK6ygKrno7qXo4Ym2hDRJloRay0EsDhg1rJsqWBTbnaf8GktxMWMeIdO8QokwkuVQGfsW1IY/7N5HkZkLzKKyV4ljC7H9Lwgt7gZFavrYMpWsUG15uinTzEI7MUsO0DBOnoq5MJblUiPPQf1UmVMtYaZCNEDHHwnqeBVjmktxshIiGgXUbDFRoS2NKsCEebkMSN5OlARVmroB1ZyRQ+L+8IQuzDmIXYTzErS4uo9VBLNzJm212uRmI8ckN9yffm5OBGE52ca/NsZ9qWnrryKyj4oa8aTNCaSyjjoprFQ0JpanMOSryHIT2tGIcGXNU7NGZOh81ZcxRkY+TVaVLjwmJzDgq9sw9NbblujKy+gPbJrhyEHnLtWWgG4I+A3ExATWPBgndUfGb16xOaM4lZvTrfvjZFasTmvTbpAFusxd/aIeNSniZMB3VgCOh/qgaphAd1cS0bfKcgBTgdS8NHF0zJ7dYWI5qIiXF/nlSTCE5qomFQUETMzcqFEc1U26zzK0hZakghDXjZmIdm9yaUpYKQnBUI8c1aWoKkkp6CtWiMmMNbI1x01IQKqCjGpp7kH+z2oBA3UtTDVg2ezRhmZtSEEc1NfVwzaNGdMaVqu+oxmpt1m5oqpdaAEc1NibWGV/uUpBy1XRUc3GOKxQaGksTjcrwFGJDnHj+D8rEDr9bUm8yAAAAAElFTkSuQmCC',
            'alt_logo_url': 'alt_logo_url',
            'color': '#0088cc',
            'second_color': '#f3ba2f',
            'alt_color': '#f3ba2f',
            'second_alt_color': '#f3ba2f',
        },
    ]
    cashboxes = [
        {
            'name': 'Tinkoff Black',
            'type_id': 1,  # Дебетовый счёт
            'provider_id': 1,
            'currency': 'RUB',
            'description': 'Дебетовая карта Black c кэш-беком рублями на всё',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Tinkoff Black Premium',
            'type_id': 1,  # Дебетовый счёт
            'provider_id': 1,
            'currency': 'RUB',
            'description': 'Расширенная страховка в поездках, доступ в бизнес-залы по всему миру, кэшбэк до 60 000 ₽ и другие привилегии',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Tinkoff «Джуниор»',
            'type_id': 1,  # Дебетовый счёт
            'provider_id': 1,
            'currency': 'RUB',
            'description': 'Самая выгодная карта для детей до 14 лет. Учит финграмотности и приносит бонусы за покупки',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Tinkoff Platinum',
            'type_id': 2,  # Кредитный счёт
            'provider_id': 1,
            'currency': 'RUB',
            'description': 'Кредитная карта с бесплатным обслуживанием и льготным периодом до 55 дней',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Tinkoff Platinum Premium',
            'type_id': 2,  # Кредитный счёт
            'provider_id': 1,
            'currency': 'RUB',
            'description': 'Премиальная кредитная карта с кэшбэком рублями',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Tinkoff Инвестиции',
            'type_id': 3,  # Инвест. счёт
            'provider_id': 1,
            'currency': 'RUB',
            'description': 'Брокерский счёт от Тинькофф для торговли акциями и ETF',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'Альфа-Карта',
            'type_id': 1,
            'provider_id': 3,
            'currency': 'RUB',
            'description': 'Дебетовая карта с начислением процентов на остаток',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Альфа-Кредит',
            'type_id': 2,
            'provider_id': 3,
            'currency': 'RUB',
            'description': 'Кредитка с кэшбэком и льготным периодом',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Альфа-Инвестиции',
            'type_id': 3,
            'provider_id': 3,
            'currency': 'RUB',
            'description': 'Инвестсчет для покупки акций и облигаций',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'СберКарта',
            'type_id': 1,
            'provider_id': 4,
            'currency': 'RUB',
            'description': 'Классическая дебетовая карта с бонусами "Спасибо"',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Карта Фикс',
            'type_id': 2,
            'provider_id': 4,
            'currency': 'RUB',
            'description': 'Бесплатная карта для любых трат, без процентов и комиссий. Возвращайте деньги, когда вам удобно',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'СберИнвестиции',
            'type_id': 3,
            'provider_id': 4,
            'currency': 'RUB',
            'description': 'Инвестиционный счёт с возможностью покупки акций',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'Наличные RUB',
            'type_id': 4,
            'provider_id': 6,
            'currency': 'RUB',
            'description': 'Физические наличные, хранящиеся дома или с собой',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Наличные USD',
            'type_id': 4,
            'provider_id': 6,
            'currency': 'USD',
            'description': 'Физические наличные, хранящиеся дома или с собой',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Наличные EUR',
            'type_id': 4,
            'provider_id': 6,
            'currency': 'EUR',
            'description': 'Физические наличные, хранящиеся дома или с собой',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'Дебетовая карта ВТБ для жизни',
            'type_id': 1,  # Дебетовый счёт
            'provider_id': 2,
            'currency': 'RUB',
            'description': 'Бесплатная карта с кешбэком рублями для счастливых моментов',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Дебетовая карта ВТБ к 90-летию Московского метрополитена',
            'type_id': 1,  # Дебетовый счёт
            'provider_id': 2,
            'currency': 'RUB',
            'description': 'Вдохновленная архитектурой и историей столичного метрополитена',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Киберкарта ВТБ',
            'type_id': 1,  # Дебетовый счёт
            'provider_id': 2,
            'currency': 'RUB',
            'description': 'Все лучшее для геймеров – в одной карте',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Кредитная «Карта возможностей» ВТБ',
            'type_id': 2,
            'provider_id': 2,
            'currency': 'RUB',
            'description': 'Карта с беспроцентным периодом до 200 дней и повышенным кешбэком',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'Цифровая Кэшбэк-карта Райффайзен',
            'type_id': 1,
            'provider_id': 5,
            'currency': 'RUB',
            'description': 'Карта с беспроцентным периодом до 200 дней и повышенным кешбэком',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'Умная дебетовая карта «Мир» от Газпромбанк',
            'type_id': 1,
            'provider_id': 7,
            'currency': 'RUB',
            'description': 'Кэшбэк до 5 000 баллов каждый месяц в топовых категориях. Переводы и снятие без комиссии.',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Премиальная карта Mir Supreme от Газпромбанк',
            'type_id': 1,
            'provider_id': 7,
            'currency': 'RUB',
            'description': 'Оформите карту с привилегиями для спорта и путешествий.',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Простая кредитная карта от Газпромбанк',
            'type_id': 2,
            'provider_id': 7,
            'currency': 'RUB',
            'description': 'Бесплатное обслуживание первый год.',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'Карта «Халва»',
            'type_id': 1,
            'provider_id': 8,
            'currency': 'RUB',
            'description': 'Вернётся до 10% стоимости покупки.',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Дебетовая карта с кэшбэком от Совкомбанк',
            'type_id': 1,
            'provider_id': 8,
            'currency': 'RUB',
            'description': 'Получите дебетовую карту с повышенным кэшбэком — до 30% рублями!',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Кредитная карта 180 дней',
            'type_id': 2,
            'provider_id': 8,
            'currency': 'RUB',
            'description': 'Бесплатная карта с длительным льготным периодом на покупки и снятием наличных без комиссии.',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'Ozon Карта',
            'type_id': 1,
            'provider_id': 9,
            'currency': 'RUB',
            'description': 'Кешбэк до 25% в рублях на покупки вне Ozon.',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Кредитная карта Ozon',
            'type_id': 2,
            'provider_id': 9,
            'currency': 'RUB',
            'description': 'До 78 дней льготного периода.',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'PayPal',
            'type_id': 6,
            'provider_id': 10,
            'currency': 'USD',
            'description': 'Международный кошелёк для онлайн-платежей и покупок',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'ЮMoney',
            'type_id': 6,
            'provider_id': 11,
            'currency': 'RUB',
            'description': 'Электронный кошелёк для онлайн-платежей и переводов',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'Binance BTC',
            'type_id': 5,  # Крипто-кошелёк
            'provider_id': 12,
            'currency': 'BTC',
            'description': 'Bitcoin-кошелёк на бирже Binance',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Binance TON',
            'type_id': 5,
            'provider_id': 12,
            'currency': 'TON',
            'description': 'TON-кошелёк в рамках Binance',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Binance USDT',
            'type_id': 5,
            'provider_id': 12,
            'currency': 'USDT',
            'description': 'Tether на кошельке Binance',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Binance ETH',
            'type_id': 5,
            'provider_id': 12,
            'currency': 'ETH',
            'description': 'Ethereum  на кошельке Binance',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Binance SOL',
            'type_id': 5,
            'provider_id': 12,
            'currency': 'SOL',
            'description': 'Solana на кошельке Binance',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Binance DOGE',
            'type_id': 5,
            'provider_id': 12,
            'currency': 'DOGE',
            'description': 'Dogecoin на кошельке Binance',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'Bybit BTC',
            'type_id': 5,  # Крипто-кошелёк
            'provider_id': 13,
            'currency': 'BTC',
            'description': 'Bitcoin-кошелёк на бирже Bybit',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Bybit TON',
            'type_id': 5,
            'provider_id': 13,
            'currency': 'TON',
            'description': 'TON-кошелёк в рамках Bybit',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Bybit USDT',
            'type_id': 5,
            'provider_id': 13,
            'currency': 'USDT',
            'description': 'Tether на кошельке Bybit',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Bybit ETH',
            'type_id': 5,
            'provider_id': 13,
            'currency': 'ETH',
            'description': 'Ethereum  на кошельке Bybit',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Bybit SOL',
            'type_id': 5,
            'provider_id': 13,
            'currency': 'SOL',
            'description': 'Solana на кошельке Bybit',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Bybit DOGE',
            'type_id': 5,
            'provider_id': 13,
            'currency': 'DOGE',
            'description': 'Dogecoin на кошельке Bybit',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'TON в Telegram',
            'type_id': 5,
            'provider_id': 14,
            'currency': 'TON',
            'description': 'Кошелёк @wallet в Telegram',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'USDT в Telegram',
            'type_id': 5,
            'provider_id': 14,
            'currency': 'USDT',
            'description': 'P2P-кошелёк Telegram через @wallet',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'Валютный счёт в долларах',
            'type_id': 7,
            'provider_id': 3,  # Альфа-Банк
            'currency': 'USD',
            'description': 'Счёт в долларах США для хранения и расчётов',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Валютный счёт в евро',
            'type_id': 7,
            'provider_id': 4,  # СберБанк
            'currency': 'EUR',
            'description': 'Счёт в евро для хранения и международных операций',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'Tinkoff Premium Multi',
            'type_id': 8,
            'provider_id': 1,
            'currency': 'MULTI',
            'description': 'Мультивалютный счёт с автоматической конверсией',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Сбер Мультивалютный',
            'type_id': 8,
            'provider_id': 4,
            'currency': 'MULTI',
            'description': 'Один счёт — много валют. Поддержка RUB, USD, EUR',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'СберСпасибо',
            'type_id': 9,
            'provider_id': 4,
            'currency': 'SBRS',
            'description': 'Бонусная программа от Сбербанка',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'Ozon Gift Card',
            'type_id': 10,
            'provider_id': 9,
            'currency': 'RUB',
            'description': 'Подарочная карта для покупок на Ozon',
            'icon': 'url',
            'is_active': True,
        },

        {
            'name': 'Копилка Сбербанк',
            'type_id': 11,
            'provider_id': 4,
            'currency': 'RUB',
            'description': 'Автоматическое накопление с карты на сберегательный счёт',
            'icon': 'url',
            'is_active': True,
        },
        {
            'name': 'Счёт накоплений Tinkoff',
            'type_id': 11,
            'provider_id': 1,
            'currency': 'RUB',
            'description': 'Счёт с повышенным процентом на остаток',
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
        'email': 'egorka.mironov.12@gmail.com',
        'first_name': 'Егор',
        'last_name': 'Миронов',
        'patronymic': 'Петрович',
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
            'balance': 43602.55,
            'is_auto_update': False,
            'last_synced_at': '2025-04-14 13:57:54.053179',
            'custom_name': 'Основная платежная карта',
            'note': 'Повышенный кэш-бек на все категории трат',
        },
        {
            'user_id': 1,
            'cashbox_id': 6,
            'balance': 300.97,
            'is_auto_update': False,
            'last_synced_at': '2025-04-14 13:57:54.053179',
            'custom_name': 'Брокерский счет в Т-Банке',
            'note': 'Необходимо продать Cara Therapeutics',
        },
        {
            'user_id': 1,
            'cashbox_id': 10,
            'balance': 38570.32,
            'is_auto_update': False,
            'last_synced_at': '2025-04-14 13:57:54.053179',
            'custom_name': 'Зарплатная карта',
            'note': 'ToDo: закрыть счет по истечению срока действия',
        },
        {
            'user_id': 1,
            'cashbox_id': 49,
            'balance': 390,
            'is_auto_update': False,
            'last_synced_at': '2025-04-14 13:57:54.053179',
            'custom_name': 'Бонусы от Сбера',
            'note': 'Индифферентно',
        },
        {
            'user_id': 1,
            'cashbox_id': 13,
            'balance': 2705.0,
            'is_auto_update': False,
            'last_synced_at': '2025-04-14 13:57:54.053179',
            'custom_name': 'Наличные',
            'note': 'Сумма в картхолдере',
        },
        {
            'user_id': 1,
            'cashbox_id': 15,
            'balance': 5.0,
            'is_auto_update': False,
            'last_synced_at': '2025-04-14 13:57:54.053179',
            'custom_name': 'Наличные',
            'note': 'Сумма в картхолдере',
        },
        {
            'user_id': 1,
            'cashbox_id': 16,
            'balance': 1200.0,
            'is_auto_update': False,
            'last_synced_at': '2025-04-14 13:57:54.053179',
            'custom_name': 'Университетская карта',
            'note': 'Стипендия и только',
        },
        {
            'user_id': 1,
            'cashbox_id': 31,
            'balance': 0.0,
            'is_auto_update': False,
            'last_synced_at': '2025-04-14 13:57:54.053179',
            'custom_name': 'Основной крипто-кошелек',
            'note': 'Вложения в цифры',
        },
        {
            'user_id': 1,
            'cashbox_id': 43,
            'balance': 0.0,
            'is_auto_update': False,
            'last_synced_at': '2025-04-14 13:57:54.053179',
            'custom_name': 'Криптовалюта в TG',
            'note': 'Потестить нововведения от Павла Дурова',
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
            'user_cashbox_id': 1,
            'category_id': 20,
            'subcategory_id': 134,
            'amount': 2000,
            'comment': 'Перевод от Папы',
            'transacted_at': '2025-05-04 12:00:00.053179',
            'source': 'Миронов П.Н.',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 20,
            'subcategory_id': 135,
            'amount': 1210,
            'comment': 'Перевод от Рамиса',
            'transacted_at': '2025-05-05 12:00:00.053179',
            'source': 'Хасаншин Р.Р.',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 20,
            'subcategory_id': 134,
            'amount': 5000,
            'comment': 'Перевод от Папы',
            'transacted_at': '2025-05-12 12:00:00.053179',
            'source': 'Миронов П.Н.',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 20,
            'subcategory_id': 134,
            'amount': 3500,
            'comment': 'Перевод от Папы',
            'transacted_at': '2025-05-18 12:00:00.053179',
            'source': 'Миронов П.Н.',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 20,
            'subcategory_id': 135,
            'amount': 400,
            'comment': 'Перевод от Давыта',
            'transacted_at': '2025-05-21 12:00:00.053179',
            'source': 'Гаффаров Д.М.',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 18,
            'subcategory_id': 124,
            'amount': 112,
            'comment': 'Ежемесячный кэш-бек за обычные покупки',
            'transacted_at': '2025-05-22 12:00:00.053179',
            'source': 'Tinkoff Black',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 20,
            'subcategory_id': 133,
            'amount': 15000,
            'comment': 'Возврат долга + подарок от Мамы',
            'transacted_at': '2025-06-09 12:00:00.053179',
            'source': 'Миронова А.А.',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 20,
            'subcategory_id': 133,
            'amount': 10000,
            'comment': 'Подарок от Папы',
            'transacted_at': '2025-06-12 12:00:00.053179',
            'source': 'Миронов П.Н.',
        },
        {
            'user_cashbox_id': 3,
            'category_id': 16,
            'subcategory_id': 109,
            'amount': 3000,
            'comment': 'Деньги с подработки',
            'transacted_at': '2025-05-05 12:00:00.053179',
            'source': 'ИП "Devmark"',
        },
        {
            'user_cashbox_id': 3,
            'category_id': 20,
            'subcategory_id': 133,
            'amount': 3000,
            'comment': 'Подарок от тети Любы',
            'transacted_at': '2025-06-12 12:00:00.053179',
            'source': 'Родионова Л.Н.',
        },
    ]
    expense = [
        {
            'user_cashbox_id': 3,
            'category_id': 5,
            'subcategory_id': 31,
            'amount': 2020,
            'comment': 'Оплата услуг общежития',
            'transacted_at': '2025-05-04 13:57:54.053179',
            'vendor': 'КФУ Приволжский',
            'location': 'Деревня Универсиады, д.3',
        },
        {
            'user_cashbox_id': 3,
            'category_id': 5,
            'subcategory_id': 31,
            'amount': 4000,
            'comment': 'Оплата услуг общежития',
            'transacted_at': '2025-06-15 13:57:54.053179',
            'vendor': 'КФУ Приволжский',
            'location': 'Деревня Универсиады, д.3',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 96,
            'amount': 399,
            'comment': 'Подписка Яндекс Плюс',
            'transacted_at': '2025-05-01 13:57:54.053179',
            'vendor': 'Yandex Plus',
            'location': 'Москва',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 20,
            'amount': 240,
            'comment': 'Такси до ресторана',
            'transacted_at': '2025-05-02 13:57:54.053179',
            'vendor': 'Яндекс Такси',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 20,
            'amount': 317,
            'comment': 'Такси до дома',
            'transacted_at': '2025-05-03 13:57:54.053179',
            'vendor': 'Яндекс Такси',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 20,
            'amount': 278,
            'comment': 'Такси до парикмахерской',
            'transacted_at': '2025-05-04 13:57:54.053179',
            'vendor': 'Яндекс Такси',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 20,
            'amount': 356,
            'comment': 'Такси до дома',
            'transacted_at': '2025-05-04 13:57:54.053179',
            'vendor': 'Яндекс Такси',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 96,
            'amount': 190,
            'comment': 'Сервисный сбор BlaBlaCar',
            'transacted_at': '2025-05-04 13:57:54.053179',
            'vendor': 'BlaBlaCar',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 5,
            'subcategory_id': 34,
            'amount': 200,
            'comment': 'Интернет в общежитии',
            'transacted_at': '2025-05-04 13:57:54.053179',
            'vendor': 'Таттелеком (Летай)',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 94,
            'amount': 650,
            'comment': 'Перевод за поездку на BlaBlaCar',
            'transacted_at': '2025-05-05 13:57:54.053179',
            'vendor': 'Алёна Г.',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 21,
            'amount': 43,
            'comment': 'Проезд до Метро',
            'transacted_at': '2025-05-05 13:57:54.053179',
            'vendor': 'Транспортная Карта',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 17,
            'amount': 43,
            'comment': 'Проезд до центра',
            'transacted_at': '2025-05-05 13:57:54.053179',
            'vendor': 'МУП Метроэлектротранс',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 11,
            'subcategory_id': 78,
            'amount': 298,
            'comment': 'Печать второй практики',
            'transacted_at': '2025-05-05 13:57:54.053179',
            'vendor': 'Копицентр',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 2,
            'subcategory_id': 12,
            'amount': 2045,
            'comment': 'Обед в BeanHearts',
            'transacted_at': '2025-05-05 13:57:54.053179',
            'vendor': 'Яндекс Еда',
            'location': 'Казань, ул.Пушкина, 13',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 18,
            'amount': 43,
            'comment': 'Проезд до Мамадышского тракта',
            'transacted_at': '2025-05-05 13:57:54.053179',
            'vendor': 'Транспортная Карта',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 94,
            'amount': 600,
            'comment': 'Перевод за поездку на BlaBlaCar',
            'transacted_at': '2025-05-05 13:57:54.053179',
            'vendor': 'Алёна Г.',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 6,
            'subcategory_id': 45,
            'amount': 298,
            'comment': 'Покупка 20-ти шариков',
            'transacted_at': '2025-05-05 13:57:54.053179',
            'vendor': 'Циркуль',
            'location': 'Набережные Челны, ул.Раскольникова, 17',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 1,
            'subcategory_id': 6,
            'amount': 183.98,
            'comment': 'Покупка продуктов питания',
            'transacted_at': '2025-05-05 13:57:54.053179',
            'vendor': 'Пятёрочка',
            'location': 'Набережные Челны, ул.Раскольникова, 17',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 96,
            'amount': 210,
            'comment': 'Сервисный сбор BlaBlaCar',
            'transacted_at': '2025-05-11 13:57:54.053179',
            'vendor': 'BlaBlaCar',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 94,
            'amount': 700,
            'comment': 'Перевод за поездку на BlaBlaCar',
            'transacted_at': '2025-05-12 13:57:54.053179',
            'vendor': 'Денис Д.',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 11,
            'subcategory_id': 78,
            'amount': 308,
            'comment': 'Печать пред-диплома',
            'transacted_at': '2025-05-12 13:57:54.053179',
            'vendor': 'Копицентр',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 96,
            'amount': 210,
            'comment': 'Сервисный сбор BlaBlaCar',
            'transacted_at': '2025-05-12 13:57:54.053179',
            'vendor': 'BlaBlaCar',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 17,
            'amount': 43,
            'comment': 'Проезд до проспекта победы',
            'transacted_at': '2025-05-12 13:57:54.053179',
            'vendor': 'МУП Метроэлектротранс',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 21,
            'amount': 43,
            'comment': 'Проезд до Мамадышского тракта',
            'transacted_at': '2025-05-12 13:57:54.053179',
            'vendor': 'Транспортная Карта',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 94,
            'amount': 600,
            'comment': 'Перевод за поездку на BlaBlaCar',
            'transacted_at': '2025-05-12 13:57:54.053179',
            'vendor': 'Рафаэль К.',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 20,
            'amount': 276,
            'comment': 'Такси до дома',
            'transacted_at': '2025-05-12 13:57:54.053179',
            'vendor': 'Яндекс Такси',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 2,
            'subcategory_id': 13,
            'amount': 3100,
            'comment': 'Доставка домашних мантов',
            'transacted_at': '2025-05-17 13:57:54.053179',
            'vendor': 'Дмитрий Е.',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 20,
            'amount': 386,
            'comment': 'Такси для Мамы',
            'transacted_at': '2025-05-18 13:57:54.053179',
            'vendor': 'Яндекс Такси',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 20,
            'amount': 402,
            'comment': 'Такси для Мамы',
            'transacted_at': '2025-05-19 13:57:54.053179',
            'vendor': 'Яндекс Такси',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 2,
            'subcategory_id': 13,
            'amount': 737.23,
            'comment': 'Покупка продуктов',
            'transacted_at': '2025-05-19 13:57:54.053179',
            'vendor': 'Пятёрочка',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 5,
            'subcategory_id': 34,
            'amount': 200,
            'comment': 'Интернет в общежитии',
            'transacted_at': '2025-05-21 13:57:54.053179',
            'vendor': 'Таттелеком (Летай)',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 96,
            'amount': 190,
            'comment': 'Сервисный сбор BlaBlaCar',
            'transacted_at': '2025-05-25 13:57:54.053179',
            'vendor': 'BlaBlaCar',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 94,
            'amount': 650,
            'comment': 'Перевод за поездку на BlaBlaCar',
            'transacted_at': '2025-05-26 13:57:54.053179',
            'vendor': 'Вероника Р.',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 21,
            'amount': 43,
            'comment': 'Проезд до Метро',
            'transacted_at': '2025-05-26 13:57:54.053179',
            'vendor': 'Транспортная Карта',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 17,
            'amount': 43,
            'comment': 'Проезд до центра',
            'transacted_at': '2025-05-26 13:57:54.053179',
            'vendor': 'МУП Метроэлектротранс',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 11,
            'subcategory_id': 78,
            'amount': 406,
            'comment': 'Печать третьей практики',
            'transacted_at': '2025-05-26 13:57:54.053179',
            'vendor': 'ПринтЦентр',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 1,
            'subcategory_id': 9,
            'amount': 41.99,
            'comment': 'Негазированная вода 0,5',
            'transacted_at': '2025-05-26 13:57:54.053179',
            'vendor': 'Магнит',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 2,
            'subcategory_id': 14,
            'amount': 334,
            'comment': 'Обед в Токмач',
            'transacted_at': '2025-05-26 13:57:54.053179',
            'vendor': 'Токмач',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 1,
            'subcategory_id': 9,
            'amount': 41.99,
            'comment': 'Негазированная вода 0,5',
            'transacted_at': '2025-05-26 13:57:54.053179',
            'vendor': 'Магнит',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 17,
            'amount': 43,
            'comment': 'Проезд до Меги',
            'transacted_at': '2025-05-26 13:57:54.053179',
            'vendor': 'МУП Метроэлектротранс',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 94,
            'amount': 700,
            'comment': 'Перевод за поездку на BlaBlaCar',
            'transacted_at': '2025-05-26 13:57:54.053179',
            'vendor': 'Денис Г.',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 96,
            'amount': 328,
            'comment': 'Подписка Яндекс Плюс',
            'transacted_at': '2025-05-31 13:57:54.053179',
            'vendor': 'Yandex Plus',
            'location': 'Москва',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 2,
            'subcategory_id': 13,
            'amount': 1308.48,
            'comment': 'Доставка продуктов питания',
            'transacted_at': '2025-06-04 13:57:54.053179',
            'vendor': 'Пятёрочка',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 2,
            'subcategory_id': 13,
            'amount': 363.46,
            'comment': 'Доставка продуктов питания',
            'transacted_at': '2025-06-07 13:57:54.053179',
            'vendor': 'Пятёрочка',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 2,
            'subcategory_id': 14,
            'amount': 359,
            'comment': 'Свежая выпечка',
            'transacted_at': '2025-06-07 13:57:54.053179',
            'vendor': 'Пекарня',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 99,
            'amount': 7000,
            'comment': 'На Wildberries',
            'transacted_at': '2025-06-09 13:57:54.053179',
            'vendor': 'Миронова А.А.',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 20,
            'amount': 289,
            'comment': 'Такси до дома',
            'transacted_at': '2025-06-11 13:57:54.053179',
            'vendor': 'Яндекс Такси',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 96,
            'amount': 50,
            'comment': 'Сервисный сбор BlaBlaCar',
            'transacted_at': '2025-06-12 13:57:54.053179',
            'vendor': 'BlaBlaCar',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 94,
            'amount': 700,
            'comment': 'Перевод за поездку на BlaBlaCar',
            'transacted_at': '2025-06-13 13:57:54.053179',
            'vendor': 'Ильнур И.',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 20,
            'amount': 566,
            'comment': 'Такси до центра',
            'transacted_at': '2025-06-13 13:57:54.053179',
            'vendor': 'Яндекс Такси',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 11,
            'subcategory_id': 78,
            'amount': 1243,
            'comment': 'Печать ВКР',
            'transacted_at': '2025-06-13 13:57:54.053179',
            'vendor': 'Копицентр',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 96,
            'amount': 190,
            'comment': 'Сервисный сбор BlaBlaCar',
            'transacted_at': '2025-06-13 13:57:54.053179',
            'vendor': 'BlaBlaCar',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 1,
            'subcategory_id': 9,
            'amount': 38.99,
            'comment': 'Негазированная вода 0,5',
            'transacted_at': '2025-06-13 13:57:54.053179',
            'vendor': 'Магнит',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 17,
            'amount': 43,
            'comment': 'Проезд до проспекта победы',
            'transacted_at': '2025-06-13 13:57:54.053179',
            'vendor': 'МУП Метроэлектротранс',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 3,
            'subcategory_id': 20,
            'amount': 196,
            'comment': 'Такси до Меги',
            'transacted_at': '2025-06-13 13:57:54.053179',
            'vendor': 'Яндекс Такси',
            'location': 'Казань',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 14,
            'subcategory_id': 94,
            'amount': 650,
            'comment': 'Перевод за поездку на BlaBlaCar',
            'transacted_at': '2025-06-13 13:57:54.053179',
            'vendor': 'Кирилл В.',
            'location': 'Набережные Челны',
        },
        {
            'user_cashbox_id': 1,
            'category_id': 2,
            'subcategory_id': 14,
            'amount': 120,
            'comment': 'Свежая выпечка',
            'transacted_at': '2025-06-13 13:57:54.053179',
            'vendor': 'Пекарня',
            'location': 'Набережные Челны',
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
