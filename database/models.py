from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint

from main import app, db

class Product(db.Model):
    __tablename__ = 'Product'
    
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String, nullable=False)
    product_description = db.Column(db.String)
    price = db.Column(db.Float, nullable=False)
    type = db.Column(db.String, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("type IN ('veg', 'non-veg')", name='check_type'),
    )

    def __repr__(self):
        return f"<Product {self.product_name}>"

class Combo(db.Model):
    __tablename__ = 'Combo'
    
    combo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    combo_name = db.Column(db.String, nullable=False)
    final_discounted_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Combo {self.combo_name}>"

class ComboProducts(db.Model):
    __tablename__ = 'ComboProducts'
    
    combo_id = db.Column(db.Integer, db.ForeignKey('Combo.combo_id', ondelete='CASCADE'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('Product.product_id', ondelete='CASCADE'), primary_key=True)

    combo = db.relationship('Combo', backref=db.backref('combo_products', cascade="all, delete-orphan"))
    product = db.relationship('Product', backref=db.backref('combo_products', cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<ComboProducts combo_id={self.combo_id}, product_id={self.product_id}>"

class Cart(db.Model):
    __tablename__ = 'Cart'
    
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('Product.product_id'))
    combo_id = db.Column(db.Integer, db.ForeignKey('Combo.combo_id'))
    quantity = db.Column(db.Integer, nullable=False)
    item_type = db.Column(db.String, nullable=False)

    __table_args__ = (
        CheckConstraint("item_type IN ('product', 'combo')", name='check_item_type'),
    )

    product = db.relationship('Product', backref=db.backref('cart_items', cascade="all, delete-orphan"))
    combo = db.relationship('Combo', backref=db.backref('cart_items', cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<Cart cart_id={self.cart_id}, item_type={self.item_type}, quantity={self.quantity}>"
