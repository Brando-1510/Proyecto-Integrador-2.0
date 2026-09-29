"""add admin role and is admin flag

Revision ID: 9a1d1c50ccec
Revises: c5b2ee0985ba
Create Date: 2026-09-28 20:43:25.241129

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '9a1d1c50ccec'
down_revision: Union[str, Sequence[str], None] = 'c5b2ee0985ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        'user_business',
        'role',
        existing_type=mysql.ENUM(
            'Gerente',
            'Analista Financiero',
            'Empleado',
            collation='utf8mb4_unicode_ci'
        ),
        type_=mysql.ENUM(
            'Administrador',
            'Gerente',
            'Analista Financiero',
            'Empleado',
            collation='utf8mb4_unicode_ci'
        ),
        existing_nullable=False
    )

    op.add_column(
        'users',
        sa.Column(
            'is_admin',
            sa.Boolean(),
            server_default='0',
            nullable=False
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column('users', 'is_admin')

    op.alter_column(
        'user_business',
        'role',
        existing_type=mysql.ENUM(
            'Administrador',
            'Gerente',
            'Analista Financiero',
            'Empleado',
            collation='utf8mb4_unicode_ci'
        ),
        type_=mysql.ENUM(
            'Gerente',
            'Analista Financiero',
            'Empleado',
            collation='utf8mb4_unicode_ci'
        ),
        existing_nullable=False
    )
