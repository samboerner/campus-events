from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from helpers import create_db
import sqlite3

# Configure application
app = Flask(__name__)

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Creation of database, if one does not currently exist
create_db()


@app.route('/')
def home():
    '''Display Homepage'''

    # Get every event from the database
    with sqlite3.connect('database.sqlite') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM events')
        events = c.fetchall()
        for i in range(len(events)):
            events[i] = {
                'id': events[i][0],
                'name': events[i][1],
                'date': events[i][2],
                'description': events[i][3],
                'user_id': events[i][4]
            }

    # Display login and signup buttons if not logged in
    if session.get('user') is None:
        return render_template('index.html', events=events)
    else:
        return render_template('index.html', user=session.get('user')['username'], events=events)


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    '''Sign up for new account'''
    if request.method == 'POST':
        # Check if username, password, and confirmation fields are filled
        if not request.form['username']:
            return render_template('signup.html', error='Username field cannot be left blank')
        elif not request.form['password']:
            return render_template('signup.html', error='Password field cannot be left blank')
        elif not request.form['confirmation']:
            return render_template('signup.html', error='Please confirm your password')
        
        # Check if password and confirmation match
        elif request.form['password'] != request.form['confirmation']:
            return render_template('signup.html', error='Passwords do not match')
        
        with sqlite3.connect('database.sqlite') as conn:
            c = conn.cursor()

            # Check if username already exists
            c.execute('SELECT * FROM users WHERE username=?', (request.form['username'],))
            rows = c.fetchall()
            if len(rows) != 0:
                return render_template('signup.html', error='Username is taken')

            # Insert new user into database
            c.execute('INSERT INTO users (username, password) VALUES (?,?)', (request.form['username'], request.form['password']))

            conn.commit()

        # Redirect user to the login page
        return redirect('/login')
    
    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Log user in'''
    if request.method == 'POST':
        # Check if username and password fields are filled
        if not request.form['username']:
            return render_template('login.html', error='Please provide a username')
        elif not request.form['password']:
            return render_template('login.html', error='Please provide a password')
        
        with sqlite3.connect('database.sqlite') as conn:
            c = conn.cursor()

            # Check if username exists and password is correct
            c.execute('SELECT * FROM users WHERE username=?', (request.form['username'],))
            rows = c.fetchall()
            if len(rows) != 1 or rows[0][2] != request.form['password']:
                return render_template('login.html', error='Invalid login')

            # Remember user has logged in
            session['user'] = {
                'id': rows[0][0],
                'username': rows[0][1]
            }

        # Redirect to homepage
        return redirect('/')

    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    '''Log user out'''

    # Forget any user id
    session.clear()

    # Redirect to home page
    return redirect('/')


@app.route('/create', methods=['GET', 'POST'])
def create_event():
    '''Create an event'''
    if session.get('user') is None:
        return redirect('/')

    if request.method == 'POST':
        # Check if fields are filled
        if not request.form['name']:
            return render_template('create.html', error='Please provide a name for the event')
        elif not request.form['date']:
            return render_template('create.html', error='Please select a date for the event')
        elif not request.form['description']:
            return render_template('create.html', error='Please provide a description for the event')
        
        with sqlite3.connect('database.sqlite') as conn:
            c = conn.cursor()

            # Insert event into database
            c.execute(
                'INSERT INTO events (name, date, description, user_id) VALUES (?,?,?,?)',
                (request.form['name'], request.form['date'], request.form['description'], session.get('user')['id'])
            )

        # Redirect to home page
        return redirect('/')
    
    else:
        return render_template('create.html', user=session.get('user')['username'])


@app.route('/event/<int:id>', methods=['GET'])
def view_event(id):
    '''View an event'''
    with sqlite3.connect('database.sqlite') as conn:
        c = conn.cursor()

        # Get event from database
        c.execute('SELECT * FROM events WHERE id=?', (id,))
        event = c.fetchall()
        if len(event) != 1:
            return redirect('/')
        event = {
            'id': event[0][0],
            'name': event[0][1],
            'date': event[0][2],
            'description': event[0][3],
            'user_id': event[0][4]
        }

        # Get all users who have rsvp'd to the event
        c.execute('SELECT * FROM rsvps WHERE event_id=?', (id,))
        rsvps = c.fetchall()
        rsvp_users = []
        for rsvp in rsvps:
            c.execute('SELECT * FROM users WHERE id=?', (rsvp[0],))
            user = c.fetchall()
            rsvp_users.append(user[0][1])

        # Get all comments for the event, in reverse chronological order
        c.execute('SELECT * FROM comments WHERE event_id=? ORDER BY id DESC', (id,))
        comments = c.fetchall()
        event_comments = []
        for comment in comments:
            c.execute('SELECT * FROM users WHERE id=?', (comment[1],))
            user = c.fetchall()
            print("comment", comment)
            event_comments.append(
                {
                    'user': user[0][1],
                    'comment': comment[3]
                }
            )

        # If user is logged in, check if user has rsvp'd to event
        if session.get('user') is not None:
            c.execute('SELECT * FROM rsvps WHERE user_id=? AND event_id=?', (session.get('user')['id'], id))
            rsvp = c.fetchall()
            if len(rsvp) != 0:
                user_rsvp = True
            else:
                user_rsvp = False

    if session.get('user') is None:
        return render_template('event.html', event=event, rsvp_users=rsvp_users)

    return render_template('event.html', user=session.get('user')['username'], event=event, rsvp_users=rsvp_users, user_rsvp=user_rsvp, comments=event_comments)


@app.route('/rsvp/<int:id>', methods=['POST'])
def rsvp(id):
    '''RSVP to an event'''
    if session.get('user') is None:
        return redirect('/event/' + str(id))

    with sqlite3.connect('database.sqlite') as conn:
        c = conn.cursor()

        # Insert rsvp'd event into database
        c.execute('INSERT INTO rsvps VALUES (?,?)', (session.get('user')['id'], id))

    return redirect('/event/' + str(id))


@app.route('/post-comment/<int:id>', methods=['POST'])
def post_comment(id):
    '''Post a comment on an event'''
    if session.get('user') is None:
        return redirect('/event/' + str(id))

    if not request.form['comment']:
        return redirect('/event/' + str(id))

    with sqlite3.connect('database.sqlite') as conn:
        c = conn.cursor()

        # Insert comment into database
        c.execute('INSERT INTO comments (user_id, event_id, comment) VALUES (?,?,?)', (session.get('user')['id'], id, request.form['comment']))

    return redirect('/event/' + str(id))


@app.route('/account', methods=['GET'])
def account():
    '''View account information'''
    if session.get('user') is None:
        return redirect('/')
    
    with sqlite3.connect('database.sqlite') as conn:
        c = conn.cursor()

        # Get events that user has created
        c.execute('SELECT * FROM events WHERE user_id=?', (session.get('user')['id'],))
        events = c.fetchall()
        user_events = []
        for event in events:
            user_events.append(
                {
                    'id': event[0],
                    'name': event[1],
                    'date': event[2],
                    'description': event[3]
                }
            )

        # Get events that user has rsvp'd for
        c.execute(
            '''
                SELECT * FROM events
                JOIN rsvps ON events.id = rsvps.event_id
                JOIN users ON rsvps.user_id = users.id
                WHERE users.id = ?
            ''',
            (session.get('user')['id'],)
        )
        rsvps = c.fetchall()
        user_rsvps = []
        for event in rsvps:
            user_rsvps.append(
                {
                    'id': event[0],
                    'name': event[1],
                    'date': event[2],
                    'description': event[3]
                }
            )

    return render_template('account.html', user=session.get('user')['username'], user_events=user_events, user_rsvps=user_rsvps)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)