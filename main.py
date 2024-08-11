import os, jsonify , requests
from flask import Flask, request, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///order.db')

db = SQLAlchemy(app)


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
    
    cart_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

with app.app_context():
    db.create_all()




@app.route("/")
def home():
    return send_file('src/index.html')

# Your existing models (Product, Combo, ComboProducts, Cart)

@app.route("/addtocart/<int:pid>", methods=['POST'])
def addtocart(pid):
    product = Product.query.get(pid)
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    if product.stock_quantity <= 0:
        return jsonify({"error": "Product out of stock"}), 400

    quantity = requests.form.get('quantity', 1, type=int)
    if quantity <= 0:
        return jsonify({"error": "Invalid quantity"}), 400

    cart_item = Cart(product_id=pid, item_type='product', quantity=quantity)
    db.session.add(cart_item)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Failed to add to cart"}), 500

    return jsonify({"message": "Added to cart"}), 200


@app.route("/removefromcart/<int:cart_id>", methods=['DELETE'])
def removefromcart(cart_id):
    cart_item = Cart.query.get(cart_id)
    if cart_item is None:
        return jsonify({"error": "Cart item not found"}), 404

    db.session.delete(cart_item)
    db.session.commit()

    return jsonify({"message": "Item removed from cart"}), 200


@app.route("/updatecartquantity/<int:cart_id>", methods=['PUT'])
def updatecartquantity(cart_id):
    cart_item = Cart.query.get(cart_id)
    if cart_item is None:
        return jsonify({"error": "Cart item not found"}), 404

    quantity = requests.form.get('quantity', type=int)
    if quantity is None or quantity <= 0:
        return jsonify({"error": "Invalid quantity"}), 400

    if cart_item.item_type == 'product':
        product = Product.query.get(cart_item.product_id)
        if product.stock_quantity < quantity:
            return jsonify({"error": "Insufficient stock"}), 400

    cart_item.quantity = quantity
    db.session.commit()

    return jsonify({"message": "Cart quantity updated"}), 200






@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    product_name = data.get('product_name')
    product_description = data.get('product_description')
    price = data.get('price')
    product_type = data.get('type')
    stock_quantity = data.get('stock_quantity')

    if not product_name or not price or not product_type or not stock_quantity:
        return jsonify({'error': 'Missing required fields'}), 400

        return jsonify({'error': 'Invalid product type'}), 400
    
    product = Product(product_name = product_name,product_description= product_description,price = price, type = product_type,stock_quantity= stock_quantity)


    db.session.add(product)
    db.session.commit()

    return jsonify({'message': 'Product added successfully', 'product_id': product.product_id}), 201


@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': 'Product deleted successfully'}), 200


@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.get_json()
    product_name = data.get('product_name')
    product_description = data.get('product_description')
    price = data.get('price')
    product_type = data.get('type')
    stock_quantity = data.get('stock_quantity')

    if product_type and product_type not in ['veg', 'non-veg']:
        return jsonify({'error': 'Invalid product type'}), 400

    if product_name:
        product.product_name = product_name
    if product_description:
        product.product_description = product_description
    if price:
        product.price = price
    if product_type:
        product.type = product_type
    if stock_quantity:
        product.stock_quantity = stock_quantity

    db.session.commit()

    return jsonify({'message': 'Product updated successfully'}), 200




@app.route('/checkout', methods=['GET'])
def checkout():
    # Get all items in the cart
    cart_items = Cart.query.all()

    # Calculate the total cost
    total_cost = 0
    for item in cart_items:
        if item.item_type == 'product':
            product = Product.query.get(item.product_id)
            total_cost += product.price * item.quantity
        else:
            combo = Combo.query.get(item.combo_id)
            total_cost += combo.final_discounted_price * item.quantity

    # Check if any product is out of stock
    out_of_stock_products = []
    for item in cart_items:
        if item.item_type == 'product':
            product = Product.query.get(item.product_id)
            if product.stock_quantity < item.quantity:
                out_of_stock_products.append(product.product_name)

    if out_of_stock_products:
        return jsonify({
            'error': 'Some products are out of stock',
            'out_of_stock_products': out_of_stock_products
        }), 400

    # Update stock quantities
    for item in cart_items:
        if item.item_type == 'product':
            product = Product.query.get(item.product_id)
            product.stock_quantity -= item.quantity

    # Clear the cart
    for item in cart_items:
        db.session.delete(item)

    db.session.commit()

    return jsonify({
        'message': 'Checkout successful',
        'total_cost': total_cost
    }), 200


    
def main():
    app.run(port=int(os.environ.get('PORT', 80)))

if __name__ == "__main__":
    main()

