from gettext import GNUTranslations, NullTranslations
from io import BytesIO
from locale import getdefaultlocale
from os.path import isdir, join, dirname
from zipfile import ZipFile

PACKAGE_PATH = dirname(dirname( __file__ ))

def translation(lang):
	try:
		with ZipFile(PACKAGE_PATH) as f:
			mo = f.read('sf/mos/{0}.mo'.format(lang))
	except KeyError:
		return NullTranslations()
	else:
		return GNUTranslations(BytesIO(mo))

DEFAULT_GETTEXT = translation(getdefaultlocale()[0][:2]).gettext
