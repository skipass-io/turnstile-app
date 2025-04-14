CREATE TABLE turnstile_app(
    id integer primary key autoincrement,
    token text not null
);


CREATE TABLE turnstile_passages(
    id integer primary key autoincrement,
    passage_id numeric not null,
    passage_duration numeric not null,
    frequent_label text not null
);

CREATE TABLE turnstile_svm_models(
    id integer primary key autoincrement,
    svm_model_id numeric not null
);