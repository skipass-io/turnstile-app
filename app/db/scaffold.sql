CREATE TABLE app_settings(
    id integer primary key autoincrement,
    show_performance boolean not null,
    gr_face_detector numeric not null,
    gr_level_a_side numeric not null,
    gr_level_b_side numeric not null,
    gr_level_c_side numeric not null,
    gr_labels_count numeric not null,
    gr_percent_required numeric not null,
    gr_iteration_count numeric not null,
    gr_allowed_time_sec numeric not null,
    gr_passage_time_sec numeric not null,
    gr_not_allowed_time_sec numeric not null,
); 

CREATE TABLE skipass(
    id integer primary key autoincrement,
    type integer not null,
    start_slot timestamp not null,
    end_slot timestamp not null,
    label text not null
);

INSERT INTO app_settings (
    show_performance, 
    gr_face_detector,
    gr_level_a_side, 
    gr_level_b_side, 
    gr_level_c_side, 
    gr_labels_count, 
    gr_percent_required, 
    gr_iteration_count,
    gr_allowed_time_sec,
    gr_passage_time_sec,
    gr_not_allowed_time_sec
)
values (
    1, 
    0, 
    136, 
    180, 
    250, 
    20, 
    85, 
    2,
    6,
    1.5,
    10
)