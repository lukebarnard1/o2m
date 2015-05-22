from setuptools import setup, find_packages
setup(
	name = "O2M",
	version = "0.2.0",
	install_requires = ["django==1.8.1", "django-bootstrap3==5.4.0", "django-mptt==0.7.3", "django-mptt-admin==0.2.1"],
	scripts = ['o2m/o2m/run_o2m.py'],
	packages = ['o2m', 'static'],
    package_dir = {'':'o2m'},   # tell distutils packages are under src
    include_package_data=True,
	package_data = {
		'': ['*.html', '*.js', '*.css', '*.py'],
	},
	data_files = [
		# ('/var/o2m',['o2m/db.sqlite3']),
		# ('/var/o2m/social',[])
		# ('',['LICENSE']),
	],

	# metadata for upload to PyPI
	author = "Luke Barnard",
	author_email = "luke.barnard99@gmail.com",
	description = "One to Many - The Fully Distributed Secure Social Network",
	license = "GNU GENERAL PUBLIC LICENSE v2",
	keywords = "social network distributed",
	url = "https://github.com/lukebarnard1/o2m",
)