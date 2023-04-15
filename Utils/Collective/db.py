import itertools
import os

import psycopg2
from psycopg2 import Error


def get_history(card_id):
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(os.getenv("COLLECTIVE_DB"))

        cursor = connection.cursor()

        # old_image = p/cards/a54bed60-f790-11eb-89bb-8d69998314a9-m.png-2021-09-24T16:26:02
        cursor.execute(
            """
                SELECT old_image, dt_created
                FROM card_updates
                WHERE target_object_printing_id = %s
            """,
            [card_id],
        )

        query = cursor.fetchall()

        return query

    except (Exception, Error) as error:
        print("Error while connecting to PostgresSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
