import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='q26_quanTrader',  
     version='0.1.1',
     packages=setuptools.find_packages(exclude=['tests*']),
     #install_requires=['numpy', 'pandas', 'matplotlib', 'importlib'],
     author="Loann Brahimi",
     author_email="loann.brahimi@data-sciences.io",
     description="A python package for live trading",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/LoannData/Q26_QuanTrader.git",
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     python_requires=">=3.6",
 )