from setuptools import setup, find_packages

from os.path import expanduser
home = expanduser("~")

setup(
	name = "O2M",
	version = "0.2.0",
	install_requires = ["django==1.8.1", "django-bootstrap3==5.4.0", "django-mptt==0.7.3", "django-mptt-admin==0.2.1", "httplib2==0.18.0", "django-ipware==1.0.0"],
	scripts = ['o2m/run_o2m.py'],
	packages = ['o2m', 'static'],
    package_dir = {'':'o2m'},   # tell distutils packages are under src
    include_package_data=True,
	package_data = {
		'': ['*.html', '*.js', '*.css', '*.py'],
	},
	data_files = [
		('%s/o2m' % home,['o2m/db.sqlite3']),
		('%s/o2m/content' % home,[])
		# ('',['LICENSE']),
	],
	test_suite = 'o2m.tests',

	# metadata for upload to PyPI
	author = "Luke Barnard",
	author_email = "luke.barnard99@gmail.com",
	description = "One to Many - The Fully Distributed Secure Social Network",
	license = "GNU GENERAL PUBLIC LICENSE v2",
	keywords = "social network distributed",
	url = "https://github.com/lukebarnard1/o2m",
)