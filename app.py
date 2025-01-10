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

    source = request.args.get('source', None)
    if source == None:
        results = WhiskyManager.search_bottles(query)

        return render_template('search.html', results=results, query=query)
    
    elif source == 'my_collection':
        username = session['username']
        users = User.load_users()
        user = next((u for u in users if u['username'] == username), None)
        results = WhiskyManager.search_bottles(query, user['collection'])
        return render_template('collection.html', results=results, query=query)
    

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


@app.route('/my_collection')
def my_collection():
    if 'username' not in session:
        return redirect(url_for('login'))

    
    return redirect(url_for('search', source = 'my_collection'))

@app.route('/edit_note/<int:bottle_id>', methods=['POST'])
def edit_note(bottle_id):
    if not is_logged_in():  # If the user is not logged in, redirect to login page
        return redirect(url_for('login'))

    note = request.form.get('note')  # Get the note from the form

    username = session['username']
    users = User.load_users()
    user = next((u for u in users if u['username'] == username), None) # dictionary object

    bottle = Bottle.get_bottle_by_id(int(bottle_id))

    User.amend_collection(user, bottle, note)  # Add the note to the bottle

    flash(f'Note edited successfully for {bottle['name']}!', 'success')
    return redirect(url_for('my_collection'))

@app.route('/edit_rating/<int:bottle_id>', methods=['POST'])
def edit_rating(bottle_id):

    rating = request.form['rating']

    username = session['username']
    users = User.load_users()
    user = next((u for u in users if u['username'] == username), None) # dictionary object

    bottle = Bottle.get_bottle_by_id(int(bottle_id))

    User.amend_collection(user, bottle, int(rating))  # Edit the rating of the bottle
    
    flash(f'Rating edited successfully to {rating} stars for {bottle['name']}!', 'success')
    return redirect(url_for('my_collection'))






if __name__ == '__main__':
    app.run(debug=True)

