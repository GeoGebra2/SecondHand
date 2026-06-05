from sqlalchemy import BigInteger, Integer


# Keep MySQL IDs aligned with the repo SQL scripts while preserving SQLite
# autoincrement behavior in tests.
BIGINT_ID = BigInteger().with_variant(Integer, 'sqlite')
