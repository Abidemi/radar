import random
from datetime import date

from radar.models.aki_process_measures import AkiProcessMeasures, PROCESS_MEASURES
from radar_fixtures.utils import random_date, add


def create_aki_process_measures_f():
    def create_aki_process_measures(patient, source_group, source_type, n):
        for _ in range(n):
            apm = AkiProcessMeasures()
            apm.patient = patient
            apm.source_group = source_group
            apm.source_type = source_type
            apm.date = random_date(patient.earliest_date_of_birth, date.today())

            for process_measure in PROCESS_MEASURES:
                value = random.randint(0, 2)

                if value == 0:
                    value = False
                elif value == 1:
                    value = True
                elif value == 2:
                    value = None

                setattr(apm, process_measure, value)

            add(apm)

    return create_aki_process_measures
