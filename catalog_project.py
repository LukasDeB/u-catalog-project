from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from db_setup import Base, Category, CategoryItem, User
# Auth imports
from flask import session as login_session, make_response
import random
import string
# Auth flow imports
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from flask import (Flask, render_template,
                   request, redirect, url_for, jsonify, flash)

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///catalogdb.db', convert_unicode=True)
Base.metadata.bind = engine

DBSession = scoped_session(sessionmaker(bind=engine))


@app.route('/catalog/login/')
def loginUser():
    """
    Generates a random state and renders the login template with it
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Gets the user's data from the Google API and assigns it
    to the login_session variable
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
           access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 50)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token client's ID does not match app's"), 401)
        print "Token client's ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            "Current user is already connected"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if user_id:
        login_session['user_id'] = user_id
    else:
        login_session['user_id'] = createUser(login_session)

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height:'
    output += ' 300px;border-radius: 150px;-webkit-border-radius:'
    output += ' 150px;-moz-border-radius: 150px;"> '
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """
    Checks if the user is logged and then proceeds to revoke
    the token from oauth as well as deleting the variables data
    if the correct response was given
    """
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps(
            "Current user not connected."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps(
            "Successfully disconnected. "), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/')
    else:
        response = make_response(json.dumps(
            "Failed to revoke token for given user."), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
def allCategoriesItems():
    """
    Queries the Database for all items and categories, sorting the items
    according to when they were added to the database and renders them
    with the template
    """
    session = DBSession()
    categories = session.query(Category).all()
    latest_items = session.query(CategoryItem).order_by(
        CategoryItem.id.desc()).limit(10).all()
    if 'username' not in login_session:
        return render_template('index.html', categories=categories,
                               user_id=None, latest_items=latest_items)
    else:
        return render_template('index.html', categories=categories,
                               user_id=login_session['user_id'],
                               latest_items=latest_items)


@app.route('/catalog/<string:category_name>/items/')
def showItemsInCategory(category_name):
    """
    Queries the database looking for all the items in a specific category
    and renders the template with the user if he is logged in
    """
    session = DBSession()
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(CategoryItem) \
        .filter(CategoryItem.category_id == category.id) \
        .order_by(CategoryItem.id.desc()).all()
    if 'username' not in login_session:
        return render_template('category_items.html',
                               category=category, items=items, user_id=None)
    else:
        return render_template('category_items.html', category=category,
                               items=items, user_id=login_session['user_id'])


@app.route('/catalog/<string:category_name>/<string:item_title>/')
def showItem(category_name, item_title):
    """
    Queries the database for a specific item and category
    rendering them later
    """
    session = DBSession()
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(CategoryItem).filter_by(title=item_title).one()
    item_creator = getUserInfo(item.user_id)
    if 'username' in login_session:
        return render_template('item_details.html', item=item,
                               item_creator=item_creator,
                               category=category,
                               username=login_session['username'],
                               user_id=login_session['user_id'])
    return render_template('item_details.html', item=item,
                           item_creator=item_creator, category=category)


@app.route('/catalog/new/', methods=['GET', 'POST'])
def addItem():
    """
    Checks if the user is logged in and redirecting him if not
    also if the request is a POST request then proceeds to
    get the data from the form and adding it to the database
    If it is another type of request it renders the template
    to create a new item
    """
    session = DBSession()
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return redirect('/catalog/login')
    if request.method == 'POST':
        category_name = request.form.get("category_name")
        category = session.query(Category).filter_by(name=category_name).one()
        newItem = CategoryItem(title=request.form['title'],
                               description=request.form['description'],
                               category_id=category.id,
                               user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('showItemsInCategory',
                                category_name=category_name))
    else:
        return render_template('item_new.html',
                               categories=categories,
                               user_id=login_session['user_id'])


@app.route('/catalog/<string:category_name>/<string:item_title>/edit/',
           methods=['GET', 'POST'])
def editItem(category_name, item_title):
    """
    Checks if the user is logged in, queries the database for the item
    in question and checks what request is, if it is a POST request checks if
    the user currently  logged in is the one who created it therefore
    allowing him or not to edit the item. Any different request will get the
    template which edit's an item
    """
    if 'username' not in login_session:
        return redirect('/catalog/login')
    session = DBSession()
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(CategoryItem).filter_by(title=item_title).one()
    if request.method == 'POST':
        if login_session['user_id'] is not item.user_id:
            flash('You are not the creator of this item', 'danger')
            return redirect(url_for('showItemsInCategory',
                                    category_name=category.name))
        if request.form['title'] and request.form['description']:
            item.title = request.form['title']
            item.description = request.form['description']
        elif request.form['title']:
            item.title = request.form['title']
        elif request.form['description']:
            item.description = request.form['description']
        session.add(item)
        session.commit()
        flash('Item correctly changed!', 'success')
        return redirect(url_for('showItemsInCategory',
                                category_name=category.name))
    else:
        return render_template('item_edit.html', category=category,
                               item=item, user_id=login_session['user_id'])


@app.route('/catalog/<string:category_name>/<string:item_title>/delete/',
           methods=['GET', 'POST'])
def deleteItem(category_name, item_title):
    """
    Checks if the user is logged in, and queries the databse for the item.
    According to the request method either Deletes the item or renders the page
    for deleting such item. Also checks if the user is the owner of the item in
    question before deleting it.
    """
    if 'username' not in login_session:
        return redirect('/catalog/login')
    session = DBSession()
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(CategoryItem).filter_by(title=item_title).one()
    if request.method == 'POST':
        if login_session['user_id'] is not item.user_id:
            flash('You are not the creator of this item', 'danger')
            return redirect(url_for('showItemsInCategory',
                                    category_name=category.name))
        session.delete(item)
        session.commit()
        flash('Item Correctly deleted!', 'success')
        return redirect(url_for('showItemsInCategory',
                                category_name=category.name))
    else:
        return render_template('item_delete.html',
                               category=category,
                               item=item, user_id=login_session['user_id'])

# API Endoints


@app.route('/catalog/api/items/')
def apiItems():
    """
    Queries the database for all items and serializes them before
    running them through jsonify and returning them
    """
    session = DBSession()
    items = session.query(CategoryItem).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalog/api/item/<int:item_id>/')
def apiOneItem(item_id):
    """
    Queries the database for a specific item and serializes it before
    running it through jsonify and returning it
    """
    session = DBSession()
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


@app.route('/catalog/api/categories/')
def apiCategories():
    """
    Queries the database for all categories and serializes them before
    running them through jsonify and returning them
    """
    session = DBSession()
    categories = session.query(Category).all()
    return jsonify(Category=[i.serialize for i in categories])


@app.route('/catalog/api/category/<int:cat_id>/items')
def apiCatItems(cat_id):
    """
    Queries the database for all items in a specific category and
    serializes them before running them through jsonify
    and returning them
    """
    session = DBSession()
    category = session.query(Category).filter_by(id=cat_id).one()
    items = session.query(CategoryItem).filter_by(
        category_id=category.id).all()
    return jsonify(Category=[i.serialize for i in items])


def createUser(login_session):
    """
    Function called if the user is not registrated locally in the database
    creates a new one and saves it according to the variable login_session
    """
    session = DBSession()
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """
    Gets a specific user's data in the local database according to his
    user_id
    """
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """
    Gets a specific user's ID from the local database using his
    email as a search item
    """
    session = DBSession()
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except DatabaseError:
        return None


if __name__ == '__main__':
    app.secret_key = 'super_secret_extra__extra_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
