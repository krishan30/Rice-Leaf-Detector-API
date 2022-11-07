import os
import uuid
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename
from mongoengine import *
from datetime import datetime
from marshmallow import Schema, fields, validates, validate

UPLOAD_FOLDER = './uploads'
if not(os.path.isdir(UPLOAD_FOLDER)):
    os.mkdir(UPLOAD_FOLDER)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
api = Api(app)
#disease_db_connection = connect('disease', host='localhost', port=27017)
disease_db_connection = connect(host='mongodb+srv://krishan99:2x5DEonuG2kCRkLo@analytics.ycjra.mongodb.net/?retryWrites=true&w=majority',db='disease')
# rice_leaf_disease_detector = RiceLeafDiseaseDetector()
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


class ImageClassifierInputSchema(Schema):
    # the 'required' argument ensures the field exists
    File = fields.Raw(type='file', required=True,
                      error_messages={"required": {"message": 'Missing data for required field', "statusCode": 301}})

    @validates("File")
    def validate_File(self, file):
        if file and file.filename == '':
            raise ValidationError(
                {"Error": {"message": "Missing File name for required file", "statusCode": 302}})
        if not (allowed_file(file.filename)):
            raise ValidationError({"Error": {"message": "Unsupported File Type", "statusCode": 303}})


class FeedBackHandlerInputFileSchema(Schema):
    image_file = fields.Raw(type='file', required=True,
                            error_messages={
                                "required": {"message": 'Missing data for required field', "statusCode": 301}})

    @validates("image_file")
    def validate_File(self, file):
        if file and file.filename == '':
            raise ValidationError(
                {"Error": {"message": "Missing File name for required image_file", "statusCode": 302}})
        if not (allowed_file(file.filename)):
            raise ValidationError({"Error": {"message": "Unsupported File Type", "statusCode": 303}})


class FeedBackHandlerInputFormSchema(Schema):
    # the 'required' argument ensures the field exists
    corrected_disease = fields.String(required=True, error_messages={
        "required": {"message": 'Missing data for required field', "statusCode": 301}},
                                      validate=validate.OneOf(
                                          ["Brown spot", "None", "Bacterial leaf blight", "Leaf smut"]))


class Disease(Document):
    image_file_name = StringField(required=True, unique=True)
    date_time = DateTimeField(required=True)
    corrected_disease = StringField(required=True)
    image = FileField(required=True)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


image_classifier_input_schema = ImageClassifierInputSchema()
feed_back_handler_input_file_schema = FeedBackHandlerInputFileSchema()
feed_back_handler_input_form_schema = FeedBackHandlerInputFormSchema()


class ImageClassifier(Resource):

    def post(self):
        try:
            error = image_classifier_input_schema.validate(request.files)
        except ValidationError as err:
            return jsonify(err.message)
        if error:
            return jsonify(error)
        file = request.files['File']
        random_name = str(uuid.uuid4())
        file_name = secure_filename(random_name) + ".jpg"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        # prediction = rice_leaf_disease_detector.detect(image_path)
        os.remove(image_path)
        response = {
            "prediction": "Brown spot",  # prediction,
            "statusCode": 200
        }

        return jsonify(response)


class FeedBackHandler(Resource):

    def post(self):
        error = dict()
        try:
            file_error = feed_back_handler_input_file_schema.validate(request.files)
        except ValidationError as err:
            return jsonify(err.message)
        if file_error:
            error.update(file_error)
        form_error = feed_back_handler_input_form_schema.validate(request.form)
        if form_error:
            error.update(form_error)
        if error:
            return jsonify(error)
        image_file = request.files['image_file']
        random_name = str(uuid.uuid4())
        file_name = secure_filename(random_name) + ".jpg"
        image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        today_date_time = datetime.now()
        print(today_date_time)
        dis = Disease(**{"image_file_name": file_name, "date_time": today_date_time,
                         "corrected_disease": request.form['corrected_disease']})
        with open(image_path, 'rb') as fd:
            dis.image.put(fd, content_type='image/jpg')
        dis.save()
        fd.close()
        os.remove(image_path)
        response = {
            "msg": "FeedBack Stored",
            "statusCode": 200
        }
        return jsonify(response)


api.add_resource(ImageClassifier, "/Predict")
api.add_resource(FeedBackHandler, "/FeedBack")

if __name__ == '__main__':
    # host="127.0.0.1", port=80
    # debug=True
    app.run(port=int(os.environ.get("PORT", 8080)),host='0.0.0.0')
