import setuptools
from fb2latex import __version__

setuptools.setup(
    name='fb2latex',
    version=__version__,
    url='https://github.com/jenda1/fb2latex',
    author='Jan Lana',
    author_email='lana.jan@gmail.com',
    description='Convert FB2 to LaTeX.',
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=[
        'lxml',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'fb2latex = fb2latex.__main__:main',
        ],
    },
)
