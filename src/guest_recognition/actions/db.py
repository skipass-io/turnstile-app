from db import database


class DB:
    def __init__(self):
        pass

    def get_token(self): 
        rows: dict[str, str] = database.fetchall( # type: ignore[empty-body]
            table="turnstile_app",
            columns=["token"],
        )
        if rows:
            return rows[-1].get("token") # type: ignore[empty-body]

    def set_token(self, token: str):
        database.insert(
            table="turnstile_app",
            column_values={
                "token": token,
            },
        )

    def set_passage(self, passage_id, passage_duration, frequent_label):
        database.insert(
            table="turnstile_passages",
            column_values={
                "passage_id": passage_id,
                "passage_duration": passage_duration,
                "frequent_label": frequent_label
            },
        )

    def get_svm_model_id(self):
        rows: dict[str, str] = database.fetchall( # type: ignore[empty-body]
            table="turnstile_svm_models",
            columns=["svm_model_id"],
        )
        if rows:
            return int(rows[-1].get("svm_model_id")) # type: ignore[empty-body]

    def set_svm_model_id(self, svm_model_id: int):
        database.insert(
            table="turnstile_svm_models",
            column_values={
                "svm_model_id": svm_model_id,
            },
        )