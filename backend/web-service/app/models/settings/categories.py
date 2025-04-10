"""
Модели для категорий
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, HistoryModel


class Category(BaseModel):
    """
    Модель категорий
    """
    __tablename__ = "category"

    name = Column(String(99))  # Наименование категории
    code = Column(Integer())  # Код категории
    logo_url = Column(String(512))  # url-ссылка логотипа категории
    color = Column(String(7))  # Цвет категории формата hex #xxxxxx

    # Связи
    subcategories = relationship('Subcategory', back_populates='category')

    def __repr__(self):
        return f"<Category {self.name}>"


class CategoryHistory(HistoryModel):
    """
    Модель изменения категорий
    """
    __tablename__ = "category_history"

    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    category = relationship('Category')


class Subcategory(BaseModel):
    """
    Модель подкатегории
    """
    __tablename__ = "subcategory"

    name = Column(String(99))  # Наименование подкатегории
    code = Column(Integer())  # Код подкатегории
    logo_url = Column(String(512))  # url-ссылка логотипа подкатегории

    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    category = relationship('Category', back_populates='subcategories')

    def __repr__(self):
        return f"Subcategory: {self.name}, {self.code}"


class SubcategoryHistory(HistoryModel):
    """
    Модель изменения подкатегорий
    """
    __tablename__ = "subcategory_history"

    subcategory_id = Column(Integer, ForeignKey('subcategory.id'), nullable=False)
    subcategory = relationship('Subcategory')