from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {"company": "team Angular Developers"}

api.add_resource(HelloWorld, '/api')

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)