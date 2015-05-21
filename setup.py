from setuptools import setup, find_packages
setup(
    name = "O2M",
    version = "0.2.0",
    packages = find_packages(),

    package_data = {
        '': ['*.db.sqlite3', '*.html'],
    },

    # metadata for upload to PyPI
    author = "Luke Barnard",
    author_email = "luke.barnard99@gmail.com",
    description = "One to Many - The Fully Distributed Secure Social Network",
    license = "GNU GENERAL PUBLIC LICENSE v2",
    keywords = "social network distributed",
    url = "https://github.com/lukebarnard1/o2m",
)