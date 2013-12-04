mohawk-data-platform
====================

**mohawk-data-platform** is a Django app for editing and publishing arbitrary JSON data in a form-based environment.


Features
--------

- Define structured models, with custom fields and validation.
- Create, edit and update instances defined models using the Django admin interface.
- Group models into applications for bulk access.
- Access models, instances and applications via a simple JSON API.
- Cross-origin API requests via CORS and JSONP.


Installation
------------

1. Checkout the latest mohawk-data-platform release and copy or symlink the
   ``data`` directory into your ``PYTHONPATH``.  If using pip, run 
   ``pip install mohawk-data-platform``.
2. Add ``'data'`` to your ``INSTALLED_APPS`` setting.
3. Add ``url(r"^", include("data.urls", namespace="data")),`` to you ``urls.py`` file.
4. Install and active the Django admin site, if not already present.


Admin usage
-----------

The bulk of the functionality for mohawk-data-platform is found within the admin UI. The basic workflow is:

1. Create a ``Model``, defining at least one ``Field``.
2. Create an ``Instance`` of that model.
3. Optionally, create an ``Application``.
4. Edit the model, and add it to the application you created.

Any data you add to the system will be **pubically-available** via the API endpoints.


Model field reference
---------------------

Fields added to a model take a number of optional config parameters, suppled as JSON documents. The available fields, and their configuration options, are listed below.

Fields which take choices expect them to be supplied as a list of ``[value, label]`` options::

    {
        "choices": [
            ["#ff0000", "Red"],
            ["#0000ff", "Green"],
            ["#00ff00", "Blue"]
        ]
    }


Text
^^^^

A single-line of unicode text.

::

    {
        "required": true,
        "choices": null
    }


Integer
^^^^^^^

An integer number.

::

    {
        "required": true,
        "choices": null
    }


Float
^^^^^

A floating-point number.

::

    {
        "required": true
    }


Date
^^^^

A date value.

::

    {
        "required": true
    }


Time
^^^^

A time value.

::

    {
        "required": true
    }


Datetime
^^^^^^^^

A combined date and time value.

::

    {
        "required": true
    }


Boolean
^^^^^^^

A true/false checkbox.

::

    {}


File
^^^^

An uploaded file.

::

    {
        "required": true
    }


Long text
^^^^^^^^^

Multiple lines of unicode text.

::

    {
        "required": true
    }


Model
^^^^^

A reference to an instance of a model.

::

    {
        "required": true,
        "model_id": "<model_id>"  // The type of instance being referenced.
    }


Multi model
^^^^^^^^^^^

A reference to multiple instances of a model.

::

    {
        "required": true,
        "model_id": "<model_id>"  // The type of instance being referenced.
    }


API endpoints
-------------


GET /<model_id>.json
^^^^^^^^^^^^^^^^^^^^

Returns all online instances of the given model::

    {
        "status": "OK",
        "message": "Instances of Your Model were successfully loaded.",
        "instances": [
            {
                "_date_created": "<timestamp>",
                "_date_modified": "<timestamp>",
                "_id": "<instance_id>",
                "_model": "<model_id>",
                "<field_name>": "<field_value>",
                ...
            },
            ...
        ]
    }


GET /<model_id>/<instance_id>.json
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Returns the given instance::

    {
        "status": "OK",
        "message": "Instances of <model_name> were successfully loaded.",
        "instance": {
            "_date_created": "<timestamp>",
            "_date_modified": "<timestamp>",
            "_id": "<instance_id>",
            "_model": "<model_id>",
            "<field_name>": "<field_value>",
            ...
        }
    }


GET /a/<application_id>.json
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Returns all online instances within the given application::

    {
        "status": "OK",
        "message": "Instances within application <application_name> were successfully loaded.",
        "instances": [
            {
                "_date_created": "<timestamp>",
                "_date_modified": "<timestamp>",
                "_id": "<instance_id>",
                "_model": "<model_id>",
                "<field_name>": "<field_value>",
                ...
            },
            ...
        ]
    }



More information
----------------

The mohawk-data-platform project was developed at `Mohawk <http://www.mohawkhq.com/>`_, and
is released as Open Source under the MIT license.

You can get the code from the `mohawk-data-platform project site <http://github.com/mohawkhq/mohawk-data-platform>`_.


Contributors
------------

The following people were involved in the development of this project.

- Dave Hall - `Blog <http://blog.etianen.com/>`_ | `GitHub <http://github.com/etianen>`_ | `Twitter <http://twitter.com/etianen>`_ | `Google Profile <http://www.google.com/profiles/david.etianen>`_