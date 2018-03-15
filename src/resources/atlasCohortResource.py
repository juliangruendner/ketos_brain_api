from flask_restful_swagger_2 import swagger, Resource
import rdb.util.omopDbConnection as OmopDbConnection
import flask
from flask_restplus import inputs
from flask_restful import reqparse
from resources.userResource import auth


class AtlasCohortResource(Resource):
    def __init__(self):
        super(AtlasCohortResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('download', type=inputs.boolean, default=False, required=False, location='args')

    @auth.login_required
    @swagger.doc({
        "summary": "Returns Atlas cohort with its patient IDs",
        "tags": ["atlas cohorts"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns Atlas cohort with its patient IDs',
        "responses": {
            "200": {
                "description": "Returns Atlas cohort ID and list with included patient IDs"
            }
        },
        "parameters": [
            {
                "name": "cohort_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the atlas cohort",
                "required": True
            },
            {
                "name": "download",
                "in": "query",
                "type": "boolean",
                "description": "flag whether to download result as json file",
                "required": False
            }
        ],
    })
    def get(self, cohort_id):
        patient_ids = OmopDbConnection.get_patient_ids_for_atlas_cohort(cohort_id)
        response = flask.make_response(flask.jsonify({'cohort_id': cohort_id, 'patient_ids': patient_ids}))
        response.headers['content-type'] = 'application/json'

        args = self.parser.parse_args()
        if args['download']:
            filename = 'atlas_cohort_' + str(cohort_id) + '_patients.json'
            response.headers['Content-Disposition'] = "attachment; filename=" + filename

        return response
