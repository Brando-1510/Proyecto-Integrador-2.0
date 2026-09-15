"""remove unique from business owner

Revision ID: 2f55c1373467
Revises: 5ea006811bfb
Create Date: 2026-09-14 19:32:06.567445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f55c1373467'
down_revision: Union[str, Sequence[str], None] = '5ea006811bfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Eliminamos temporalmente la llave foránea en MySQL para liberar el índice
    op.execute("ALTER TABLE businesses DROP FOREIGN KEY businesses_ibfk_1;")

    # 2. Eliminamos el índice único de la columna owner_id
    with op.batch_alter_table('businesses', schema=None) as batch_op:
        batch_op.drop_index('owner_id')

    # 3. Volvemos a crear la llave foránea (ahora permitiendo múltiples registros por usuario)
    op.execute("""
        ALTER TABLE businesses 
        ADD CONSTRAINT businesses_ibfk_1 
        FOREIGN KEY (owner_id) REFERENCES users(user_id);
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE businesses DROP FOREIGN KEY businesses_ibfk_1;")
    with op.batch_alter_table('businesses', schema=None) as batch_op:
        batch_op.create_index('owner_id', ['owner_id'], unique=True)
    op.execute("""
        ALTER TABLE businesses 
        ADD CONSTRAINT businesses_ibfk_1 
        FOREIGN KEY (owner_id) REFERENCES users(user_id);
    """)