from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from whisky_manager import WhiskyManager, User, Bottle

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # This is needed for session management

# Mock user authentication
def is_logged_in():
    return 'username' in session

@app.route('/', methods=['GET', 'POST'])
def search():
    if not is_logged_in():  # If the user is not logged in, redirect to login page
        return redirect(url_for('login'))
    
    if request.method == 'POST': # Direct search
        query = request.form.get('search')
    elif request.method == 'GET': # URL search or refresh
        query = request.args.get('search')
    query = query if query else ""  # If query is None, set it to an empty string

    
    # Retrieve sorting and filtering arguments
    sort_by = request.args.get('sort_by', None)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_age = request.args.get('min_age', type=int)
    max_age = request.args.get('max_age', type=int)
    distilleries = request.args.getlist('distilleries')

    source = request.args.get('source', None)

    if source == None:
        results = WhiskyManager.search_bottles(query)
        results = WhiskyManager.sort_bottles(sort_by, results)
        results = WhiskyManager.filter_bottles(min_price, max_price, min_age, max_age, distilleries, results)
        return render_template('search.html', results=results, query=query, all_distilleries = WhiskyManager.all_distilleries())
    
    elif source == 'my_collection':
        username = session['username']
        users = User.load_users()
        user = next((u for u in users if u['username'] == username), None)
        results = WhiskyManager.search_bottles(query, user['collection'])
        results = WhiskyManager.sort_bottles(sort_by, results)
        results = WhiskyManager.filter_bottles(min_price, max_price, min_age, max_age, distilleries, results)
        return render_template('collection.html', results=results, query=query, all_distilleries = WhiskyManager.all_distilleries())
    
    elif source == 'my_wishlist':
        username = session['username']
        users = User.load_users()
        user = next((u for u in users if u['username'] == username), None)
        results = WhiskyManager.search_bottles(query, user['wishlist'])
        results = WhiskyManager.sort_bottles(sort_by, results)
        results = WhiskyManager.filter_bottles(min_price, max_price, min_age, max_age, distilleries, results)
        return render_template('wishlist.html', results=results, query=query, all_distilleries = WhiskyManager.all_distilleries())
    

    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve login data
        username = request.form['username']
        password = request.form['password']
        
        # Load users from the JSON file
        users = User.load_users()
        
        # Check if the username exists and store the user data
        user = next((u for u in users if u['username'] == username), None)
        if not user:
            flash('Username not found. Please register first.', 'error')
            return redirect(url_for('register'))  # Redirect to the registration page
        
        # Validate the password
        if user['password'] == password:
            session['username'] = username  # Store username in session
            return redirect(url_for('search'))  # Redirect to the search page
        else:
            flash('Incorrect password. Please try again.', 'error')
            return render_template('login.html')  # Re-render login page

    return render_template('login.html')  # Render the login page

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        # Check if the username is already taken
        usernames = {user['username'] for user in User.load_users()}
        if username in usernames:
            flash('Username already taken!', 'error')
            return redirect(url_for('register'))

        # Check if the passwords match
        if password != password_confirm:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))

        # Store the new user in the JSON file
        User(username, password)
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear  # Clear the session data
    return redirect(url_for('login'))  # Redirect to login page after logout



@app.route('/my_collection')
def my_collection():
    if 'username' not in session:
        return redirect(url_for('login'))

    
    return redirect(url_for('search', source = 'my_collection'))


@app.route('/add_to_collection/<bottle_id>', methods=['POST'])
def add_to_collection(bottle_id):
    if not is_logged_in():  # If the user is not logged in, redirect to login page
        return redirect(url_for('login'))
    
    username = session['username']
    users = User.load_users()
    user = next((u for u in users if u['username'] == username), None) # dictionary object

    if user:
        bottle = Bottle.get_bottle_by_id(int(bottle_id))
        if not any (b['id'] == bottle['id'] for b in user['collection']):
            User.amend_collection(user,bottle, True)
            flash_message = f'{bottle['name']} added to your collection.'
            message_type = 'success'
        else:
            flash_message = f'{bottle['name']} is already in your collection.'
            message_type = 'error'

    # Redirect back to the search page via AJAX
    return jsonify({'message': flash_message, 'type': message_type})
            

    


@app.route('/remove_from_collection/<int:bottle_id>', methods=['POST'])
def remove_from_collection(bottle_id):
    if not is_logged_in():  # If the user is not logged in, redirect to login page
        return redirect(url_for('login'))
    
    username = session['username']
    users = User.load_users()
    user = next((u for u in users if u['username'] == username), None) # dictionary object
    

    # Remove the bottle from the user's collection
    bottle = Bottle.get_bottle_by_id(int(bottle_id))
    User.amend_collection(user, bottle, False)


    # Redirect back to the "My Collection" page
    flash(f'{bottle['name']} removed from your collection.')
    return redirect(url_for('search', query='', source='my_collection'))

@app.route('/edit_rating/<int:bottle_id>', methods=['POST'])
def edit_rating(bottle_id):

    rating = request.form['rating']

    username = session['username']
    users = User.load_users()
    user = next((u for u in users if u['username'] == username), None) # dictionary object

    bottle = Bottle.get_bottle_by_id(int(bottle_id))

    User.amend_collection(user, bottle, int(rating))  # Edit the rating of the bottle, convert to int to avoid editing note
    
    flash(f'Rating edited successfully to {rating} stars for {bottle['name']}!', 'success')
    return redirect(url_for('my_collection'))



@app.route('/my_wishlist')
def my_wishlist():
    if 'username' not in session:
        return redirect(url_for('login'))

    
    return redirect(url_for('search', source = 'my_wishlist'))


@app.route('/add_to_wishlist/<bottle_id>', methods=['POST'])
def add_to_wishlist(bottle_id):
    if not is_logged_in():  # If the user is not logged in, redirect to login page
        return redirect(url_for('login'))
    
    username = session['username']
    users = User.load_users()
    user = next((u for u in users if u['username'] == username), None) # dictionary object

    if user:
        bottle = Bottle.get_bottle_by_id(int(bottle_id))
        if not any (b['id'] == bottle['id'] for b in user['wishlist']):
            User.amend_wishlist(user,bottle, True)
            flash_message = f'{bottle['name']} added to your wishlist.'
            message_type = 'success'
        else:
            flash_message = f'{bottle['name']} is already in your wishlist.'
            message_type = 'error'

    # Redirect back to the search page via AJAX
    return jsonify({'message': flash_message, 'type': message_type})
            

    


@app.route('/remove_from_wishlist/<int:bottle_id>', methods=['POST'])
def remove_from_wishlist(bottle_id):
    if not is_logged_in():  # If the user is not logged in, redirect to login page
        return redirect(url_for('login'))
    
    username = session['username']
    users = User.load_users()
    user = next((u for u in users if u['username'] == username), None) # dictionary object
    

    # Remove the bottle from the user's wishlist
    bottle = Bottle.get_bottle_by_id(int(bottle_id))
    User.amend_wishlist(user, bottle, False)


    # Redirect back to the "My Wishlist" page
    flash(f'{bottle['name']} removed from your wishlist.')
    return redirect(url_for('search', query='', source='my_wishlist'))


# For both collection and wishlist pages
@app.route('/edit_note/<int:bottle_id>', methods=['POST'])
def edit_note(bottle_id):
    if not is_logged_in():  # If the user is not logged in, redirect to login page
        return redirect(url_for('login'))

    
    note = request.form.get('note')  # Get the note from the form

    username = session['username']
    users = User.load_users()
    user = next((u for u in users if u['username'] == username), None) # dictionary object

    bottle = Bottle.get_bottle_by_id(int(bottle_id))


    if "my_collection" in request.referrer:
        User.amend_collection(user, bottle, note)  # Add the note to the bottle
        flash(f'Note edited successfully for {bottle['name']}!', 'success')
        return redirect(url_for('my_collection'))
    
    elif "my_wishlist" in request.referrer:
        User.amend_wishlist(user, bottle, note)  # Add the note to the bottle
        flash(f'Note edited successfully for {bottle['name']}!', 'success')
        return redirect(url_for('my_wishlist'))

@app.route('/create_bottle', methods=['POST'])
def create_bottle():
    """Handle the creation of a new bottle."""

    # Extract data from the request
    name = request.form.get('name')
    distillery = request.form.get('distillery')
    bottle_type = request.form.get('type')
    age = request.form.get('age', type=int)
    abv = request.form.get('abv', type=float)
    price = request.form.get('price', type=float)
    image_url = request.form.get('image_url')


    Bottle(name, distillery, bottle_type, age, abv, price, image_url)

    return redirect(url_for('search'))


    
    





if __name__ == '__main__':
    app.run(debug=True)

