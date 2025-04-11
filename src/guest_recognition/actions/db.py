from db import database


class DB:
    def __init__(self):
        pass

    def get_token(self):
        rows: dict[str, str] = database.fetchall(
            table="turnstile_app",
            columns=["token"],
        )
        if rows:
            return rows[-1].get("token")

    def set_token(self, token: str):
        database.insert(
            table="turnstile_app",
            column_values={
                "token": token,
            },
        )

    def set_passage(self, passage_id, passage_duration):
        database.insert(
            table="turnstile_passages",
            column_values={
                "passage_id": passage_id,
                "passage_duration": passage_duration,
            },
        )
