create extension if not exists vector;

create table if not exists book_docs (
  id bigserial primary key,
  content text,
  embedding vector(1024)
)