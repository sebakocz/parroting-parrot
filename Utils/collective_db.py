import itertools
import os

import psycopg2
from psycopg2 import Error

def getDeckFromMatch(match_id):
    try:
        connection = psycopg2.connect(os.getenv("COLLECTIVE_DB"))

        cursor = connection.cursor()

        cursor.execute("""
                SELECT deck_id
                FROM completed_game_users cgu
                WHERE completed_game_id = %s
            """, [match_id])

        query = cursor.fetchone()
        deck_id = query[0]

        cursor.execute("""
            SELECT dlc.card_id
            FROM deck_list_cards dlc
            WHERE deck_id = %s
        """, [deck_id])

        query = cursor.fetchall()

        return list(itertools.chain(*query))

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            # print("PostgreSQL connection is closed")