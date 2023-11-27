from setuptools import setup, find_packages
from pip._internal.req import parse_requirements

# Parse the requirements file and generate a list of package dependencies
requirements = parse_requirements('requirements.txt', session=False)
install_requires = [str(req.requirement) for req in requirements]

setup(
    name='pyet',
    version='0.1',
    description='Python package for calculating energy transfer rates between lanthanide ions',
    url='https://github.com/JaminMartin/pyet-mc',
    author='Jamin Martin',
    author_email='jamin.martin@pg.canterbury.ac.nz',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=install_requires,
    package_data={'': ['plotting_config/*']},  
    include_package_data=True,
)