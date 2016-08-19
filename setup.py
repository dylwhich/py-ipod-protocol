from setuptools import setup, find_packages

def read_license():
    with open("LICENSE") as f:
        return f.read()

setup(
    name='ipodproto',
    packages=find_packages(),
    version='0.1',
    description='iPod accessory protocol library',
    long_description="""A library which can be used both for implementing iPod accessories
and for emulating an iPod to communicate with existing accessories.""",    
    license=read_license(),
    author='Dylan Whichard',
    author_email='dylan@whichard.com',
    url='https://github.com/dylwhich/py-ipod-protocol',
    keywords=[
        'ipod'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=open('requirements.txt').readlines(),
)
