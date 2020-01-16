from operator import itemgetter
from json import loads

from sf import deread
from tm.mkresults import TristoMietitoreScanner

class Scanner(TristoMietitoreScanner):

    SHORT_NAME = 'sf'
    SOURCE_PATTERN = r'(?P<uid>.*)/latest/(?P<exercise>.+)/(?P<source>.*\.(c|h|java|sh))$'
    CASES_PATTERN = r'(?P<uid>.*)/latest/TEST-(?P<exercise>.+)\.(?P<case>json)$'

    def cases_reader(self, path):
        return loads(deread(path))

    def sort(self):
        for res in self.results:
            res['exercises'].sort(key = itemgetter('name'))
            for exercise in res['exercises']:
                if exercise['cases']:
                    first = exercise['cases'].pop( 0 )
                    exercise['cases'].sort( key = itemgetter('name'))
                    exercise['cases'].insert( 0, first )
                exercise['sources'].sort( key = itemgetter('name'))
        self.results.sort(key = lambda _: _['signature']['uid'])
        return self
