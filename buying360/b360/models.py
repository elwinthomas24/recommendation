
from flask_login import UserMixin
from b360 import db
from b360 import bcrypt
from b360 import login_manager

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

cart = db.Table('cart',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id')),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'))
)

# class CartItems(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
#     product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
#     quantity = db.Column(db.Integer, nullable=False)
#     price_per_unit = db.Column(db.Float, nullable=False)
#      # Define the relationships with the user and product
#     user = db.relationship('Users', back_populates='cart_items')
#     product = db.relationship('Products', back_populates='cart_items')

#     @property
#     def total_price(self):
#         return self.quantity * self.price_per_unit

class Users(db.Model, UserMixin):
    user_id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.String(length = 30),nullable = False, unique = True)
    password_hash = db.Column(db.String(length = 60),nullable = False)
    # cart_items = db.relationship('CartItems', back_populates='users')
    user_cart = db.relationship('Products', secondary = cart, backref= db.backref('paying_customer', lazy = 'dynamic'))

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
            
    def get_id(self):
        return (self.user_id)

    def __repr__(self):
        
        return f'{self.user_id}'



class Products(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    product_name = db.Column(db.String(length = 30),nullable = False)
    product_description = db.Column(db.String(length = 30),nullable = False)
    product_img = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float(),nullable = False)
    stock_available = db.Column(db.Integer(), nullable = False)
    # cart_items = db.relationship('CartItems', back_populates='products')


    def __repr__(self):
        # return f'{self.location} {self.tournament_type}'
        return f'{self.id} {self.product_name} {self.product_description} {self.product_img} {self.price}'

    def add_to_cart_for_user(self, user):
        self.paying_customer.append(user)
        db.session.commit()      

class CartLineItem(db.Model):
    cart_id = db.Column(db.Integer(), primary_key = True)
    product_id = db.Column(db.Integer(), nullable= False)
    user_id = db.Column(db.Integer(), nullable= False)
    product_name = db.Column(db.String(length = 30),nullable = False)
    product_description = db.Column(db.String(length = 30),nullable = False)
    product_img = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float(),nullable = False)
    quantity = db.Column(db.Integer(), nullable = False)
    
    total_price = db.Column(db.Float(), nullable= False)

class SubmittedPR(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    pr_id = db.Column(db.Integer(), nullable = False)
    product_id = db.Column(db.Integer(), nullable= False)
    user_id = db.Column(db.Integer(), nullable= False)
    product_name = db.Column(db.String(length = 30),nullable = False)
    product_description = db.Column(db.String(length = 30),nullable = False)
    product_img = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float(),nullable = False)
    quantity = db.Column(db.Integer(), nullable = False)
    
    total_price = db.Column(db.Float(), nullable= False)
    total_pr_price = db.Column(db.Float(), nullable= False)



    
