from core_algorithms_index_inverted import create_attribute_index
from datetime import datetime

index_name = "dates"
attribute_regex = "Dátum vydania rozhodnutia:\n(([0-2][0-9]|3[0-1])\. ?(0[0-9]|1[0-2])\. ?[0-9]{4})"

create_attribute_index(index_name, attribute_regex,
                       sort_lambda=lambda date: datetime.strptime(date.split(':')[0], '%d. %m. %Y'),
                       reverse_order=True
                       )
