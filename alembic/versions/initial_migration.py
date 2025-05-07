"""initial migration

Revision ID: 3efcbc24c80a
Revises: 
Create Date: 2024-05-07 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3efcbc24c80a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create plan table
    op.create_table(
        'plan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('rate_limit', sa.Integer(), nullable=True),
        sa.Column('initial_credits', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_plan_id'), 'plan', ['id'], unique=False)
    op.create_index(op.f('ix_plan_name'), 'plan', ['name'], unique=True)

    # Create user table
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('api_key', sa.String(), nullable=True),
        sa.Column('credits', sa.Integer(), nullable=True),
        sa.Column('plan_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_api_key'), 'user', ['api_key'], unique=True)
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)

    # Create requestlog table
    op.create_table(
        'requestlog',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('endpoint', sa.String(), nullable=True),
        sa.Column('request_data', sa.String(), nullable=True),
        sa.Column('response_data', sa.String(), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('credits_deducted', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_requestlog_id'), 'requestlog', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_requestlog_id'), table_name='requestlog')
    op.drop_table('requestlog')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_index(op.f('ix_user_api_key'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_plan_name'), table_name='plan')
    op.drop_index(op.f('ix_plan_id'), table_name='plan')
    op.drop_table('plan') 