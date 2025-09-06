from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql

revision = "<autogenererad_ny_id>"
down_revision = "92655b483c00"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "predictions",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("lat", sa.Float, nullable=False),
        sa.Column("lon", sa.Float, nullable=False),
        sa.Column("target_date", sa.Date, nullable=False),
        sa.Column("t_p50", sa.Float),
        sa.Column("t_p10", sa.Float),
        sa.Column("t_p90", sa.Float),
        sa.Column("method", sa.Text),
        sa.Column("components", psql.JSONB),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("lat", "lon", "target_date", name="uq_predictions_lat_lon_date"),
    )
    op.create_index("idx_pred_latlon_date", "predictions", ["lat", "lon", "target_date"], unique=False)

    op.create_unique_constraint("uq_climo_latlon_doy", "climatology_daily", ["lat", "lon", "doy"])

def downgrade():
    op.drop_constraint("uq_climo_latlon_doy", "climatology_daily", type_="unique")
    op.drop_index("idx_pred_latlon_date", table_name="predictions")
    op.drop_table("predictions")
