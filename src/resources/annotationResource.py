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
    @swagger.doc({
        "summary": "Returns all existing annotation tasks",
        "tags": ["annotation tasks"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all existing annotation tasks',
        "responses": {
            "200": {
                "description": "Returns the list of annotation tasks"
            }
        }
    })
    def get(self):
        return handle_request(request)

    @auth.login_required
    @swagger.doc({
        "summary": "Create annotation task",
        "tags": ["annotation tasks"],
        "produces": [
            "application/json"
        ],
        "description": 'Create annotation task',
        "responses": {
            "200": {
                "description": "Success: Returns newly created annotation task"
            },
            "404": {
                "description": "Not found error when crawler job doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "number_of_annotators",
                "in": "query",
                "type": "integer",
                "description": "Number of annotators for the current task",
                "required": True
            },
            {
                "name": "annotation_task",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "crawler_job_id": {
                            "type": "string"
                        },
                        "creator_id": {
                            "type": "integer"
                        },
                        "name": {
                            "type": "string"
                        },
                        "anno_type": {
                            "type": "integer"
                        }
                    }
                }
            }
        ],
    })
    def post(self):
        json_data = request.get_json()
        json_data["creator_id"] = g.user.id
        return handle_request(request)


class AnnotationTaskResource(Resource):
    def __init__(self):
        super(AnnotationTaskResource, self).__init__()

    @auth.login_required
    @swagger.doc({
        "summary": "Returns a specific annotation task",
        "tags": ["annotation tasks"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns the annotation task for the given ID',
        "responses": {
            "200": {
                "description": "Returns the annotation task with the given ID"
            },
            "404": {
                "description": "Not found error when annotation task doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "task_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the annotation task",
                "required": True
            }
        ],
    })
    def get(self, task_id):
        return handle_request(request)

    @auth.login_required
    @swagger.doc({
        "summary": "Update annotation task",
        "tags": ["annotation tasks"],
        "produces": [
            "application/json"
        ],
        "description": 'Update annotation task',
        "responses": {
            "200": {
                "description": "Success: Newly updated annotation task is returned"
            },
            "404": {
                "description": "Not found error when annotation task doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "task_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the annotation task",
                "required": True
            },
            {
                "name": "annotation_task",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "crawler_job_id": {
                            "type": "string"
                        },
                        "name": {
                            "type": "string"
                        },
                        "anno_type": {
                            "type": "integer"
                        }
                    }
                }
            }
        ],
    })
    def put(self, task_id):
        return handle_request(request)

    @auth.login_required
    @swagger.doc({
        "summary": "Deletes a specific annotation task",
        "tags": ["annotation tasks"],
        "produces": [
            "application/json"
        ],
        "description": 'Delete the annotation task for the given ID',
        "responses": {
            "200": {
                "description": "Success: Returns the given ID"
            },
            "404": {
                "description": "Not found error when annotation task doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "task_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the annotation task",
                "required": True
            }
        ],
    })
    def delete(self, task_id):
        return handle_request(request)


class UserAnnotationTaskListResource(Resource):
    def __init__(self):
        super(UserAnnotationTaskListResource, self).__init__()

    @swagger.doc({
        "summary": "Get all annotation tasks for user",
        "tags": ["annotation tasks"],
        "produces": [
            "application/json"
        ],
        "description": 'Get all annotation tasks for user',
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the user",
                "required": True
            }
        ],
        "responses": {
            "200": {
                "description": "annotation tasks"
            }
        }
    })
    def get(self, user_id):
        return handle_request(request)


class AnnotationTaskEntryListResource(Resource):
    def __init__(self):
        super(AnnotationTaskEntryListResource, self).__init__()

    @swagger.doc({
        "summary": "Returns all entries for specific annotation task",
        "tags": ["annotation entries"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all entries for specific annotation task',
        "responses": {
            "200": {
                "description": "Returns all entries for specific annotation task"
            }
        },
        "parameters": [
            {
                "name": "task_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the annotation task",
                "required": True
            }
        ],
    })
    def get(self, task_id):
        return handle_request(request)


class AnnotationTaskScaleEntryListResource(Resource):
    def __init__(self):
        super(AnnotationTaskScaleEntryListResource, self).__init__()

    @swagger.doc({
        "summary": "Returns all scale entries for annotation task",
        "tags": ["annotation task scale entries"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all scale entries for annotation task',
        "responses": {
            "200": {
                "description": "Returns all scale entries for annotation task"
            }
        },
        "parameters": [
            {
                "name": "task_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the annotation task",
                "required": True
            }
        ],
    })
    def get(self, task_id):
        return handle_request(request)

    @swagger.doc({
        "summary": "Create scale entry for annotation task",
        "tags": ["annotation task scale entries"],
        "produces": [
            "application/json"
        ],
        "description": 'Create scale entry for annotation task',
        "responses": {
            "200": {
                "description": "Success: Returns newly created scale entry"
            }
        },
        "parameters": [
            {
                "name": "task_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the annotation task",
                "required": True
            },
            {
                "name": "scale_entry",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "code": {
                            "type": "string"
                        }
                    }
                }
            }
        ],
    })
    def post(self, task_id):
        return handle_request(request)


class AnnotationTaskAnnotatorListResource(Resource):
    def __init__(self):
        super(AnnotationTaskAnnotatorListResource, self).__init__()

    @swagger.doc({
        "summary": "Returns all annotators a annotation task",
        "tags": ["annotators"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all annotators a annotation task',
        "responses": {
            "200": {
                "description": "Returns the list of annotation tasks for a user"
            }
        },
        "parameters": [
            {
                "name": "task_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the annotation task",
                "required": True
            }
        ],
    })
    def get(self, task_id):
        return handle_request(request)

    @swagger.doc({
        "summary": "Create annotator",
        "tags": ["annotators"],
        "produces": [
            "application/json"
        ],
        "description": 'Create annotator',
        "responses": {
            "200": {
                "description": "Success: Returns newly created annotator"
            },
            "404": {
                "description": "Not found error when annotation task doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "annotator",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        }
                    }
                }
            }
        ],
    })
    def post(self, task_id):
        return handle_request(request)


class AnnotationResultListResource(Resource):
    def __init__(self):
        super(AnnotationResultListResource, self).__init__()

    @swagger.doc({
        "summary": "Returns all existing annotation results",
        "tags": ["annotation results"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all existing annotation results',
        "responses": {
            "200": {
                "description": "Returns the list of annotation results"
            }
        }
    })
    def get(self):
        return handle_request(request)

    @swagger.doc({
        "summary": "Create annotation result",
        "tags": ["annotation results"],
        "produces": [
            "application/json"
        ],
        "description": 'Create annotation result',
        "responses": {
            "200": {
                "description": "Success: Returns newly created annotation result"
            }
        },
        "parameters": [
            {
                "name": "annotation_result",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "scale_entry_id": {
                            "type": "integer"
                        },
                        "annotator_id": {
                            "type": "integer"
                        },
                        "entry_id": {
                            "type": "integer"
                        }
                    }
                }
            }
        ],
    })
    def post(self):
        return handle_request(request)


class AnnotatorResultListResource(Resource):
    def __init__(self):
        super(AnnotatorResultListResource, self).__init__()

    @swagger.doc({
        "summary": "Returns all annotation results for a specific annotator",
        "tags": ["annotation results"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all annotation results for a specific annotator',
        "responses": {
            "200": {
                "description": "Returns the list of annotation results for a annotator"
            }
        },
        "parameters": [
            {
                "name": "annotator_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the annotator",
                "required": True
            }
        ],
    })
    def get(self, annotator_id):
        return handle_request(request)


class AnnotationTaskResultListResource(Resource):
    def __init__(self):
        super(AnnotationTaskResultListResource, self).__init__()

    @swagger.doc({
        "summary": "Returns all annotation results for a specific annotation task",
        "tags": ["annotation results"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all annotation results for a specific annotation task',
        "responses": {
            "200": {
                "description": "Returns the list of annotation results for a annotation task"
            }
        },
        "parameters": [
            {
                "name": "task_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the annotation task",
                "required": True
            }
        ],
    })
    def get(self, task_id):
        return handle_request(request)

    def post(self, task_id):
        return handle_request(request)


class EntriesForAnnotatorResource(Resource):
    def __init__(self):
        super(EntriesForAnnotatorResource, self).__init__()

    @swagger.doc({
        "summary": "Returns all entries for annotator token",
        "tags": ["annotation entries"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all entries for annotator token',
        "responses": {
            "200": {
                "description": "Returns all entries for annotator token"
            }
        },
        "parameters": [
            {
                "name": "token",
                "in": "path",
                "type": "string",
                "description": "token of an annotator",
                "required": True
            }
        ],
    })
    def get(self, token):
        return handle_request(request)


class AnnotatorResource(Resource):
    def __init__(self):
        super(AnnotatorResource, self).__init__()

    @swagger.doc({
        "summary": "Returns the annotator for a token",
        "tags": ["annotators"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns the annotator for a token',
        "responses": {
            "200": {
                "description": "Returns the annotator for a token"
            }
        },
        "parameters": [
            {
                "name": "token",
                "in": "path",
                "type": "string",
                "description": "token of an annotator",
                "required": True
            }
        ],
    })
    def get(self, token):
        return handle_request(request)


class AnnotationTaskScaleEntry(Resource):
    def __init__(self):
        super(AnnotationTaskScaleEntry, self).__init__()

    @swagger.doc({
        "summary": "Returns specific scale entry for annotation task",
        "tags": ["annotation task scale entries"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns specific scale entry for annotation task',
        "responses": {
            "200": {
                "description": "Returns specific scale entry for annotation task"
            }
        },
        "parameters": [
            {
                "name": "task_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the annotation task",
                "required": True
            },
            {
                "name": "scale_entry_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the scale entry",
                "required": True
            }
        ],
    })
    def get(self, task_id, scale_entry_id):
        return handle_request(request)

    @swagger.doc({
        "summary": "Update scale entry for annotation task",
        "tags": ["annotation task scale entries"],
        "produces": [
            "application/json"
        ],
        "description": 'Update scale entry for annotation task',
        "responses": {
            "200": {
                "description": "Success: Returns newly updated scale entry"
            }
        },
        "parameters": [
            {
                "name": "task_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the annotation task",
                "required": True
            },
            {
                "name": "scale_entry_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the scale entry",
                "required": True
            },
            {
                "name": "scale_entry",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "code": {
                            "type": "string"
                        }
                    }
                }
            }
        ],
    })
    def put(self, task_id, scale_entry_id):
        return handle_request(request)

    @swagger.doc({
        "summary": "Delete specific scale entry for annotation task",
        "tags": ["annotation task scale entries"],
        "produces": [
            "application/json"
        ],
        "description": 'Delete specific scale entry for annotation task',
        "responses": {
            "200": {
                "description": "Returns the given scale entry ID"
            }
        },
        "parameters": [
            {
                "name": "task_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the annotation task",
                "required": True
            },
            {
                "name": "scale_entry_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the scale entry",
                "required": True
            }
        ],
    })
    def delete(self, task_id, scale_entry_id):
        return handle_request(request)
