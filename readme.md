# Mistral RAG

## 🚀 Quick Start

Follow these steps to get the project running on your local machine.

### 1. Clone the repository

### 2. Set up a Virtual Environment

It is highly recommended to use a virtual environment to isolate project dependencies.

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate

```

**Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate

```

### 3. Install Dependencies

Once the virtual environment is activated, install the required packages:

**macOS / Linux:**

```bash
pip3 install -r requirements.txt

```

**Windows:**

```bash
pip install -r requirements.txt

```

### 4. Database Setup (Supabase)

This project uses [Supabase](https://supabase.com/) with `pgvector` for vector storage. Before running the application, you need to set up your database:

1. Create a new project in your Supabase dashboard.
2. Navigate to the **SQL Editor**.
3. Run the following SQL queries to enable the vector extension, create the documents table, and set up the search function:

```sql
-- Enable the vector extension
create extension if not exists vector; 

-- Create the table for storing documents and embeddings
create table if not exists book_docs ( 
  id bigserial primary key, 
  content text, 
  embedding vector(1024) 
);

-- Create a function to search for similar documents
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
```

### 5. Configure Environment Variables

The project uses a `.env` file for configuration. Create your own by copying the template:

```bash
cp .env.example .env

```

*Note: Open the newly created `.env` file and fill in your actual credentials/API keys.*

### 6. Run the Application

Finally, start the project:


```bash
python main.py

```