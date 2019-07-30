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
import re
from flask_mail import Mail, Message

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["samatha"]
booksCollection = db["books"]
categoriesCollection = db["categories"]
authorsCollection = db["authors"]
developementCollection = db["developement"]
loginCollection = db["login"]

password = "samathaadmin"
username = "samathaadmin"
UPLOAD_FOLDER = "/home/ubuntu/dist/samatha-bookstore/assets/img"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
api = Api(app)
CORS(app)
mail = Mail(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.config.update(dict(
   DEBUG = True,
   MAIL_SERVER = 'smtp.gmail.com',
   MAIL_PORT = 587,
   MAIL_USE_TLS = True,
   MAIL_USE_SSL = False,
   MAIL_USERNAME = 'levinrockx@gmail.com',
   MAIL_PASSWORD = 'paozafuaksdzqver',
))


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
        return {'status': 'success', 'data': {'categories': sorted(categorywiselist, key = lambda x: len(x["books"]),reverse=True)}}


class Book(Resource):
    def post(self):
        req = request.get_json();
        id = ObjectId(str(req['id']));
        book = booksCollection.find_one({'_id': id})
        return {'status': 'success', 'data': json.loads(json_util.dumps(book))}


class Category(Resource):
    def post(self):
        req = request.get_json();
        id = ObjectId(req["id"]);
        category = categoriesCollection.find_one({"_id": id});
        bookList = booksCollection.find({'category': category['category_name']})
        # print(json.loads(json_util.dumps(bookList)))
        return {'status': 'success',
                'data': {"category_name": category['category_name'], "books": json.loads(json_util.dumps(bookList))}}


class AddCategory(Resource):
    def post(self):
        category = request.get_json();
        id = 0;
        id = categoriesCollection.insert_one(category).inserted_id;
        if len(str(id)) != 0:
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
        return {'status': 'success'}


class AuthorAll(Resource):
    def get(self):
        count = 0;
        authorList = [];
        authordblist = json.loads(json_util.dumps(authorsCollection.find({})));
        # authordblist = authorsCollection.find({});
        for author in authordblist:
            count = count + 1;
            authobj = {
                "oid": str(author["_id"]["$oid"]),
                "id": count,
                "itemName": author["author_name"]
            };
            authorList.append(authobj);
        return {'status': 'success', "data": authorList}


class CategoryAll(Resource):
    def get(self):
        count = 0;
        categoriesList = [];
        categorydblist = json.loads(json_util.dumps(categoriesCollection.find({})));
        # categorydblist = categoriesCollection.find({});
        for category in categorydblist:
            count = count + 1;
            obj = {
                "oid": str(category["_id"]["$oid"]),
                "id": count,
                "itemName": category["category_name"]
            };
            categoriesList.append(obj);
        return {'status': 'success', "data": categoriesList}


class EditCategory(Resource):
    def post(self):
        req = request.get_json();
        id = ObjectId(str(req['id']));
        category = categoriesCollection.find_one({"_id": id});
        booksCollection.update_many({"category": category["category_name"]},
                                    {"$set": {"category": req["category_name"]}})
        categoriesCollection.update_one({"_id": id}, {"$set": {"category_name": req["category_name"]}})
        return {"status": "success"}


class EditAuthor(Resource):
    def post(self):
        req = request.get_json();
        id = ObjectId(str(req['id']));
        author = authorsCollection.find_one({"_id": id});
        booksCollection.update_many({"author": author["author_name"]}, {"$set": {"author": req["author_name"]}})
        authorsCollection.update_one({"_id": id}, {"$set": {"author_name": req["author_name"]}})
        return {"status": "success"}


class EditBook(Resource):
    def post(self):
        req = request.get_json();
        # print(req);
        id = ObjectId(str(req["id"]));
        booksCollection.update_one({"_id": id},
                                   {"$set":
                                        {"title": req["title"],
                                         "description": req["description"],
                                         "author": req["author"],
                                         "category": req["category"],
                                         "price": req["price"],
                                         "edition": req["edition"],
                                         "image": req["image"]}
                                    }
                                   );
        return {"status": "success"}


class DeleteCategory(Resource):
    def post(self):
        req = request.get_json();
        id = ObjectId(str(req['id']));
        category = categoriesCollection.find_one({"_id": id});
        booksCollection.update_many({"category": category["category_name"]},
                                    {"$set": {"category": "Uncategorised"}});
        categoriesCollection.delete_one({"_id": id});
        return {"status": "success"}


class DeleteAuthor(Resource):
    def post(self):
        req = request.get_json();
        id = ObjectId(str(req['id']));
        category = authorsCollection.find_one({"_id": id});
        booksCollection.update_many({"author": category["author_name"]},
                                    {"$set": {"author": ""}});
        authorsCollection.delete_one({"_id": id});
        return {"status": "success"}


class DeleteBook(Resource):
    def post(self):
        req = request.get_json();
        id = ObjectId(str(req['id']));
        booksCollection.delete_one({"_id": id});
        return {"status": "success"}


class Login(Resource):
    def post(self):
        login = loginCollection.find_one({})
        req = request.get_json();
        if ((req["username"] == login["username"]) and (req["password"] == login["password"])):
            return {"status": "success"}
        else:
            return {"status": "login failed"}


class Search(Resource):
    def post(self):
        req = request.get_json();
        regx = re.compile(req["keyword"], re.IGNORECASE);
        bookList = booksCollection.find(
            {
                "$or": [
                    {
                        "title": regx
                    },
                    {
                        "category": regx
                    },
                    {
                        "author": regx
                    }
                ]
            }
        );
        dataList = [];
        for obj in json.loads(json_util.dumps(bookList)):
            dataList.append(obj);
        #print(req,dataList)
        return {"status": "success","data":dataList}


class ContactUs(Resource):
   def post(self):
       submit = request.get_json();
       print(submit);
       msg = Message(submit['name'],
                     sender=submit['email'],
                     recipients=["levinrockx@gmail.com"])
       mail.send(msg);
       print(msg);
       return {'status': 'success'}, 201



api.add_resource(BookAll, '/api/bookall')
api.add_resource(Book, '/api/book')
api.add_resource(Category, '/api/category')
api.add_resource(AddCategory, '/api/addcategory')
api.add_resource(AddAuthor, '/api/addauthor')
api.add_resource(AddBookImage, '/api/addbookimage')
api.add_resource(AddBook, '/api/addbook')
api.add_resource(CategoryAll, '/api/categoryall')
api.add_resource(AuthorAll, '/api/authorall')
api.add_resource(EditCategory, '/api/editcategory')
api.add_resource(EditAuthor, '/api/editauthor')
api.add_resource(EditBook, '/api/editbook')
api.add_resource(DeleteCategory, '/api/deletecategory')
api.add_resource(DeleteAuthor, '/api/deleteauthor')
api.add_resource(DeleteBook, '/api/deletebook')
api.add_resource(Login, '/api/login')
api.add_resource(Search, '/api/search')
api.add_resource(ContactUs, '/api/contactus')
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
