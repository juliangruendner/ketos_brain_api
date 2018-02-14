from flask_restful import reqparse, fields, marshal_with
from flask_restful_swagger_2 import swagger, Resource
import rdb.models.predictionOutcome as PredictionOutcome
from rdb.models.id import ID, id_fields
from resources.userResource import auth

pred_outcome_fields = {
    'id': fields.Integer,
    'model_id': fields.Integer,
    'outcome_codesystem': fields.String,
    'outcome_code': fields.String,
    'outcome_value': fields.String,
}


class PredictionOutcomeListResource(Resource):
    def __init__(self):
        super(PredictionOutcomeListResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('model_id', type=int, required=True, help='No model id provided', location='json')
        self.parser.add_argument('outcome_codesystem', type=str, required=False, location='json')
        self.parser.add_argument('outcome_code', type=str, required=True, help='No outcome code provided', location='json')
        self.parser.add_argument('outcome_value', type=str, required=True, help='No outcome value provided', location='json')

    @auth.login_required
    @marshal_with(pred_outcome_fields)
    def get(self):
        return PredictionOutcome.get_all(), 200

    @auth.login_required
    @marshal_with(pred_outcome_fields)
    def post(self):
        args = self.parser.parse_args()

        if args['outcome_codesystem']:
            p_o = PredictionOutcome.create(args['model_id'], args['outcome_code'], args['outcome_value'], args['outcome_codesystem'])
        else:
            p_o = PredictionOutcome.create(args['model_id'], args['outcome_code'], args['outcome_value'])

        return p_o, 201


class PredictionOutcomeResource(Resource):
    def __init__(self):
        super(PredictionOutcomeResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('model_id', type=int, required=True, help='No model id provided', location='json')
        self.parser.add_argument('outcome_codesystem', type=str, required=False, location='json')
        self.parser.add_argument('outcome_code', type=str, required=True, help='No outcome code provided', location='json')
        self.parser.add_argument('outcome_value', type=str, required=True, help='No outcome value provided', location='json')

    @auth.login_required
    @marshal_with(pred_outcome_fields)
    def get(self, pred_outcome_id):
        return PredictionOutcome.get(pred_outcome_id), 200

    @auth.login_required
    @marshal_with(pred_outcome_fields)
    def put(self, pred_outcome_id):
        args = self.parser.parse_args()
        p_o = PredictionOutcome.update(pred_outcome_id=pred_outcome_id, outcome_codesystem=args['outcome_codesystem'],
                                       outcome_code=args['outcome_code'], outcome_value=args['outcome_value'])
        return p_o, 200

    @auth.login_required
    @marshal_with(id_fields)
    def delete(self, pred_outcome_id):
        id = ID()
        id.id = PredictionOutcome.delete(pred_outcome_id)

        return id, 200


class ModelPredictionOutcomeListResource(Resource):
    def __init__(self):
        super(ModelPredictionOutcomeListResource, self).__init__()

    @auth.login_required
    @marshal_with(pred_outcome_fields)
    def get(self, model_id):
        return PredictionOutcome.get_all_for_model(model_id), 200
