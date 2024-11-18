CREATE TABLE app_settings(
    id integer primary key autoincrement,
    show_performance boolean not null,
    gr_level_a numeric not null,
    gr_level_b numeric not null,
    gr_level_c numeric not null,
    gr_labels numeric not null,
    gr_percent numeric not null
); 

INSERT INTO app_settings (show_performance, gr_level_a, gr_level_b, gr_level_c, gr_labels, gr_percent)
values (0, 136, 180, 250, 20, 85)