from alembic import op # type: ignore
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute('create extension if not exists "uuid-ossp";')

    op.create_table(
        "climatology_daily",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("doy", sa.Integer(), nullable=False),
        sa.Column("tmean", sa.Float()),
        sa.Column("tmin", sa.Float()),
        sa.Column("tmax", sa.Float()),
        sa.Column("period_start", sa.Date()),
        sa.Column("period_end", sa.Date()),
        sa.Column("source", sa.Text(), server_default=sa.text("'meteostat'")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_climo_latlon_doy", "climatology_daily", ["lat", "lon", "doy"])

    op.create_table(
        "forecast_cache",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("run_time", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("tmean", sa.Float()),
        sa.Column("payload", psql.JSONB()),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("lat", "lon", "run_time", "target_date", name="uq_fc_lat_lon_run_target"),
    )
    op.create_index("idx_fc_latlon_target", "forecast_cache", ["lat", "lon", "target_date"])
    op.create_index("idx_fc_expires", "forecast_cache", ["expires_at"])

    op.create_table(
        "residuals",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("month", sa.Integer()),
        sa.Column("lead_days", sa.Integer()),
        sa.Column("variable", sa.Text(), server_default=sa.text("'tmean'")),
        sa.Column("resid", sa.Float(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_residuals_key", "residuals", ["month", "lead_days", "variable"])

    op.create_table(
        "backtest_runs",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.Column("finished_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("params", psql.JSONB()),
        sa.Column("summary", psql.JSONB()),
    )

def downgrade() -> None:
    op.drop_table("backtest_runs")
    op.drop_index("idx_residuals_key", table_name="residuals")
    op.drop_table("residuals")
    op.drop_index("idx_fc_expires", table_name="forecast_cache")
    op.drop_index("idx_fc_latlon_target", table_name="forecast_cache")
    op.drop_table("forecast_cache")
    op.drop_index("idx_climo_latlon_doy", table_name="climatology_daily")
    op.drop_table("climatology_daily")
