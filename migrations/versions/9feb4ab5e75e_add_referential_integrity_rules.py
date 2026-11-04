"""add referential integrity rules

Revision ID: 9feb4ab5e75e
Revises: 3a8916465ae0
Create Date: 2026-11-04 09:18:00.130532
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9feb4ab5e75e"
down_revision: Union[str, Sequence[str], None] = "3a8916465ae0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply explicit ON DELETE / ON UPDATE rules."""

    # businesses.creator_id -> users.user_id
    op.drop_constraint("businesses_ibfk_1", "businesses", type_="foreignkey")
    op.create_foreign_key(
        "fk_businesses_creator_id_users",
        "businesses", "users",
        ["creator_id"], ["user_id"],
        ondelete="RESTRICT",
        onupdate="CASCADE",
    )

    # categories.business_id -> businesses.business_id
    op.drop_constraint("categories_ibfk_1", "categories", type_="foreignkey")
    op.create_foreign_key(
        "fk_categories_business_id_businesses",
        "categories", "businesses",
        ["business_id"], ["business_id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )

    # imports
    op.drop_constraint("imports_ibfk_2", "imports", type_="foreignkey")
    op.drop_constraint("imports_ibfk_1", "imports", type_="foreignkey")
    op.create_foreign_key(
        "fk_imports_business_id_businesses",
        "imports", "businesses",
        ["business_id"], ["business_id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )
    op.create_foreign_key(
        "fk_imports_user_id_users",
        "imports", "users",
        ["user_id"], ["user_id"],
        ondelete="RESTRICT",
        onupdate="CASCADE",
    )

    # movements
    op.drop_constraint("movements_ibfk_1", "movements", type_="foreignkey")
    op.drop_constraint("movements_ibfk_2", "movements", type_="foreignkey")
    op.drop_constraint("movements_ibfk_3", "movements", type_="foreignkey")
    op.drop_constraint("movements_ibfk_4", "movements", type_="foreignkey")
    op.create_foreign_key(
        "fk_movements_updated_by_users",
        "movements", "users",
        ["updated_by"], ["user_id"],
        ondelete="SET NULL",
        onupdate="CASCADE",
    )
    op.create_foreign_key(
        "fk_movements_import_id_imports",
        "movements", "imports",
        ["import_id"], ["import_id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )
    op.create_foreign_key(
        "fk_movements_business_id_businesses",
        "movements", "businesses",
        ["business_id"], ["business_id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )
    op.create_foreign_key(
        "fk_movements_created_by_users",
        "movements", "users",
        ["created_by"], ["user_id"],
        ondelete="RESTRICT",
        onupdate="CASCADE",
    )

    # recoveries.user_id -> users.user_id
    op.drop_constraint("recoveries_ibfk_1", "recoveries", type_="foreignkey")
    op.create_foreign_key(
        "fk_recoveries_user_id_users",
        "recoveries", "users",
        ["user_id"], ["user_id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )

    # sales
    op.drop_constraint("sales_ibfk_1", "sales", type_="foreignkey")
    op.drop_constraint("sales_ibfk_2", "sales", type_="foreignkey")
    op.drop_constraint("sales_ibfk_3", "sales", type_="foreignkey")
    op.drop_constraint("sales_ibfk_4", "sales", type_="foreignkey")
    op.drop_constraint("sales_ibfk_5", "sales", type_="foreignkey")
    op.create_foreign_key(
        "fk_sales_updated_by_users",
        "sales", "users",
        ["updated_by"], ["user_id"],
        ondelete="SET NULL",
        onupdate="CASCADE",
    )
    op.create_foreign_key(
        "fk_sales_category_id_categories",
        "sales", "categories",
        ["category_id"], ["category_id"],
        ondelete="RESTRICT",
        onupdate="CASCADE",
    )
    op.create_foreign_key(
        "fk_sales_business_id_businesses",
        "sales", "businesses",
        ["business_id"], ["business_id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )
    op.create_foreign_key(
        "fk_sales_created_by_users",
        "sales", "users",
        ["created_by"], ["user_id"],
        ondelete="RESTRICT",
        onupdate="CASCADE",
    )
    op.create_foreign_key(
        "fk_sales_import_id_imports",
        "sales", "imports",
        ["import_id"], ["import_id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )

    # user_business
    op.drop_constraint("user_business_ibfk_1", "user_business", type_="foreignkey")
    op.drop_constraint("user_business_ibfk_2", "user_business", type_="foreignkey")
    op.create_foreign_key(
        "fk_user_business_business_id_businesses",
        "user_business", "businesses",
        ["business_id"], ["business_id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )
    op.create_foreign_key(
        "fk_user_business_user_id_users",
        "user_business", "users",
        ["user_id"], ["user_id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )


def downgrade() -> None:
    """Restore the original foreign-key definitions."""

    # Drop the named constraints created by upgrade().
    op.drop_constraint(
        "fk_user_business_user_id_users", "user_business", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_user_business_business_id_businesses", "user_business", type_="foreignkey"
    )

    op.drop_constraint("fk_sales_import_id_imports", "sales", type_="foreignkey")
    op.drop_constraint("fk_sales_created_by_users", "sales", type_="foreignkey")
    op.drop_constraint("fk_sales_business_id_businesses", "sales", type_="foreignkey")
    op.drop_constraint("fk_sales_category_id_categories", "sales", type_="foreignkey")
    op.drop_constraint("fk_sales_updated_by_users", "sales", type_="foreignkey")

    op.drop_constraint("fk_recoveries_user_id_users", "recoveries", type_="foreignkey")

    op.drop_constraint(
        "fk_movements_created_by_users", "movements", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_movements_business_id_businesses", "movements", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_movements_import_id_imports", "movements", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_movements_updated_by_users", "movements", type_="foreignkey"
    )

    op.drop_constraint("fk_imports_user_id_users", "imports", type_="foreignkey")
    op.drop_constraint("fk_imports_business_id_businesses", "imports", type_="foreignkey")

    op.drop_constraint(
        "fk_categories_business_id_businesses", "categories", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_businesses_creator_id_users", "businesses", type_="foreignkey"
    )

    # Recreate the original constraints without explicit ON DELETE / ON UPDATE.
    op.create_foreign_key(
        "businesses_ibfk_1", "businesses", "users", ["creator_id"], ["user_id"]
    )
    op.create_foreign_key(
        "categories_ibfk_1", "categories", "businesses", ["business_id"], ["business_id"]
    )
    op.create_foreign_key(
        "imports_ibfk_1", "imports", "businesses", ["business_id"], ["business_id"]
    )
    op.create_foreign_key(
        "imports_ibfk_2", "imports", "users", ["user_id"], ["user_id"]
    )
    op.create_foreign_key(
        "movements_ibfk_1", "movements", "businesses", ["business_id"], ["business_id"]
    )
    op.create_foreign_key(
        "movements_ibfk_2", "movements", "users", ["created_by"], ["user_id"]
    )
    op.create_foreign_key(
        "movements_ibfk_3", "movements", "imports", ["import_id"], ["import_id"]
    )
    op.create_foreign_key(
        "movements_ibfk_4", "movements", "users", ["updated_by"], ["user_id"]
    )
    op.create_foreign_key(
        "recoveries_ibfk_1", "recoveries", "users", ["user_id"], ["user_id"]
    )
    op.create_foreign_key(
        "sales_ibfk_1", "sales", "businesses", ["business_id"], ["business_id"]
    )
    op.create_foreign_key(
        "sales_ibfk_2", "sales", "categories", ["category_id"], ["category_id"]
    )
    op.create_foreign_key(
        "sales_ibfk_3", "sales", "users", ["created_by"], ["user_id"]
    )
    op.create_foreign_key(
        "sales_ibfk_4", "sales", "imports", ["import_id"], ["import_id"]
    )
    op.create_foreign_key(
        "sales_ibfk_5", "sales", "users", ["updated_by"], ["user_id"]
    )
    op.create_foreign_key(
        "user_business_ibfk_1", "user_business", "businesses",
        ["business_id"], ["business_id"]
    )
    op.create_foreign_key(
        "user_business_ibfk_2", "user_business", "users",
        ["user_id"], ["user_id"]
    )
