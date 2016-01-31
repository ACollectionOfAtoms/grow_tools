drop table if exists plants;
create table plants (
  id integer primary key autoincrement,
  plant_name text not null,
  sci_name text not null
);
