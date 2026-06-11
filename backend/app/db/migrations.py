from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


def run_legacy_mysql_migrations(engine: Engine) -> None:
    if engine.dialect.name != 'mysql':
        return

    with engine.begin() as connection:
        columns = _get_table_columns(connection, 'product')

        if 'product_id' not in columns:
            return

        has_legacy_category_name = 'category_name' in columns
        has_category_id = 'category_id' in columns

        if not has_category_id:
            connection.execute(text("ALTER TABLE product ADD COLUMN category_id BIGINT NULL AFTER seller_id"))
            has_category_id = True

        if has_legacy_category_name:
            connection.execute(
                text(
                    """
                    UPDATE product p
                    JOIN category c ON c.category_name = p.category_name
                    SET p.category_id = c.category_id
                    WHERE p.category_id IS NULL
                    """
                )
            )

            unresolved_count = connection.execute(
                text("SELECT COUNT(*) FROM product WHERE category_id IS NULL")
            ).scalar_one()
            if unresolved_count:
                raise SQLAlchemyError('存在未能映射到 category_id 的旧商品数据，请先检查 category 表与 product.category_name 数据。')

        if not has_category_id:
            return

        index_names = _get_index_names(connection, 'product')
        if 'idx_product_category_status' in index_names and has_legacy_category_name:
            connection.execute(text("DROP INDEX idx_product_category_status ON product"))

        connection.execute(
            text(
                """
                ALTER TABLE product
                MODIFY COLUMN category_id BIGINT NOT NULL
                """
            )
        )
        if 'idx_product_category_status' not in _get_index_names(connection, 'product'):
            connection.execute(
                text(
                    """
                    ALTER TABLE product
                    ADD INDEX idx_product_category_status (category_id, status)
                    """
                )
            )

        constraints = _get_foreign_key_names(connection, 'product')
        if 'fk_product_category' not in constraints:
            connection.execute(
                text(
                    """
                    ALTER TABLE product
                    ADD CONSTRAINT fk_product_category
                    FOREIGN KEY (category_id) REFERENCES category(category_id)
                    """
                )
            )


def _get_table_columns(connection, table_name: str) -> set[str]:
    return {
        row[0]
        for row in connection.execute(
            text(
                """
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = :table_name
                """
            ),
            {'table_name': table_name},
        )
    }


def _get_index_names(connection, table_name: str) -> set[str]:
    return {
        row[0]
        for row in connection.execute(
            text(
                """
                SELECT DISTINCT INDEX_NAME
                FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = :table_name
                """
            ),
            {'table_name': table_name},
        )
    }


def _get_foreign_key_names(connection, table_name: str) -> set[str]:
    return {
        row[0]
        for row in connection.execute(
            text(
                """
                SELECT CONSTRAINT_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = :table_name
                  AND REFERENCED_TABLE_NAME IS NOT NULL
                """
            ),
            {'table_name': table_name},
        )
    }
