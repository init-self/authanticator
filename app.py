from flask import Flask, url_for, request, redirect, jsonify
from datetime import datetime
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash 

# loading templates



app = Flask(__name__) # referencing this file
app.secret_key = "authanticatorHashPasswordSecretKey"


try:
	mongo_client = MongoClient('localhost', 27017)  # or app.config['MONGO_URI'] = 'mongodb://localhost:27017/authanticator_db'

	database = mongo_client['DatabaseAuthanticator']		# assigning the database to client

	print('\n\n---------- Connection Successfull ---------------\n\n')
except:
	print('\n\nCould not connect to database. Error\n\n')


# index route
@app.route('/')
def server():
	return "Hello Pythonist! Your server is running ..."

@app.route('/api/auth/signup', methods=['POST'])
def signupRoute():
	print('\n\nRequest Received >>> ', request.json)
	_username = request.json['username'].lower()
	_password = request.json['password']
	_email = request.json['email'].lower()
	_name = request.json['name']

	collection = database['users'] 		# assigning the collection to database

	if request.method == 'POST':
		_hashed_password = generate_password_hash(_password)

		try:
			query = {'username': _username}
			document = collection.find_one(query)
			# make an api for email duplicate verification
			if document and document['username'] == _username:
				response = jsonify({
					'message': 'User already signed up. Please try logging in!',
					'give_access': False,
					'creds_match': True
				})
				response.status_code == 200
			else:
				collection.insert_one({
				    'name': _name,
				    'email': _email,
		            'username': _username,
		            'password': _hashed_password,
		            'last_updated': datetime.utcnow()
				})
				response = jsonify({
					'message': "User added Successfully"
				})
				response.status_code = 200
		except:
			print('Could not insert new user', e)
			response = jsonify({'message': 'Could not signup a new user'})
			response.status_code = 500
		return response
	else:
		return not_found()


@app.route('/api/auth/login', methods=['POST'])
def loginRoute():
	print('\n\nRequest Recieved >>> ', request.json)

	_username = request.json['username'].lower()
	_password = request.json['password']

	collection = database['users']

	if request.method == 'POST' and isinstance(_username, str) and isinstance(_password, str):
		try:
			query = {'username': _username}
			document = collection.find(query)
			if check_password_hash(document[0]['password'], _password):
				response = jsonify({
					'message': 'Welcome returning user',
					'give_access': True,
					'creds_match': True
               })
				response.status_code = 200
			else:
				response = jsonify({
					'message': "Wrong Credentials. Please try again!",
					'give_access': False,
					'creds_match': False
				})
		except:
			print('Could not find a collection with requested name ')
			response = jsonify({
				'message': 'Could not find the returning user. ',
				'give_access': False,
				'creds_match': None
           })
			response.status_code = 200
		return response
	else:
		return not_found()


@app.route('/user/creds/delete/<int:id>')
def deleteCreds(id: int):
	pass

@app.errorhandler(404)
def not_found(error=None):
	response = jsonify({
		'status': 404,
		'message': 'Request not found for url: ' + request.url
	})
	response.status_code = 404

	return response



if __name__ == "__main__":
	app.run(debug=True) # if any errors pop, they appear on web page