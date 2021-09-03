import setuptools


def get_version(module_path):
    match = next(line for line in open(module_path) if line.startswith('__version__'))
    _, version, _ = match.replace('"',"'").split("'")
    return version


setuptools.setup(
    name='flowdock-api-wrapper',
    url='https://github.com/apua/flowdock',
    version=get_version('flowdock.py'),
    description='Flowdock API Wrapper',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    keywords='flowdock',
    install_requires=['requests'],
    py_modules=['flowdock'],
    python_requires='>=3.6',
    classifiers=[
        #'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        #'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Communications :: Chat',
        'Topic :: Communications :: Conferencing',
        'License :: OSI Approved :: MIT License',
    ],
)
