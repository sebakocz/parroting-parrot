import itertools
import os

import psycopg2
from psycopg2 import Error

def get_deck_from_match(match_id):
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(os.getenv("COLLECTIVE_DB"))

        cursor = connection.cursor()

        cursor.execute("""
                            SELECT deck_id
                            FROM completed_games cg
                                INNER JOIN completed_game_users cgu
                                ON cg.winning_player_id = cgu.user_id
                            WHERE completed_game_id = %s
                            AND cgu.completed_game_id = cg.id
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
        print("Error while connecting to PostgresSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()