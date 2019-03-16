Jinja2 Templates with bareASGI
==============================

`Jinja2 <http://jinja.pocoo.org>`_ template support for `bareASGI <https://bareasgi.readthedocs.io/en/latest>`_.

Installation
------------

The package can be installed with pip.

.. code-block:: bash

    pip install bareasgi-jinja2

This is a Python 3.7 and later package with dependencies on:

* bareASGI
* `jinja2 <http://jinja.pocoo.org>`_

Usage
-----

A utility function `add_jinja2` is provided.

.. code-block:: python

    from typing import Mapping, Any
    import jinja2
    import os.path
    import uvicorn
    from bareasgi import Application
    import bareasgi_jinja2

    here = os.path.abspath(os.path.dirname(__file__))


    @bareasgi_jinja2.template('example1.html')
    async def http_request_handler(scope, info, matches, content):
        return {'name': 'rob'}


    app = Application()

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(here, 'templates')),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
        enable_async=True
    )

    bareasgi_jinja2.add_jinja2(app, env)

    app.http_router.add({'GET'}, '/example1', http_request_handler)

    uvicorn.run(app, port=9010)


.. toctree::
    :maxdepth: 2
    :caption: Contents:

    api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
