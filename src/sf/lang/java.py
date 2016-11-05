from re import compile as recompile

from sf.lang import Lang, execute

class JavaLang(Lang):
    SOURCES_GLOB = '*.java'
    MAIN_SOURCE_RE = recompile(r'public\s+static\s+void\s+main')
    def __init__(self, path):
        super(JavaLang, self).__init__(path)
        self.main_class = self.main_source.split('.')[0]
    def compile(self):
        return execute(['javac'] + self.sources)
    def run(self, args = None):
        return execute(['java', self.main_class] + args)
