from typing import Union
from rapidfuzz import fuzz
from years import Years

class Event:
    SIMILARITY_THRESHOLD = 90

    def __init__(self, props):
        self.category = props['category']
        self.name = props['name'].strip()
        self.year = props['year']
        self.description = props['description']

    def __repr__(self) -> str:
        return f'{self.name} ({self.year})'

    def __eq__(self, value: Union['Event', None]) -> bool:
        # Check only if the _compared_ value is None.
        # `self` is an instance, therefore it's not None.
        if value is None:
            return False
        
        name_similarity = fuzz.ratio(self.name, value.name)
        # TODO: use a type that can be compared for `year`:
        year_similarity = self.calculate_years_similarity(self.year, value.year)
        overall_similarity = (name_similarity * 0.7) + (year_similarity * 0.3)

        return overall_similarity >= 90
    
    def calculate_years_similarity(self, year1, year2) -> int:
        y1 = Years(year1)
        y2 = Years(year2)

        if y1 == y2: # Yup. Even if those are None.
            return 100

        if y1 is None or y2 is None:
            return 0
        
        if abs(y1 - y2) <= 2: # allow a difference of 2 years
            return self.SIMILARITY_THRESHOLD # less similar because the == is already done earlier
        
        return 0 # We covered all the potential cases. By this point it's NOT similar.
