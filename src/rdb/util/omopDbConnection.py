import psycopg2
import config


connection = None
try:
    connection = psycopg2.connect(host=config.OMOP_ON_FHIR_HOST,
                                  database=config.OMOP_ON_FHIR_POSTGRES_DB,
                                  user=config.OMOP_ON_FHIR_POSTGRES_USER,
                                  password=config.OMOP_ON_FHIR_POSTGRES_PASSWORD,
                                  connect_timeout=3)
except psycopg2.OperationalError:
    pass


def get_patient_ids_for_atlas_cohort(cohort_id):
    if not connection:
        return list()

    cursor = connection.cursor()
    statement = 'SELECT subject_id FROM ohdsi.cohort WHERE cohort_definition_id = %s ORDER BY subject_id ASC'
    cursor.execute(statement, (cohort_id,))

    ret = list()
    while True:
        next_id = cursor.fetchone()
        if not next_id:
            break
        ret.append(next_id[0])

    return ret
