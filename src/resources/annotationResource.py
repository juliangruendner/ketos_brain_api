from flask_restful_swagger_2 import swagger, Resource
from rdb.models.user import auth
from resources.adminAccess import AdminAccess
from flask import request
import requests
import config
from flask import g


def get_anno_api_url(req):
    return 'http://' + config.ANNOTATION_API_HOST + req.path


def do_anno_api_request(req):
    anno_api_url = get_anno_api_url(req)
    resp = requests.request(method=req.method, url=anno_api_url, params=req.args, json=req.get_json())
    return resp


def handle_request(req):
    resp = do_anno_api_request(request)
    return resp.json(), resp.status_code


class AnnotationTaskListResource(Resource):
    def __init__(self):
        super(AnnotationTaskListResource, self).__init__()

    @auth.login_required
    @AdminAccess()
    def get(self):
        return handle_request(request)

    @auth.login_required
    def post(self):
        json_data = request.get_json()
        json_data["creator_id"] = g.user.id
        return handle_request(request)


class AnnotationTaskResource(Resource):
    def __init__(self):
        super(AnnotationTaskResource, self).__init__()

    @auth.login_required
    def get(self, task_id):
        return handle_request(request)

    @auth.login_required
    def put(self, task_id):
        return handle_request(request)

    @auth.login_required
    def delete(self, task_id):
        return handle_request(request)


class UserAnnotationTaskListResource(Resource):
    def __init__(self):
        super(UserAnnotationTaskListResource, self).__init__()

    def get(self, user_id):
        return handle_request(request)


class AnnotationTaskEntryListResource(Resource):
    def __init__(self):
        super(AnnotationTaskEntryListResource, self).__init__()

    def get(self, task_id):
        return handle_request(request)


class AnnotationTaskScaleEntryListResource(Resource):
    def __init__(self):
        super(AnnotationTaskScaleEntryListResource, self).__init__()

    def get(self, task_id):
        return handle_request(request)

    def post(self, task_id):
        return handle_request(request)


class AnnotationTaskAnnotatorListResource(Resource):
    def __init__(self):
        super(AnnotationTaskAnnotatorListResource, self).__init__()

    def get(self, task_id):
        return handle_request(request)

    def post(self, task_id):
        return handle_request(request)


class AnnotationResultListResource(Resource):
    def __init__(self):
        super(AnnotationTaskResultListResource, self).__init__()

    def get(self, task_id):
        return handle_request(request)

    def post(self):
        return handle_request(request)


class AnnotatorResultListResource(Resource):
    def __init__(self):
        super(AnnotatorResultListResource, self).__init__()

    def get(self, annotator_id):
        return handle_request(request)


class AnnotationTaskResultListResource(Resource):
    def __init__(self):
        super(AnnotationTaskResultListResource, self).__init__()

    def get(self, task_id):
        return handle_request(request)


class EntriesForAnnotatorResource(Resource):
    def __init__(self):
        super(EntriesForAnnotatorResource, self).__init__()

    def get(self, token):
        return handle_request(request)
