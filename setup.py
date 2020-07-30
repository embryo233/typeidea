from setuptools import setup, find_packages


setup(
    name='typeidea',
    version='${version}',
    description='Blog System base on Django',
    author='author',
    author_email='example@gmail.com',
    url='https://www.example.com',
    license='MIT',
    #packages=find_packages('typeidea.typeidea','typeidea.extra_apps.xadmin'),

    #packages=find_packages('typeidea','extra_apps.xadmin'),

    packages=find_packages('typeidea'),
    package_dir={'': 'typeidea'},
    package_data={'': [    # 打包数据文件，方法一
        'themes/*/*/*/*',  # 需要按目录层级匹配
    ]},
    #include_package_data=True,  # 方法二 配合 MANIFEST.in文件
    install_requires=[
        'django~=3.0.8',
        'django-admin-tools',
        'gunicorn==20.0.4',
        'supervisor==4.0.2',

        #从19.0开始，dependency_links过时 从pip18.1开始可在install_requires放置这些依赖 使用pip install .而不是python setup.py install
        #'xadmin @ git+https://github.com/vip68/xadmin_bugfix@3084bb334c372600052dc901bfe76d8190d290dc'

        'mysqlclient==2.0.1',
        'django-ckeditor==5.9.0',
        'django-rest-framework==0.1.0',
        'django-autocomplete-light==3.5.1',
        'mistune==0.8.4',
        'Pillow==7.2.0',
        'coreapi==2.3.3',
        'django-redis==4.12.1',
        'hiredis==1.1.0',
        # debug
        'django-debug-toolbar==2.2',
        'djdt_flamegraph',
        'pympler',
        'django-debug-toolbar-line-profiler @ git+https://github.com/mikekeda/django-debug-toolbar-line-profiler@f967b13e259c92ce249676e864c5a5f5c7b7cb42',
        'django-silk==4.0.1',
    ],
    scripts=[
        'typeidea/manage.py',
        'typeidea/typeidea/wsgi.py',
    ],
    entry_points={
        'console_scripts': [
            'typeidea_manage = manage:main',
        ]
    },
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Blog :: Django Blog',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],

)
