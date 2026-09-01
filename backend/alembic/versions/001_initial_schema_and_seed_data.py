"""Initial schema and seed data for categories and teams

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-01 16:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=True)

    # 2. Create teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_teams_name'), 'teams', ['name'], unique=True)

    # 3. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 4. Create agents table
    op.create_table(
        'agents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('skills', sa.JSON(), nullable=False),
        sa.Column('current_workload', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # 5. Create complaints table
    op.create_table(
        'complaints',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('complaint_id', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='Medium'),
        sa.Column('complexity', sa.String(length=20), nullable=False, server_default='Medium'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Registered'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('complaint_id')
    )
    op.create_index(op.f('ix_complaints_complaint_id'), 'complaints', ['complaint_id'], unique=True)
    op.create_index(op.f('ix_complaints_category_id'), 'complaints', ['category_id'], unique=False)
    op.create_index(op.f('ix_complaints_status'), 'complaints', ['status'], unique=False)

    # 6. Create tickets table
    op.create_table(
        'tickets',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('ticket_id', sa.String(length=50), nullable=False),
        sa.Column('complaint_id', sa.String(length=36), nullable=False),
        sa.Column('assigned_team_id', sa.Integer(), nullable=True),
        sa.Column('assigned_agent_id', sa.String(length=36), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Registered'),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='Medium'),
        sa.Column('ai_confidence', sa.Float(), nullable=True),
        sa.Column('escalated', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('escalated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assigned_agent_id'], ['agents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_team_id'], ['teams.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('complaint_id')
    )
    op.create_index(op.f('ix_tickets_ticket_id'), 'tickets', ['ticket_id'], unique=False)
    op.create_index(op.f('ix_tickets_status'), 'tickets', ['status'], unique=False)
    op.create_index(op.f('ix_tickets_priority'), 'tickets', ['priority'], unique=False)

    # 7. Create ticket_history table
    op.create_table(
        'ticket_history',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('ticket_id', sa.String(length=36), nullable=False),
        sa.Column('old_status', sa.String(length=50), nullable=True),
        sa.Column('new_status', sa.String(length=50), nullable=False),
        sa.Column('changed_by', sa.String(length=36), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('ticket_id', sa.String(length=36), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. Create faqs table
    op.create_table(
        'faqs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 10. Seed Categories and Teams (PRD Section 6)
    categories_table = sa.table('categories', sa.column('name', sa.String), sa.column('is_active', sa.Boolean))
    teams_table = sa.table('teams', sa.column('name', sa.String), sa.column('is_active', sa.Boolean))

    op.bulk_insert(
        categories_table,
        [
            {'name': 'Other', 'is_active': True},
            {'name': 'Technical', 'is_active': True},
            {'name': 'Delivery', 'is_active': True},
            {'name': 'Billing', 'is_active': True},
            {'name': 'Service', 'is_active': True},
            {'name': 'Account', 'is_active': True},
        ]
    )

    op.bulk_insert(
        teams_table,
        [
            {'name': 'General Support', 'is_active': True},
            {'name': 'Technical Support', 'is_active': True},
            {'name': 'Delivery Support', 'is_active': True},
            {'name': 'Billing Support', 'is_active': True},
            {'name': 'Service Support', 'is_active': True},
            {'name': 'Account Support', 'is_active': True},
        ]
    )


def downgrade() -> None:
    op.drop_table('faqs')
    op.drop_table('notifications')
    op.drop_table('ticket_history')
    op.drop_table('tickets')
    op.drop_table('complaints')
    op.drop_table('agents')
    op.drop_table('users')
    op.drop_table('teams')
    op.drop_table('categories')
