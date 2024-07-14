import sqlite3
import logging
from flask import Flask, jsonify, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

# Global variable to count database connections
db_connection_count = 0

# Function to get a database connection.
def get_db_connection():
    global db_connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    connection.close()
    return post

# Function to count the total number of posts
def get_post_count():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    connection.close()
    return post_count

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logger.info('Non-existing article accessed, returning 404')
        return render_template('404.html'), 404
    else:
        logger.info('Article "%s" retrieved!', post['title'])
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logger.info('About Us page retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
            connection.commit()
            connection.close()
            logger.info('New article "%s" created!', title)

            return redirect(url_for('index'))

    return render_template('create.html')

# Healthcheck endpoint
@app.route('/healthz')
def healthz():
    try:
        connection = get_db_connection()
        connection.execute('SELECT 1 FROM posts LIMIT 1')
        connection.close()
        response = jsonify({"result": "OK - healthy"})
        return response, 200
    except Exception as e:
        logger.error('Health check failed: %s', e)
        response = jsonify({"result": "ERROR - unhealthy", "details": str(e)})
        return response, 500

# Metrics endpoint
@app.route('/metrics')
def metrics():
    post_count = get_post_count()
    response = {
        "db_connection_count": db_connection_count,
        "post_count": post_count
    }
    return jsonify(response), 200

# Start the application on port 3111
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3111)
