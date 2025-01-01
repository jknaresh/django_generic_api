from setuptools import setup, find_packages

setup(
    name="django_generic_api",
    version="0.1.0a261",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description=(
        "A reusable Django app for generic CRUD operations based on "
        "dynamic payloads."
    ),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jknaresh/django_generic_api",
    author="Naresh Jonnala",
    author_email="ff.jonnala@gmail.com",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 4.0",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    install_requires=[
        "django==4.2.16",
        "djangorestframework==3.15.2",
        "pydantic==2.9.1",
        "email-validator==2.2.0",
        "djangorestframework-simplejwt==5.3.1",
        "jsonschema==4.23.0",
        "django-cors-headers==4.4.0",
        "pytest==8.3.3",
        "model-bakery==1.20.0",
        "pytest-django==4.9.0",
        "django-simple-captcha==0.6.0",
    ],
    setup_requires=[
        "pytest-runner",
    ],
    tests_require=["pytest"],
)
