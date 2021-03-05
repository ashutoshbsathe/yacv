from setuptools import *

LONG_DESC = """
yacv: Yet Another Compiler Visualizer - Tool which lets you visualize LL(1) and LR parsing process using `manim`
"""

setup(name='yacv',
      version='0.0.1',
      description='Yet Another Compiler Visualizer',
      long_description=LONG_DESC,
      author='Ashutosh Sathe',
      author_email='2ashutoshbs@gmail.com',
      url='https://github.com/ashutoshbsathe/yacv',
      install_requires=['pandas', 'pygraphviz', 'manim'],
      license='MIT',
      packages=find_packages(),
      entry_points={
        'console_scripts': [
            'yacv = yacv.__main__:main',
        ]
      },
      zip_safe=False)

