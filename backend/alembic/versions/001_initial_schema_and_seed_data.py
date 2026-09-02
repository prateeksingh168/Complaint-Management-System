"""Initial schema and seed data matching PostgreSQL schema.sql

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-01 16:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('role', sa.String(length=20), server_default='user', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint("role IN ('user', 'admin')", name='users_role_check'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # 2. Create teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # 3. Create agents table
    op.create_table(
        'agents',
        sa.Column('id', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('team_id', sa.BigInteger(), nullable=True),
        sa.Column('skills', sa.Text(), nullable=True),
        sa.Column('availability', sa.String(length=20), server_default='Available', nullable=False),
        sa.Column('current_workload', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint("availability IN ('Available', 'Busy', 'Unavailable')", name='agents_availability_check'),
        sa.CheckConstraint("current_workload >= 0", name='agents_workload_check'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], onupdate='CASCADE', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # 4. Create complaints table
    op.create_table(
        'complaints',
        sa.Column('complaint_id', sa.String(length=20), nullable=False),
        sa.Column('complaint_text', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('complexity', sa.String(length=20), nullable=False),
        sa.Column('recommended_team', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], onupdate='CASCADE', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('complaint_id')
    )
    op.create_index('idx_complaints_category', 'complaints', ['category'])
    op.create_index('idx_complaints_priority', 'complaints', ['priority'])
    op.create_index('idx_complaints_complexity', 'complaints', ['complexity'])
    op.create_index('idx_complaints_recommended_team', 'complaints', ['recommended_team'])
    op.create_index('idx_complaints_user_id', 'complaints', ['user_id'])

    # 5. Create tickets table
    op.create_table(
        'tickets',
        sa.Column('id', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('ticket_number', sa.String(length=30), nullable=False),
        sa.Column('complaint_id', sa.String(length=20), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=30), server_default='Registered', nullable=False),
        sa.Column('assigned_team_id', sa.BigInteger(), nullable=True),
        sa.Column('assigned_agent_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_information', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_agent_id'], ['agents.id'], onupdate='CASCADE', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_team_id'], ['teams.id'], onupdate='CASCADE', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.complaint_id'], onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticket_number'),
        sa.UniqueConstraint('complaint_id')
    )
    op.create_index('idx_tickets_status', 'tickets', ['status'])
    op.create_index('idx_tickets_priority', 'tickets', ['priority'])
    op.create_index('idx_tickets_category', 'tickets', ['category'])
    op.create_index('idx_tickets_assigned_team', 'tickets', ['assigned_team_id'])
    op.create_index('idx_tickets_assigned_agent', 'tickets', ['assigned_agent_id'])

    # 6. Create ticket_history table
    op.create_table(
        'ticket_history',
        sa.Column('id', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('ticket_id', sa.BigInteger(), nullable=False),
        sa.Column('old_status', sa.String(length=30), nullable=True),
        sa.Column('new_status', sa.String(length=30), nullable=False),
        sa.Column('changed_by', sa.BigInteger(), nullable=True),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id'], onupdate='CASCADE', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ticket_history_ticket_id', 'ticket_history', ['ticket_id'])

    # 7. Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('ticket_id', sa.BigInteger(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.String(length=30), nullable=False),
        sa.Column('is_read', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], onupdate='CASCADE', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('idx_notifications_ticket_id', 'notifications', ['ticket_id'])

    # 8. Create faqs table
    op.create_table(
        'faqs',
        sa.Column('id', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('keywords', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. Create ai_predictions table
    op.create_table(
        'ai_predictions',
        sa.Column('id', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('ticket_id', sa.BigInteger(), nullable=False),
        sa.Column('predicted_category', sa.String(length=50), nullable=True),
        sa.Column('predicted_priority', sa.String(length=20), nullable=True),
        sa.Column('confidence_score', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('model_version', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ai_predictions_ticket_id', 'ai_predictions', ['ticket_id'])

    # 10. Seed Teams
    teams_table = sa.table('teams', sa.column('name', sa.String), sa.column('description', sa.Text))
    op.bulk_insert(
        teams_table,
        [
            {'name': 'General Support', 'description': 'General customer inquiries'},
            {'name': 'Technical Support', 'description': 'Technical & application issues'},
            {'name': 'Delivery Support', 'description': 'Package & shipping support'},
            {'name': 'Billing Support', 'description': 'Payment & invoice support'},
            {'name': 'Service Support', 'description': 'Service-related assistance'},
            {'name': 'Account Support', 'description': 'Account & login assistance'},
        ]
    )


def downgrade() -> None:
    op.drop_table('ai_predictions')
    op.drop_table('faqs')
    op.drop_table('notifications')
    op.drop_table('ticket_history')
    op.drop_table('tickets')
    op.drop_table('complaints')
    op.drop_table('agents')
    op.drop_table('teams')
    op.drop_table('users')
