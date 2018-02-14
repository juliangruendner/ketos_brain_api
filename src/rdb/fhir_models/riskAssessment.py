fhir__base_risk_assessment = {
    "resourceType":"RiskAssessment",
    "subject":{
        "reference":"Patient/1"
    },
    "date":"2009-01-18T00:00:00+00:00",
    "condition":{
        "reference":"Measurement/700000008"
    },
    "method": {
        "coding": [
            {
            "system": "KETOS",
            "code": "ketos_ml_method"
        }]
    }
}

fhir_base_patient_prediction = {
    "outcome":{
        "coding":[
        {
            "system":"KETOS",
            "code":"chem_therapy_resp_yes"
        }
        ]
    },
    "probabilityDecimal":0.00,
    "whenPeriod":{
        "start":"2009-01-18T00:00:00+00:00",
        "end":"2009-01-18T00:00:00+00:00"
    },
    "rationale":"ketos_prediction"
}