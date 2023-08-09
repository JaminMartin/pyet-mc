from setuptools import setup, find_packages
from pip._internal.req import parse_requirements

# Parse the requirements file and generate a list of package dependencies
requirements = parse_requirements('requirements.txt', session=False)
install_requires = [str(req.requirement) for req in requirements]

setup(
    name='pyet',
    version='0.1',
    description='A short description of your package',
    url='https://github.com/your_username/pyet',
    author='Jamin Martin',
    author_email='your_email@example.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=install_requires,
    include_package_data=True,
)