"""connect resources to alert_channels

Revision ID: e9fcfbdd9498
Revises: 55b6e612672f
Create Date: 2018-02-28 13:52:50.717217

"""

# revision identifiers, used by Alembic.
revision = "e9fcfbdd9498"
down_revision = "55b6e612672f"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "channels_resources",
        sa.Column(
            "channel_pkey",
            sa.Integer,
            sa.ForeignKey(
                "alert_channels.pkey", ondelete="CASCADE", onupdate="CASCADE"
            ),
            primary_key=True,
        ),
        sa.Column(
            "resource_id",
            sa.Integer,
            sa.ForeignKey(
                "resources.resource_id", ondelete="CASCADE", onupdate="CASCADE"
            ),
            primary_key=True,
        ),
    )


def downgrade():
    op.drop_table("channels_resources")
