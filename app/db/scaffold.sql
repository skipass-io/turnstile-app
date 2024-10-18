create table config(
    workday datetime primary key,
    start_workday datetime,
    end_workday datetime,
);

create table skipasses( 
    label varchar(255) primary key,
    start_slot datetime,
    end_slot datetime,
    type_slot integer,
);

create table passages( 
    id integer primary key,
    time_passage datetime,
    FOREIGN KEY(skipass_label) REFERENCES skipasses(label),
    is_open boolean,
);

insert into config(workday, start_workday, end_workday) 
values 
    ("2024-10-13", "2024-10-13 10:00:00", "2024-10-13 18:00:00"),
    ("2024-10-14", "2024-10-14 10:00:00", "2024-10-14 18:00:00"),
    ("2024-10-15", "2024-10-15 10:00:00", "2024-10-15 18:00:00"),
    ("2024-10-16", "2024-10-16 10:00:00", "2024-10-16 18:00:00"),
    ("2024-10-17", "2024-10-17 10:00:00", "2024-10-17 18:00:00"),
    ("2024-10-18", "2024-10-18 10:00:00", "2024-10-18 18:00:00"),
    ("2024-10-19", "2024-10-19 10:00:00", "2024-10-19 18:00:00"),
    ("2024-10-20", "2024-10-20 10:00:00", "2024-10-20 18:00:00"),
    ("2024-10-21", "2024-10-21 10:00:00", "2024-10-21 18:00:00");

insert into skipasses (label, start_slot, end_slot, type_slot)
values
    ("kirill_zagoskin", "2024-10-13 10:00:00", "2024-10-13 16:00:00", 0);

