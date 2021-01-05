from flowerfield import __version__
import setuptools

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
    name='flowerfield',
    version=__version__,
    author='Crystal Melting Dot',
    author_email='stresspassing@gmail.com',
    description='Tiny python module to automatically'
                'map dictionaries to python objects.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[],
    url='https://github.com/cmd410/flowerfield',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]
)
