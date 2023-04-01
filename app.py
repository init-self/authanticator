from flask import Flask, url_for, request, redirect, jsonify
from markupsafe import escape
from datetime import datetime
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import secrets

# loading routes
# import routes



app = Flask(__name__, template_folder="templates") # referencing this file
cors = CORS(app, resources={
	r"/api/*": {
	"origins": "*"
	}
	})
app.secret_key = "8ut4a6t1c2tor4a5hPa55word53cr6tK2y"



try:
	mongo_client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=10000)  # or app.config['MONGO_URI'] = 'mongodb://localhost:27017/authanticator_db'
	if(mongo_client.server_info()):
		database = mongo_client['DatabaseAuthanticator']		# assigning the database to client
		print('\n\n---------- Connection Successful ---------------\n\n')
	else:
		"""
		source: https://kb.objectrocket.com/mongo-db/check-if-a-mongodb-server-is-running-using-the-pymongo-python-driver-643
		MongoDB is a powerful document database that focuses on search and document retrieval capabilities. Exception raising is not the highest priority. But that should be okay giving what MongoDB has to offer far outweighs how it handles exceptions.

		When the MongoClient() receives the settings of the port and domain and they aren’t the same as the server, an exception won’t automatically be raised. The good news is that there are ways to go around it so your coding isn’t hindered in the least.
		
		# Raise an Exception with server_info() client object method
		-> The server_info() method of the client object can be called when MongoDB returns a client instance. You’re verifying that the instance is genuine. An exception ServerSelectionTimeoutError is shown when the port string and domain settings are wrong.

		"""
		raise Exception
except Exception as e:
	print('\n\nCould not connect to database. Error: ', e)


# index route
@app.route('/')
def server():
	"""
	To access the qyery params, use request.args.get('name')
	"""
	return "Hello Pythonist! Your server is running ..."


@app.route('/api/auth/signup', methods=['POST'])
def signupRoute():
	print('\n\nRequest Received >>> ', request.json)

	# variable keys to save in the database
	_username = request.json['email'].split('@')[0].lower()
	_password = request.json['password']
	_email = request.json['email'].lower()
	_name = request.json['name']

	collection = database['users'] 		# collection[table] being used

	_hashed_password = generate_password_hash(_password)

	try:
		# query to find the user with same email in document
		query = {'email': _email}
		document = collection.find_one(query)

		# match the email with database for returning user
		if document and document['email'] == _email:
			response = jsonify({
				'message': 'User already signed up. Please try logging in!',
				'give_access': False
				})
			response.status_code == 200
		else:
			collection.insert_one({
				'name': _name,
				'email': _email,
				'username': _username,
				'password': _hashed_password,
				'last_updated': datetime.utcnow(),
				'secret_key': secrets.token_hex()
				})
			response = jsonify({
				'message': "User added Successfully",
				'give_access': True
				})
			response.status_code = 200
	except Exception as e:
		print('\n\n\nSuffered Internal Server Error: ', e)
		response = jsonify({
			'message': 'Could not signup a new user',
			'server_error': True,
			'give_access': False
			})
		response.status_code = 500
	return response
# Signup Route Ends


@app.route('/api/auth/login', methods=['POST'])
def loginRoute():
	print('\n\nRequest Recieved >>> ', request.json)

	_email = request.json['email'].lower()
	_password = request.json['password']

	collection = database['users']	# collection[table] being used

	try:
		query = {'email': _email}
		document = collection.find(query)

		if collection.count_documents(query) == 1:
			if check_password_hash(document[0]['password'], _password):
				data = []
				for doc in document:
					doc['_id'] = str(doc['_id'])
					data.append(doc)
					response = jsonify({
						'message': 'Welcome returning user',
						'give_access': True,
						'data': data
					})
					response.status_code = 200
			else:
				response = jsonify({
					'message': "Wrong Credentials. Please try again!",
					'give_access': False
				}), 200
		else:
			print('Multiple Users found. ')
			response = jsonify({
				'message': 'Server Error. Multiple Users found.',
				'give_access': False,
			}), 500
	except Exception as e:
		print('\n\n\nSuffered Internal Server Error: ', e)
		response = jsonify({
			'message': 'Internal Server Error. ',
			'give_access': False,
			'server_error': True
			}), 500
	return response
# Login Route Ends



@app.route('/api/user/creds/update/<string:user_id>', methods=['PUT'])
def updateProfile(user_id: str):
	print('\n\n Updating Profile: ', user_id)
	print('\n\n Request Received: ', request.json)

	expected_keys = ['username', 'email', 'password', 'theme_mode', 'profile_image']

	received_keys = {key.lower(): request.json[key] for key in request.json if key in expected_keys and request.json[key] not in ('', None)}

	collection = database['users']		# collection[table] being used

	print(received_keys)

	## learn about Async/Await

	try:
		if(request.args.get('loggedin') and isinstance(user_id, str)):
			# assign a new secret key if password or email is changed
			if ('password' in received_keys or 'email' in received_keys):
				received_keys['secret_key'] = secrets.token_hex()

			query = {'_id': ObjectId(user_id)}
			document = collection.find(query)

			if document and len(document) == 1:
				collection.insert_one(received_keys)
				response = jsonify({
					message: 'User updated successfully. ',
					log_out: True,
					give_access: True,
					data: list(document)
				}), 200
			else:
				print('Multiple Documents Found. Server Error. ')
				response = jsonify({
					message: 'Server Error. Multiple Documents Found. ',
					give_access: True,
					log_out: False,
					data: []
				}), 500
	except Exception as e:
		print('Suffered Internal Server Error: ', e)
		response = jsonify({
			message: 'Internal Server Error. ',
			give_access: False,
			log_out: False,
			data: [],
		}), 500
	return response





@app.route('/user/creds/delete/<int:id>')
def deleteCreds(id: int):
	pass

@app.errorhandler(404)
@app.errorhandler(405)
def requestNotFound(error=None):
	response = jsonify({
		'status': 405,
		'message': 'Request not found for url: ' + request.url
	})
	response.status_code = 405

	return response












if __name__ == "__main__":
	app.run(debug=True) # if any errors pop, they appear on web page