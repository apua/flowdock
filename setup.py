"""
1.  Refer to PyPA tutorial -- `Packaging Python Projects`_, we leverage ``twine`` here.

2.  Verions is defined in both ``git tag`` and ``README.rst``, not source code.

3.  Test uploading to PyPI with TestPyPI first.

    .. code:: sh

        # in flowdock source code
        $ rm -r dist ; python setup.py sdist bdist_wheel
        $ twine check dist/*.whl
        $ twine upload --user=${user} --password=${password} --repository-url https://test.pypi.org/legacy/ 'dist/*'

    .. WARNING:: MUST avoid version collision, which is no way to solve even deleting it on PyPI/TestPyPI.

.. _`packaging python projects`: https://packaging.python.org/tutorials/packaging-projects/
"""


import setuptools

lines = open('README.rst', 'r').readlines()
description = (lines[1] if lines[0] == lines[2] else lines[0]).strip()
for ln, line in enumerate(lines):
    line_ = line.strip().lower()
    if line_.startswith(':version:'):
        version = line_.split(':version:', 1)[1].strip()
        break
else:
    raise Exception('parse error, cannot find version number from README')
long_description = ''.join(lines[ln+1:])

print(f'⭐version: {version}⭐')
print(f'⭐description: {description}⭐')

setuptools.setup(
    name='flowdock-api-wrapper',
    version=version,
    description=description,
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/apua/flowdock',
    keywords='flowdock',
    install_requires=['requests'],
    py_modules=['flowdock'],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
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
