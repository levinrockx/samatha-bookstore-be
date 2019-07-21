from flask import Flask, request
from bson import json_util
from bson.objectid import ObjectId
import json
# from flask import jsonify
from flask_restful import Resource, Api, reqparse
import pymongo
from flask_cors import CORS

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["samatha"]
booksCollection = db["books"]
categoriesCollection = db["categories"]

app = Flask(__name__)
api = Api(app)


class BookAll(Resource):
    def get(self):
        categorywiselist = []
        categorylist = json.loads(json_util.dumps(categoriesCollection.find({})));
        for categoryobj in categorylist:
            obj = {
                "category_name": categoryobj["category_name"],
                "books": json.loads(json_util.dumps(booksCollection.find({"category":categoryobj["category_name"]})))
            }
            categorywiselist.append(obj);
        return {'status': 'success', 'data':{ 'categories': categorywiselist}}

api.add_resource(BookAll, '/api/bookall')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
