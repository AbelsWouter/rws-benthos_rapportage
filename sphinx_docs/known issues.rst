Known Issues
==================

Deprecation
~~~~~~~~~~~~~~~~~~~~~~~~~


When running the script, you may see the following warning:
.. code-block:: cmd
    ..\..\Users\Maarten Japink\AppData\Local\pypoetry\Cache\virtualenvs\rws-benthos-rapportage-m5VeNjis-py3.12\Lib\site-packages\dateutil\tz\tz.py:37
    C:\Users\Maarten Japink\AppData\Local\pypoetry\Cache\virtualenvs\rws-benthos-rapportage-m5VeNjis-py3.12\Lib\site-packages\dateutil\tz\tz.py:37: DeprecationWarning: datetime.datetime.utcfromtimestamp() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.fromtimestamp(timestamp, datetime.UTC).
    EPOCH = datetime.datetime.utcfromtimestamp(0)
    -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html