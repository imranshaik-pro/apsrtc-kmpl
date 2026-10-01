from decimal import Decimal
import pytest
from src.reporting.vehicle_summary import get_slab, build_slab_operation_table
from src.calculations.pipeline import calculate_for_day, calculate_up_to_day

@pytest.mark.parametrize('value,label', [
    ('5.00','<=5.00'),('5.0001','5.01-5.10'),('5.005','5.01-5.10'),
    ('5.01','5.01-5.10'),('5.10','5.01-5.10'),('5.105','5.11-5.20'),
    ('5.11','5.11-5.20'),('5.20','5.11-5.20'),('5.205','5.21-5.30'),
    ('5.21','5.21-5.30'),('5.30','5.21-5.30'),('5.305','>5.30'),
    ('5.31','>5.30'),('1000000','>5.30'),
])
def test_boundaries_have_no_gaps(value,label):
    assert get_slab(Decimal(value)) == label

def test_source_to_table_counts_independent_day_and_upto():
    records=[]
    for i,value in enumerate(['4.99','5.005','5.105','5.205','5.305']):
        records.append({'vehicle_no':f'BUS{i}', 'operation_type':'OR',
            'for_day_total_kms':Decimal(value)*1000,'for_day_hsd':1000,
            'up_to_day_total_kms':Decimal('5.005')*1000,'up_to_day_hsd':1000})
    day=calculate_for_day(records); upto=calculate_up_to_day(records)
    _,counts,_=build_slab_operation_table(day,upto,records)
    labels=['<=5.00','5.01-5.10','5.11-5.20','5.21-5.30','>5.30']
    assert [counts[label]['for_day']['OR'] for label in labels] == [1,1,1,1,1]
    assert [counts[label]['up_to_day']['OR'] for label in labels] == [0,5,0,0,0]
    for group in ['for_day','up_to_day']:
        assert sum(counts[label][group]['OR'] for label in labels) == counts['Total'][group]['OR'] == 5
