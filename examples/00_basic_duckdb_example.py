import duckdb as db

result = db.sql("SELECT 'Hello, DuckDB!' AS greeting").fetchall()
print(type(result))
print(result)

res = db.sql("SELECT 'DuckDB is awesome!' AS message")
print(type(res))
print(res)

# rel = db.sql("SELECT * from range(10_00) AS tbl(ID)")
# rel.show()

# Create a connection to an in-memory DuckDB database
conn = db.connect("my_database.db")

conn.sql("SHOW ALL TABLES").show()

# Create a new table
conn.sql("""
         CREATE OR REPLACE TABLE countries(
             country VARCHAR,
             code VARCHAR,
             region VARCHAR,
             subregion VARCHAR,
             intermdiate_region VARCHAR
         );
         """)

# Insert data into the table
conn.sql("""
         INSERT INTO countries VALUES
             ('United States', 'US', 'Americas', 'Northern America', NULL),
             ('Canada', 'CA', 'Americas', 'Northern America', NULL),
             ('Mexico', 'MX', 'Americas', 'Central America', NULL),
             ('Brazil', 'BR', 'Americas', 'South America', NULL),
             ('Argentina', 'AR', 'Americas', 'South America', NULL);
         """)
conn.sql("SHOW ALL TABLES").show()