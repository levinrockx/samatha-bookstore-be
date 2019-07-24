from flask import Flask, request
from bson import json_util
from bson.objectid import ObjectId
import json
# from flask import jsonify
from flask_restful import Resource, Api, reqparse
import pymongo
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["samatha"]
booksCollection = db["books"]
categoriesCollection = db["categories"]
authorsCollection = db["authors"]
developementCollection = db["developement"]

UPLOAD_FOLDER = "F:/samatha-bookstore/src/assets/img"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
api = Api(app)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5*1024*1024

class BookAll(Resource):
    def get(self):
        categorywiselist = []
        categorylist = json.loads(json_util.dumps(categoriesCollection.find({})));
        # categorylist = categoriesCollection.find({});
        # categoryList = [{"category_name":"1"},{"category_name":"1"},{"category_name":"1"}]
        for categoryobj in categorylist:
            obj = {
                "category_name": categoryobj["category_name"],
                "books": json.loads(json_util.dumps(booksCollection.find({"category": categoryobj["category_name"]})))
            }
            categorywiselist.append(obj);
        return {'status': 'success', 'data': {'categories': categorywiselist}}


class AddCategory(Resource):
    def post(self):
        category = request.get_json();
        id = 0;
        id = categoriesCollection.insert_one(category).inserted_id;
        if len(id) != 0:
            return {'status': 'success'}
        else:
            return {'status': 'error'}
        # print(category)
        # return {'status':'success'}


class AddAuthor(Resource):
    def post(self):
        author = request.get_json();
        # print(author)
        # auth = AuthorsCollection.find({})
        # print(len(json.loads(json_util.dumps(auth))))
        authorsCollection.insert_one(author)
        return {'status': 'success'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class AddBookImage(Resource):
    def post(self):
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(filename)
            return {'status': 'success'}
        else:
            return {'status': 'error'}

class AddBook(Resource):
    def post(self):
        book = request.get_json();
        booksCollection.insert_one(book)
        return {'status':'sucess'}

class AuthorAll(Resource):
    def get(self):
        count = 0;
        authorList = [];
        authordblist = json.loads(json_util.dumps(authorsCollection.find({})));
        # authordblist = authorsCollection.find({});
        for author in authordblist:
            count = count + 1;
            authobj = {
                "id": count,
                "itemName": author["author_name"]
            };
            authorList.append(authobj);
        return {'status': 'success', "data": authorList}


class CategoryAll(Resource):
    def get(self):
        count = 0;
        categoriesList =[];
        categorydblist = json.loads(json_util.dumps(categoriesCollection.find({})));
        # categorydblist = categoriesCollection.find({});
        for category in categorydblist:
            count = count+1;
            obj = {
                "id" : count,
                "itemName" : category["category_name"]
            };
            categoriesList.append(obj);
        return {'status': 'success', "data": categoriesList}

api.add_resource(BookAll, '/api/bookall')
api.add_resource(AddCategory, '/api/addcategory')
api.add_resource(AddAuthor, '/api/addauthor')
api.add_resource(AddBookImage, '/api/addbookimage')
api.add_resource(AddBook, '/api/addbook')
api.add_resource(CategoryAll, '/api/categoryall')
api.add_resource(AuthorAll, '/api/authorall')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
