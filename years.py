import re
from typing import Union

class Years:
    def __init__(self, year: Union[int, str]):
        self.year = year

    def __int__(self):
        if type(self.year) == type('') and type(re.match(r'\D', self.year)):
            return int(re.split(r'\D', self.year)[0])
        return int(self.year)

    # Less or Equal than...
    def __le__(self, other_year):
        return self.year <= other_year.year

    def __sub__(self, other_year):       
        return int(self) - int(other_year)
