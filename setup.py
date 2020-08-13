from setuptools import setup

setup(
	name = 'hotel',
	version = '1.0',
	py_modules = ['hotel'],
	install_requires = [
		'Click',
	],
	entry_points = '''
		[console_scripts]
		hotel=hotel:cli
	''',
)