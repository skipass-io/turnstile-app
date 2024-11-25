CREATE TABLE app_settings(
    id integer primary key autoincrement,
    show_performance boolean not null,
    gr_face_detector numeric not null,
    gr_level_a numeric not null,
    gr_level_b numeric not null,
    gr_level_c numeric not null,
    gr_labels numeric not null,
    gr_percent numeric not null,
    gr_iteration numeric not null
); 

CREATE TABLE skipass(
    id integer primary key autoincrement,
    type integer not null,
    start_time timestamp not null,
    end_time timestamp not null,
    label text not null
);

INSERT INTO app_settings (
    show_performance, 
    gr_face_detector,
    gr_level_a, 
    gr_level_b, 
    gr_level_c, 
    gr_labels, 
    gr_percent,
    gr_iteration
)
values (1, 0, 136, 180, 250, 20, 85, 3)