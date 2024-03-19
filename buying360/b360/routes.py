from b360 import app
from flask import render_template, redirect, url_for, request
from b360.models import Users, Products, CartLineItem, SubmittedPR
from b360.forms import CancelRegisterForm, RegisterForm, LoginForm, AddToCart, SubmitPRForm, SearchForm
from b360 import db
from flask_login import login_user,logout_user, login_required, current_user
from flask.helpers import flash
import random
import pandas as pd
import joblib
from surprise import SVD, Reader, Dataset
from surprise.model_selection import cross_validate


####################   Reused Functions ####################

# Function that takes in productId and useId as input and outputs up to 5 most similar products.
def hybrid_recommendations(userId, productId, matrix, svd):
    
    # Get the Id of the top five products that are correlated with the ProductId chosen by the user.
    top_five=matrix.corrwith(matrix[productId]).sort_values(ascending=False).head(5)
    
    # Predict the ratings the user might give to these top 5 most correlated products.
    est_rating=[]
    for x in list(top_five.index):
        if str(top_five[x])!='nan':
            est_rating.append(svd.predict(userId, iid=x, r_ui=None).est)
           
    return pd.DataFrame({'productId':list(top_five.index)[:len(est_rating)], 'estimated_rating':est_rating}).sort_values(by='estimated_rating', ascending=False).reset_index(drop=True)


############## add to Cart func ##################

@app.route('/')
@app.route('/home',methods= ['GET','POST'])
def home_page():
    return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = Users.query.filter_by(username =form.username.data).first()
        print(attempted_user.username)
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as:  {attempted_user.username}', category = 'success')
            return redirect(url_for('landing_page'))
        else:
            flash(f'Team Name and Password do not match! Please try again', category = 'danger')    
    return render_template('login.html', form = form)

@app.route('/logout')
def logout_page():
    logout_user()
    # flash("You have been logged out!", category ='info')
    return redirect(url_for('home_page'))

@app.route('/register', methods=['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create  = Users(username=form.username.data,
                                password=form.password1.data)
        
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account created successfully! You are now logged in as {user_to_create.username}', category = 'success')

        return redirect(url_for('landing_page'))
    if form.errors != {}:   #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating the team: {err_msg}', category = 'danger')

    return render_template('register.html', form=form)

@app.route('/query', methods = ['GET','POST'])
@login_required
def landing_page():
        form = SearchForm()
        return render_template('landingPage.html', form = form)
    #####   search bar form ####

    # popular_item1_form = PopItem1Form()
    # popular_item2_form = PopItem2Form()
    # popular_item3_form = PopItem3Form()

    ###### Add To Cart Form #######

@app.route('/process_search', methods = ['GET','POST'])
@login_required
def process_search():
    search_query = request.form['searched']
    print(search_query)
    return redirect(url_for('catalog_page', search_query = search_query))

def addToCart():
    if request.method == 'POST':
        #Add to cart logic
        add_to_cart_item = request.form.get('add_to_cart_item')
        add_to_cart_item_object = Products.query.filter_by(id=add_to_cart_item).first()
        if add_to_cart_item_object:
            line_item = CartLineItem.query.filter_by(
                product_id=add_to_cart_item_object.id,
                user_id = current_user.user_id).first()
            #### update quantity and price if it exists.
            if line_item:
                line_item.quantity = line_item.quantity + 1
                line_item.total_price = add_to_cart_item_object.price * line_item.quantity
            ### set quantity and total price for first item insertion    
            else:
                quantity = 1
                total_price = add_to_cart_item_object.price

                lineItemToInsert = CartLineItem(
                product_id = add_to_cart_item_object.id,
                user_id = current_user.user_id,
                product_name = add_to_cart_item_object.product_name,                
                product_description = add_to_cart_item_object.product_description,
                product_img= "abc",
                price = add_to_cart_item_object.price,
                quantity = quantity,
                total_price = total_price
                )
                db.session.add(lineItemToInsert)
                db.session.commit()
                        
                        
            # current_user.user_cart.contains(add)
            add_to_cart_item_object.add_to_cart_for_user(current_user)

                    
            flash(f"Item added to cart.", category='success')    
    return

@app.route('/catalog', methods = ['GET','POST'])
@login_required
def catalog_page():
    
    search_query = str(request.args.get('search_query'))
    searched_products = Products.query.filter(Products.product_description.like('%' + search_query + '%')).all()

    add_to_cart_form = AddToCart()
    lineItemToInsert = CartLineItem()
    if add_to_cart_form.validate_on_submit():
        addToCart()
        # if request.method == 'POST':
        #     #Add to cart logic
        #     add_to_cart_item = request.form.get('add_to_cart_item')
        #     add_to_cart_item_object = Products.query.filter_by(id=add_to_cart_item).first()
        #     if add_to_cart_item_object:
        #         line_item = CartLineItem.query.filter_by(
        #             product_id=add_to_cart_item_object.id,
        #             user_id = current_user.user_id).first()
        #         #### update quantity and price if it exists.
        #         if line_item:
        #             line_item.quantity = line_item.quantity + 1
        #             line_item.total_price = add_to_cart_item_object.price * line_item.quantity
        #         ### set quantity and total price for first item insertion    
        #         else:
        #             quantity = 1
        #             total_price = add_to_cart_item_object.price

        #             lineItemToInsert = CartLineItem(
        #             product_id = add_to_cart_item_object.id,
        #             user_id = current_user.user_id,
        #             product_name = add_to_cart_item_object.product_name,                
        #             product_description = add_to_cart_item_object.product_description,
        #             product_img= "abc",
        #             price = add_to_cart_item_object.price,
        #             quantity = quantity,
        #             total_price = total_price
        #             )
        #             db.session.add(lineItemToInsert)
        #             db.session.commit()
                        
                        
        #         # current_user.user_cart.contains(add)
        #         add_to_cart_item_object.add_to_cart_for_user(current_user)

                    
        #         flash(f"Item added to cart.", category='success')        
        
    return render_template('catalog.html', add_to_cart_form = add_to_cart_form, searched_products = searched_products, search_query = search_query)



@app.route('/cart', methods = ['GET','POST'])
@login_required
def cart_page():
    line_items = CartLineItem.query.filter_by(user_id = current_user.user_id).all()
    submit_request_form = SubmitPRForm()
    add_to_cart_form = AddToCart()
    ###recommendations logic
    recommendations_list = []       ##### this list will contain the product ids of recommended products based on current cart
    recommended_products_from_list = []

    for line_item in line_items:
        ###recommendations
        column_names=['id', 'brand', 'name', 'reviews.rating', 'reviews.username']
        df=pd.read_csv('/Users/I527231/Documents/Dissertation/buying360/b360/data/Reviews.csv',names=column_names)
        matrix=pd.pivot_table(data=df, values='reviews.rating', index='reviews.username',columns='id')
        svd = joblib.load('/Users/I527231/Documents/Dissertation/buying360/b360/ml_models/svd_model.pkl')
        df = hybrid_recommendations(current_user.username, line_item.product_id, matrix, svd)
        recommendations_list.append(df['productId'].tolist())
        print("recommendations list:")
        print(recommendations_list)

    #####get each product from product id in recommendations
    for sublist in recommendations_list:
        for product_id in sublist:
            recommended_products_from_list.append(Products.query.filter_by(id=product_id).first())



    ###add to cart of recommended products
    
                  

    if submit_request_form.validate_on_submit():
        generated_pr_id = random.randint(1000, 9999)
        total_pr_price = 0
        for line_item in line_items:
            total_pr_price = total_pr_price + line_item.total_price
        for line_item in line_items:
            pr_item = SubmittedPR(
                pr_id = generated_pr_id,
                product_id = line_item.product_id,
                user_id = line_item.user_id,
                product_name = line_item.product_name,
                product_description = line_item.product_description,
                product_img = line_item.product_img,
                price = line_item.price,
                quantity = line_item.quantity,
                total_price = line_item.total_price,
                total_pr_price = total_pr_price)
            print(pr_item)
            db.session.add(pr_item)
            db.session.commit()
            ##delete from cart_line_items table
            db.session.delete(line_item)
            db.session.commit()
            print("submitted")

        flash(f"Purchase Requisition Request submitted successfully.", category='success')
        return redirect(url_for('pr_page',generated_pr_id = generated_pr_id))

    return render_template('cart.html', line_items = line_items, submit_request_form = submit_request_form, recommended_products = recommended_products_from_list, add_to_cart_form = add_to_cart_form)



@app.route('/PR', methods = ['GET','POST'])
@login_required
def pr_page():
    pr_id = str(request.args.get('generated_pr_id'))
    pr_items = SubmittedPR.query.filter_by(pr_id = pr_id).all()
    return render_template('prPage.html', pr_items= pr_items)

@app.route('/submittedPRs', methods = ['GET','POST'])
@login_required
def submitted_pr_page():

    return render_template('submittedPRPage.html')
