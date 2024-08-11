from main import app,db
import unittest
from unittest.mock import patch
from main import Product,Cart


class TestMain(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///order.db'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Test cases for each function go here


def test_addtocart(self):
    # Create a test product
    product = Product(product_name='Test Product', price=10.0, type='veg', stock_quantity=5)
    db.session.add(product)
    db.session.commit()

    # Test adding a valid product to the cart
    data = {'quantity': 2}
    response = self.app.post(f'/addtocart/{product.product_id}', data=data)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json, {'message': 'Added to cart'})

    # Test adding an out-of-stock product to the cart
    product.stock_quantity = 0
    db.session.commit()
    response = self.app.post(f'/addtocart/{product.product_id}', data=data)
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.json, {'error': 'Product out of stock'})

    # Test adding an invalid quantity to the cart
    data = {'quantity': -1}
    response = self.app.post(f'/addtocart/{product.product_id}', data=data)
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.json, {'error': 'Invalid quantity'})
    
    



    def test_removefromcart(self):
        # Create a test product and add it to the cart
        product = Product(product_name='Test Product', price=10.0, type='veg', stock_quantity=5)
        db.session.add(product)
        db.session.commit()
        cart_item = Cart(product_id=product.product_id, item_type='product', quantity=2)
        db.session.add(cart_item)
        db.session.commit()

        # Test removing the item from the cart
        response = self.app.delete(f'/removefromcart/{cart_item.cart_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'Item removed from cart'})

        # Test removing a non-existent cart item
        response = self.app.delete('/removefromcart/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {'error': 'Cart item not found'})

    def test_updatecartquantity(self):
        # Create a test product and add it to the cart
        product = Product(product_name='Test Product', price=10.0, type='veg', stock_quantity=10)
        db.session.add(product)
        db.session.commit()
        cart_item = Cart(product_id=product.product_id, item_type='product', quantity=2)
        db.session.add(cart_item)
        db.session.commit()

        # Test increasing the quantity
        data = {'quantity': 5}
        response = self.app.put(f'/updatecartquantity/{cart_item.cart_id}', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cart.query.get(cart_item.cart_id).quantity, 5)

        # Test decreasing the quantity
        data = {'quantity': 1}
        response = self.app.put(f'/updatecartquantity/{cart_item.cart_id}', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'Cart quantity updated'})
        self.assertEqual(Cart.query.get(cart_item.cart_id).quantity, 1)

        # Test invalid quantity
        data = {'quantity': 0}
        response = self.app.put(f'/updatecartquantity/{cart_item.cart_id}', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'Invalid quantity'})

        # Test insufficient stock
        data = {'quantity': 20}
        response = self.app.put(f'/updatecartquantity/{cart_item.cart_id}', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'Insufficient stock'})

    # Add more test cases for other functions here

if __name__ == '__main__':
    unittest.main()

