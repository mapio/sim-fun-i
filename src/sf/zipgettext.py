from gettext import GNUTranslations, NullTranslations
from io import BytesIO
from locale import getdefaultlocale
from os.path import dirname
from zipfile import ZipFile

PACKAGE_PATH = dirname(dirname( __file__ ))

def translation(lang):
	if lang is None: return NullTranslations()
	try:
		with ZipFile(PACKAGE_PATH) as f:
			mo = f.read('sf/mos/{0}.mo'.format(lang))
	except KeyError:
		return NullTranslations()
	else:
		return GNUTranslations(BytesIO(mo))

try:
	lang = getdefaultlocale()[0][:2]
except:
	lang = None

DEFAULT_GETTEXT = translation(lang).gettext
