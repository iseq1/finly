"""
Скрипт для заполнения базы данных начальными данными
"""
from app import create_app
from app.extensions import db
from app.models.settings.categories import Category, Subcategory


def seed_categories():
    categories_data = [
        {
            "name": "Медицина",
            "code": "89",
            "logo_url": "url",
            "subcategories": [
                {"name": "Прием терапевта", "code": "89"},
                {"name": "Еженедельный массаж", "code": "89"}
            ]
        },
        {
            "name": "Быт",
            "code": "89",
            "logo_url": "url",
            "subcategories": [
                {"name": "Дивиденды", "code": "dividends"},
                {"name": "Продажа акций", "code": "stock_sales"}
            ]
        },
        {
            "name": "Подарки",
            "code": "gifts",
            "subcategories": [
                {"name": "День рождения", "code": "birthday"},
                {"name": "Прочие", "code": "other"}
            ]
        }
    ]

    for cat in categories_data:
        category = Category(name=cat["name"], code=cat["code"])
        db.session.add(category)
        db.session.flush()  # чтобы category.id стал доступен
        for sub in cat["subcategories"]:
            subcat = Subcategory(
                name=sub["name"],
                code=sub["code"],
                category_id=category.id
            )
            db.session.add(subcat)

    db.session.commit()
    print("Категории и подкатегории успешно добавлены")

def seed_db():
    app = create_app('development')
    with app.app_context():
        seed_categories()


if __name__ == '__main__':
    seed_db()
