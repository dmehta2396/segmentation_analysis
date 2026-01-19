"""Setup script for segmentation analysis package."""

from setuptools import setup, find_packages

setup(
    name='segmentation_analysis',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'pandas>=2.1.4',
        'numpy>=1.26.2',
        'plotly>=5.18.0',
        'dash>=2.14.2',
        'dash-bootstrap-components>=1.5.0',
        'openpyxl>=3.1.2',
        'python-dotenv>=1.0.0',
    ],
    python_requires='>=3.8',
)