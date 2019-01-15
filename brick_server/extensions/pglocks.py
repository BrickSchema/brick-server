from contextlib import contextmanager
from zlib import crc32
import pdb

import psycopg2

@contextmanager
def advisory_lock(lock_id, shared=False, wait=True, using=None):

    #from django.db import DEFAULT_DB_ALIAS, connections, transaction

    dbname = 'brick'
    user = 'bricker'
    pw = 'brick-demo'
    host = 'localhost'
    port = 6001
    conn_str = "dbname='{dbname}' host='{host}' port='{port}' " \
        .format(dbname=dbname, host=host, port=port) + \
        "password='{pw}' user='{user}'".format(user=user, pw=pw)
    connections = psycopg2.connect(conn_str)

    # Assemble the function name based on the options.

    function_name = 'pg_'

    if not wait:
        function_name += 'try_'

    function_name += 'advisory_lock'

    if shared:
        function_name += '_shared'

    release_function_name = 'pg_advisory_unlock'
    if shared:
        release_function_name += '_shared'

    # Format up the parameters.


    # Generates an id within postgres integer range (-2^31 to 2^31 - 1).
    # crc32 generates an unsigned integer in Py3, we convert it into
    # a signed integer using 2's complement (this is a noop in Py2)

    base = "SELECT %s(%d)"
    params = (lock_id,)

    acquire_params = ( function_name, ) + params

    command = base % acquire_params
    cursor = connections.cursor()

    cursor.execute(command)

    if not wait:
        acquired = cursor.fetchone()[0]
    else:
        acquired = True

    try:
        yield acquired
    finally:
        if acquired:
            release_params = ( release_function_name, ) + params

            command = base % release_params
            cursor.execute(command)

        cursor.close()

def get_lock_id(uuid):
    pass


if __name__ == '__main__':
    lock_id = 1234
    with advisory_lock(lock_id, shared=False, wait=True, using=None) as al:
        pdb.set_trace()