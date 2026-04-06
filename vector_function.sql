create or replace function match_book_docs (
  query_embedding extensions.vector(1024),
  match_threshold float,
  match_count int
)
returns table (
  id bigint,
  content text,
  similarity float
)
language sql stable
as $$
  select
    book_docs.id,
    book_docs.content,
    1 - (book_docs.embedding <=> query_embedding) as similarity
  from book_docs
  where 1 - (book_docs.embedding <=> query_embedding) > match_threshold
  order by (book_docs.embedding <=> query_embedding) asc
  limit match_count;
$$;