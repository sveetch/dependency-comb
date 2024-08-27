.. _Libraries.io: https://www.python.org/

.. _install_intro:

=======
Install
=======

Install package in your environment : ::

    pip install dependency-comb

For development usage see :ref:`development_install`.

.. _install_apikey_intro:

API key
*******

Once installed you will need to create a private API key from `Libraries.io`_ with a
personal account, there is a free plan which allows to use the API with a simple amount
of 60 request/minute rate limit. The commandline already set a pause time which should
always respect this limit.

For security reasons, we only accept the API key from a file that we will call the
*filekey*. The filekey is just a simple plain text file that only contains the API as
generated from your `Libraries.io`_ account at section *Account Settings > API Key*. So
it would look like this: ::

    z4t315ztt0281b0be149ef351715325e

.. Warning::
    This is a randomly generated hash for this documentation purpose, it is not a
    valid registered key on the API.

On default, the commandlines expect a file ``librariesio-key.txt`` at your current
position but they have an option to specify a custom path so you can store it where you
want.