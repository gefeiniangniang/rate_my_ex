
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

current_user = None

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
DATABASEURI = "postgresql://gz2315:992144@34.73.36.248/project1" # Modify this with your own credentials you received from Joseph!


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():
      return render_template("index.html")

# Route for handling the login page logic
@app.route('/userlogin', methods=['GET', 'POST'])
def userlogin():
    global current_user
    users = g.conn.execute("SELECT User_ID FROM user_table")
    User_IDs = []
    for result in users:
        User_IDs.append(result['user_id'])
    users.close()

    error = None
    if request.method == 'POST':
        if request.form['username'] not in User_IDs:
            error = 'Invalid Credentials. Please try again.'
        else:
            password = g.conn.execute('SELECT Password FROM user_table WHERE User_ID = (%s)' , request.form['username'])
            mypass = []
            for item in password:
                mypass.append(item['password'])
            if request.form['password'] != mypass[0]:
                error = 'Invalid Credentials. Please try again.'
            else:
                current_user = request.form['username']
                return redirect(url_for('.home'))
            password.close()
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    global current_user
    users = g.conn.execute("SELECT User_ID FROM user_table")
    User_IDs = []
    for result in users:
        User_IDs.append(result['user_id'])
    users.close()

    error = None
    if request.method == 'POST':
        if request.form['username'] in User_IDs:
            error = 'Repeated User Id. Please try again.'
        else:
            username = request.form['username']
            password = request.form['password']
            city = request.form['city']
            birthday = request.form['birthday']
            sex = request.form['sex']
            ethnicity = request.form['ethnicity']
            sexual_orientation = request.form['sexual_orientation']
            g.conn.execute('INSERT INTO user_table(User_ID,Password,City,Sex,Birthday,Ethnicity,Sexual_Orientation,Number_of_likes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', username, password,city,sex,birthday,ethnicity,sexual_orientation,0)
            current_user = request.form['username']
            return redirect(url_for('.more'))
    return render_template('register.html', error=error)


@app.route('/more', methods=['GET', 'POST'])
def more():
    global current_user
    registed_users = g.conn.execute("SELECT User_ID FROM registered_user")
    Registed_User_IDs = []
    for result in registed_users:
        Registed_User_IDs.append(result['user_id'])
    registed_users.close()

    error = None
    if request.method == 'POST':
        if current_user in Registed_User_IDs:
            error = 'This id have already registed. Please try again.'
        else:
            name = current_user
            phone_number = request.form['phone_number']
            email = request.form['email']
            real_id = request.form['real_id']
            g.conn.execute('INSERT INTO registered_user(User_ID,phone_number,email,real_id) VALUES (%s, %s, %s, %s)', name,phone_number,email,real_id)
            return redirect(url_for('.home'))
    return render_template("more.html",error=error,user=current_user)

#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/home')
def home():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  cursor1 = g.conn.execute("SELECT User_ID FROM user_table ORDER BY number_of_likes desc LIMIT 5")
  User_IDs = []
  for result in cursor1:
    User_IDs.append(result['user_id'])  # can also be accessed using result[0]
  cursor1.close()
  context1 = dict(data1 = User_IDs)

  cursor2 = g.conn.execute("SELECT user_table.User_ID FROM user_table natural join registered_user ORDER BY registered_user.average_overall_score desc LIMIT 5")
  User_IDs2 = []
  for result in cursor2:
    User_IDs2.append(result['user_id'])  # can also be accessed using result[0]
  cursor2.close()
  context2 = dict(data2 = User_IDs2)

  cursor3 = g.conn.execute("SELECT user_table.User_ID FROM user_table natural join registered_user ORDER BY registered_user.average_appearance_score desc LIMIT 5")
  User_IDs3 = []
  for result in cursor3:
    User_IDs3.append(result['user_id'])  # can also be accessed using result[0]
  cursor3.close()
  context3 = dict(data3 = User_IDs3)

  cursor4 = g.conn.execute("SELECT user_table.User_ID FROM user_table natural join registered_user ORDER BY registered_user.average_personality_score desc LIMIT 5")
  User_IDs4 = []
  for result in cursor4:
    User_IDs4.append(result['user_id'])  # can also be accessed using result[0]
  cursor3.close()
  context4 = dict(data4 = User_IDs4)
  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #



  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("home.html", **context1, **context2,**context3,**context4,user=current_user)

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/rate')
def rate():
  return render_template("rate.html")
@app.route('/discover')
def discover():
  return render_template("discover.html")

@app.route('/post')
def post():
    global current_user
    return render_template("post.html", user=current_user)


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()

@app.route('/search', methods=['GET', 'POST'])
def search():
    users = g.conn.execute("SELECT User_ID FROM user_table")
    User_IDs = []
    for result in users:
        User_IDs.append(result['user_id'])
    users.close()

    users = g.conn.execute("SELECT User_ID FROM registered_user")
    registered = []
    for result in users:
        registered.append(result['user_id'])
    users.close()

    error = None
    if request.method == 'POST':
      if request.form['search'] not in User_IDs:
        error = 'Invalid User ID. Please try again.'
      else:
        userprofile = g.conn.execute("SELECT user_id,city,sex,ethnicity,sexual_orientation,number_of_likes,extract(year from age(now(),Birthday))as age FROM user_table where User_ID = (%s)",request.form['search'])
        User_IDs = []
        for result in userprofile:
          User_IDs.append(result['user_id'])
          User_IDs.append(result['city'])
          User_IDs.append(result['sex'])
          User_IDs.append(result['ethnicity'])
          User_IDs.append(result['sexual_orientation'])
          User_IDs.append(result['number_of_likes'])
          User_IDs.append(result['age'])
        userprofile.close()


        if request.form['search'] not in registered:
          return render_template('profile.html', user_id=User_IDs[0], city=User_IDs[1], sex=User_IDs[2],
          ethnicity=User_IDs[3],sexual_orientation=User_IDs[4],number_of_likes=User_IDs[5], age=User_IDs[6])
        else:
          score = g.conn.execute("SELECT * FROM registered_user where User_ID = (%s)",request.form['search'])
          for result in score:
            User_IDs.append(result['average_overall_score'])
            User_IDs.append(result['average_appearance_score'])
            User_IDs.append(result['average_personality_score'])
          score.close()

          review = g.conn.execute("select x.reviewer, x.start, x.end, re.overall_experience_score, re.appearance_score, re.personality_score, re.review_content, re.review_time from ((select e.review_to_attend_1 as review_number, a.attend_user_2 as reviewer, r.start_time as start, r.end_time as end from eval_for e natural join relationship r natural join attend a where a.attend_user_1=(%s)) UNION ALL (select e1.review_to_attend_2 as review_number, a1.attend_user_1 as reviewer, r1.start_time as start, r1.end_time as end from eval_for e1 natural join relationship r1 natural join attend a1 where a1.attend_user_2=(%s))) x, review re where re.review_id=x.review_number order by x.start desc",request.form['search'],request.form['search'])
          data = review.fetchall()
          review.close()

          posts=g.conn.execute("SELECT p.post_id, p.post_content, p.post_time FROM user_post u natural join posts p where u.User_ID = (%s)",request.form['search'])
          post = posts.fetchall()
          posts.close()


          comments=g.conn.execute("SELECT x.post_id, u.user_id, x.comment_content, x.comment_time from (SELECT * FROM user_post p natural join com_to_post natural join comments c where p.user_id = (%s))x, user_comments u where x.comment_id=u.comment_id",request.form['search'])
          comment = comments.fetchall()
          comments.close()

          return render_template('profile.html', user_id=User_IDs[0], city=User_IDs[1], sex=User_IDs[2],
          ethnicity=User_IDs[3],sexual_orientation=User_IDs[4],number_of_likes=User_IDs[5], age=User_IDs[6], data=data, post=post, comment=comment)
    return render_template('discover.html', error=error)



@app.route('/logout')
def logout():
    global current_user
    current_user = None
    return render_template("index.html")


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
