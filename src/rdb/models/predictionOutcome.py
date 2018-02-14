from rdb.rdb import db
from flask_restful import abort


class PredictionOutcome(db.Model):
    """PredictionOutcome Class"""

    __tablename__ = "prediction_outcome"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('ml_model.id'), nullable=False)
    outcome_codesystem = db.Column(db.Text, nullable=False)
    outcome_code = db.Column(db.Text, nullable=False)
    outcome_value = db.Column(db.Text, nullable=False)

    def __init__(self):
        super(PredictionOutcome, self).__init__()

    def __repr__(self):
        """Display when printing a prediction outcome object"""

        return "<ID: {}, model id: {}, outcome code: {} outcome value: {}>".format(self.id, self.model_id, self.outcome_code, self.outcome_value)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def create(model_id, outcome_code, outcome_value, outcome_codesystem='KETOS'):
    p_o = PredictionOutcome()
    p_o.model_id = model_id
    p_o.outcome_code = outcome_code
    p_o.outcome_value = outcome_value
    p_o.outcome_codesystem = outcome_codesystem

    db.session.add(p_o)
    db.session.commit()
    return p_o


def abort_if_prediction_outcome_doesnt_exist(outcome_id):
        abort(404, message="prediction outcome {} doesn't exist".format(outcome_id))


def get(prediction_outcome_id, raise_abort=True):
    p_o = PredictionOutcome.query.get(prediction_outcome_id)

    if raise_abort and not p_o:
        abort_if_prediction_outcome_doesnt_exist(prediction_outcome_id)

    return p_o


def get_all():
    return PredictionOutcome.query.all()


def get_all_for_model(model_id):
    return PredictionOutcome.query.filter_by(model_id=model_id).all()

def update(pred_outcome_id, outcome_codesystem, outcome_code, outcome_value, raise_abort=True):
    p_o = get(pred_outcome_id, raise_abort=raise_abort)

    if outcome_codesystem:
        p_o.outcome_codesystem = outcome_codesystem
    
    if outcome_code:
        p_o.outcome_code = outcome_code

    if outcome_value:
        p_o.outcome_value = outcome_value

    db.session.commit()
    return p_o


def delete(pred_outcome_id, raise_abort=True):
    p_o = get(pred_outcome_id, raise_abort=raise_abort)

    db.session.delete(p_o)
    db.session.commit()
    return pred_outcome_id
