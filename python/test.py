import os
from dotenv import load_dotenv
from flask import Flask, render_template, send_from_directory, jsonify, request
from flask_sockets import Sockets
from foursquare import Foursquare
from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi

from geventwebsocket.handler import WebSocketHandler
from slack_bot_controller import SlackBotController
from web_socket_bot_controller import WebSocketBotController


#template_dir = 'templates'
#app = Flask(__name__,template_folder='templates')
#app.debug=True

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='$$',
        block_end_string='$$',
        variable_start_string='$',
        variable_end_string='$',
        comment_start_string='$#',
        comment_end_string='#$',
    )
)

# global vars
app = CustomFlask(__name__)
app.debug=True
sockets = Sockets(app)
port = int(os.getenv('PORT', 8080))
web_socket_bot_controller = None
web_socket_protocol = 'ws://'

#@app.route('/<path:path>')
#def send_file(path):
#    return send_from_directory('public', path)

@app.route('/')
def index():
#   return "hello"
    return render_template("index.html")

@app.route('/four/<text>')
def process_websocket_message(text):
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    foursquare_client_id = os.environ.get('FOURSQUARE_CLIENT_ID')
    foursquare_client_secret=os.environ.get('FOURSQUARE_CLIENT_SECRET')

    print foursquare_client_id
    print foursquare_client_secret
    foursquare_client = None
    if foursquare_client_id is not None and foursquare_client_secret is not None:
        foursquare_client = Foursquare(client_id=foursquare_client_id, client_secret=foursquare_client_secret)
    else:
        foursquare_client = None
    query = text + ' Doctor'
    # Get the location entered by the user to be used in the query
    location = 'austin'
    params = {
            'query': query,
            'near': location,
            'radius': 5000,
            'categoryId':'4bf58dd8d48988d104941735,4bf58dd8d48988d10f951735'
        }
    print (params)
    venues = foursquare_client.venues.search(params=params)
    print "here"

    #cvenues = self.foursquare_client.venues.search(params=params)
    if venues is None or 'venues' not in venues.keys() or len(venues['venues']) == 0:
        reply = 'Sorry, I couldn\'t find any doctors near you.'
    else:
        reply = 'Here is what I found:\n';
        for venue in venues['venues']:
            if len(reply) > 0:
                reply = reply + '\n'
            reply = reply + '* ' + venue['name']
    return reply
   # return jsonify(venues)

if __name__ == '__main__':
    port = int(os.getenv("port",9099))
    app.run(host='0.0.0.0',port=port)