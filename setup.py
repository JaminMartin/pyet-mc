from setuptools import setup, find_packages

setup(
    name='pyet',
    version='0.1',
    description='A short description of your package',
    url='https://github.com/your_username/pyet',
    author='Jamin Martin',
    author_email='your_email@example.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'numpy',
        'pandas',
    ],
    include_package_data=True,
)