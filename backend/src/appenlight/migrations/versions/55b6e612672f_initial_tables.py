# -*- coding: utf-8 -*-

# Copyright 2010 - 2017 RhodeCode GmbH and the AppEnlight project authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""initial tables

Revision ID: 55b6e612672f
Revises: None
Create Date: 2014-10-13 23:47:38.295159

"""

# revision identifiers, used by Alembic.
revision = "55b6e612672f"
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("users", sa.Column("first_name", sa.Unicode(25)))
    op.add_column("users", sa.Column("last_name", sa.Unicode(50)))
    op.add_column("users", sa.Column("company_name", sa.Unicode(255)))
    op.add_column("users", sa.Column("company_address", sa.Unicode(255)))
    op.add_column("users", sa.Column("phone1", sa.Unicode(25)))
    op.add_column("users", sa.Column("phone2", sa.Unicode(25)))
    op.add_column("users", sa.Column("zip_code", sa.Unicode(25)))
    op.add_column(
        "users",
        sa.Column(
            "default_report_sort",
            sa.Unicode(20),
            nullable=False,
            server_default="newest",
        ),
    )
    op.add_column("users", sa.Column("city", sa.Unicode(128)))
    op.add_column("users", sa.Column("notes", sa.UnicodeText, server_default=""))
    op.add_column(
        "users",
        sa.Column("notifications", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.add_column(
        "users",
        sa.Column("registration_ip", sa.Unicode(40), nullable=False, server_default=""),
    )

    op.create_table(
        "integrations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "resource_id",
            sa.Integer(),
            sa.ForeignKey(
                "resources.resource_id", onupdate="cascade", ondelete="cascade"
            ),
        ),
        sa.Column("integration_name", sa.Unicode(64)),
        sa.Column("config", sa.dialects.postgresql.JSON, nullable=False),
        sa.Column(
            "modified_date", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("external_id", sa.Unicode(255)),
        sa.Column("external_id2", sa.Unicode(255)),
    )

    op.create_table(
        "alert_channels",
        sa.Column(
            "owner_id",
            sa.Integer(),
            sa.ForeignKey("users.id", onupdate="cascade", ondelete="cascade"),
            nullable=False,
        ),
        sa.Column("channel_name", sa.Unicode(25), nullable=False),
        sa.Column("channel_value", sa.Unicode(80), nullable=False),
        sa.Column("channel_json_conf", sa.dialects.postgresql.JSON, nullable=False),
        sa.Column(
            "channel_validated", sa.Boolean, nullable=False, server_default="False"
        ),
        sa.Column("send_alerts", sa.Boolean, nullable=False, server_default="True"),
        sa.Column(
            "notify_only_first", sa.Boolean, nullable=False, server_default="False"
        ),
        sa.Column("daily_digest", sa.Boolean, nullable=False, server_default="True"),
        sa.Column("pkey", sa.Integer(), primary_key=True),
        sa.Column(
            "integration_id",
            sa.Integer,
            sa.ForeignKey("integrations.id", onupdate="cascade", ondelete="cascade"),
        ),
    )
    op.create_unique_constraint(
        "uq_alert_channels",
        "alert_channels",
        ["owner_id", "channel_name", "channel_value"],
    )

    op.create_table(
        "alert_channels_actions",
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column(
            "resource_id",
            sa.Integer(),
            sa.ForeignKey(
                "resources.resource_id", onupdate="cascade", ondelete="cascade"
            ),
        ),
        sa.Column("pkey", sa.Integer(), primary_key=True),
        sa.Column("action", sa.Unicode(10), nullable=False, server_default="always"),
        sa.Column("rule", sa.dialects.postgresql.JSON),
        sa.Column("type", sa.Unicode(10), index=True),
        sa.Column("other_id", sa.Unicode(40), index=True),
        sa.Column("config", sa.dialects.postgresql.JSON),
        sa.Column("name", sa.Unicode(255), server_default=""),
    )

    op.create_table(
        "application_postprocess_conf",
        sa.Column("pkey", sa.Integer(), primary_key=True),
        sa.Column("do", sa.Unicode(25), nullable=False),
        sa.Column("new_value", sa.UnicodeText(), nullable=False, server_default=""),
        sa.Column(
            "resource_id",
            sa.Integer(),
            sa.ForeignKey(
                "resources.resource_id", onupdate="cascade", ondelete="cascade"
            ),
            nullable=False,
        ),
        sa.Column("rule", sa.dialects.postgresql.JSON),
    )

    op.create_table(
        "applications",
        sa.Column(
            "resource_id",
            sa.Integer(),
            sa.ForeignKey(
                "resources.resource_id", onupdate="cascade", ondelete="cascade"
            ),
            nullable=False,
            primary_key=True,
            autoincrement=False,
        ),
        sa.Column("domains", sa.UnicodeText, nullable=False),
        sa.Column("api_key", sa.Unicode(32), nullable=False, index=True),
        sa.Column(
            "default_grouping",
            sa.Unicode(20),
            nullable=False,
            server_default="url_type",
        ),
        sa.Column("public_key", sa.Unicode(32), nullable=False, index=True),
        sa.Column(
            "error_report_threshold", sa.Integer(), server_default="10", nullable=False
        ),
        sa.Column(
            "slow_report_threshold", sa.Integer(), server_default="10", nullable=False
        ),
        sa.Column("apdex_threshold", sa.Float(), server_default="0.7", nullable=False),
        sa.Column(
            "allow_permanent_storage",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
    )
    op.create_unique_constraint(None, "applications", ["public_key"])
    op.create_unique_constraint(None, "applications", ["api_key"])

    op.create_table(
        "metrics",
        sa.Column("pkey", sa.types.BigInteger, nullable=False, primary_key=True),
        sa.Column(
            "resource_id",
            sa.Integer(),
            sa.ForeignKey(
                "resources.resource_id", onupdate="cascade", ondelete="cascade"
            ),
        ),
        sa.Column("timestamp", sa.DateTime),
        sa.Column("namespace", sa.Unicode(255)),
        sa.Column("tags", sa.dialects.postgresql.JSON, server_default="{}"),
    )

    op.create_table(
        "events",
        sa.Column("id", sa.Integer, nullable=False, primary_key=True),
        sa.Column("start_date", sa.DateTime, nullable=False, index=True),
        sa.Column("end_date", sa.DateTime),
        sa.Column("status", sa.Integer(), nullable=False, index=True),
        sa.Column("event_type", sa.Integer(), nullable=False, index=True),
        sa.Column("origin_user_id", sa.Integer()),
        sa.Column("target_user_id", sa.Integer()),
        sa.Column("resource_id", sa.Integer(), index=True),
        sa.Column("text", sa.UnicodeText, server_default=""),
        sa.Column("values", sa.dialects.postgresql.JSON),
        sa.Column("target_id", sa.Integer()),
        sa.Column("target_uuid", sa.Unicode(40), index=True),
    )

    op.create_table(
        "logs",
        sa.Column("log_id", sa.types.BigInteger, nullable=False, primary_key=True),
        sa.Column(
            "resource_id",
            sa.Integer(),
            sa.ForeignKey(
                "resources.resource_id", onupdate="cascade", ondelete="cascade"
            ),
        ),
        sa.Column("log_level", sa.SmallInteger(), nullable=False),
        sa.Column("primary_key", sa.Unicode(128), nullable=True),
        sa.Column("message", sa.UnicodeText, nullable=False, server_default=""),
        sa.Column("timestamp", sa.DateTime),
        sa.Column("namespace", sa.Unicode(255)),
        sa.Column("request_id", sa.Unicode(40)),
        sa.Column("tags", sa.dialects.postgresql.JSON, server_default="{}"),
        sa.Column("permanent", sa.Boolean(), server_default="false", nullable=False),
    )

    op.create_table(
        "reports_groups",
        sa.Column("id", sa.types.BigInteger, primary_key=True),
        sa.Column(
            "resource_id",
            sa.Integer,
            sa.ForeignKey(
                "resources.resource_id", onupdate="cascade", ondelete="cascade"
            ),
            nullable=False,
        ),
        sa.Column("priority", sa.Integer, nullable=False, server_default="5"),
        sa.Column(
            "first_timestamp",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("last_timestamp", sa.DateTime()),
        sa.Column("error", sa.UnicodeText, nullable=False, server_default=""),
        sa.Column("grouping_hash", sa.Unicode(40), nullable=False, server_default=""),
        sa.Column(
            "triggered_postprocesses_ids",
            sa.dialects.postgresql.JSON,
            nullable=False,
            server_default="[]",
        ),
        sa.Column("report_type", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_reports", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_report", sa.Integer, nullable=False, server_default="0"),
        sa.Column("occurences", sa.Integer, nullable=False, server_default="1"),
        sa.Column("average_duration", sa.Float(), nullable=False, server_default="0"),
        sa.Column("summed_duration", sa.Float(), nullable=False, server_default="0"),
        sa.Column("notified", sa.Boolean, nullable=False, server_default="False"),
        sa.Column("fixed", sa.Boolean, nullable=False, server_default="False"),
        sa.Column("public", sa.Boolean, nullable=False, server_default="False"),
        sa.Column("read", sa.Boolean, nullable=False, server_default="False"),
    )

    op.create_table(
        "reports",
        sa.Column("id", sa.types.BigInteger, primary_key=True),
        sa.Column(
            "group_id",
            sa.types.BigInteger,
            sa.ForeignKey("reports_groups.id", onupdate="cascade", ondelete="cascade"),
            nullable=False,
            index=True,
        ),
        sa.Column("resource_id", sa.Integer, nullable=False, index=True),
        sa.Column("report_type", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error", sa.UnicodeText, nullable=False, server_default=""),
        sa.Column(
            "extra", sa.dialects.postgresql.JSON, nullable=False, server_default="{}"
        ),
        sa.Column(
            "request", sa.dialects.postgresql.JSON, nullable=False, server_default="{}"
        ),
        sa.Column(
            "tags", sa.dialects.postgresql.JSON, nullable=False, server_default="{}"
        ),
        sa.Column("ip", sa.Unicode(39), nullable=False, server_default=""),
        sa.Column("username", sa.Unicode(255), nullable=False, server_default=""),
        sa.Column("user_agent", sa.Unicode(512), nullable=False, server_default=""),
        sa.Column("url", sa.UnicodeText, nullable=False, server_default=""),
        sa.Column("request_id", sa.Unicode(40), nullable=False, server_default=""),
        sa.Column(
            "request_stats",
            sa.dialects.postgresql.JSON,
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "traceback",
            sa.dialects.postgresql.JSON,
            nullable=False,
            server_default="{}",
        ),
        sa.Column("traceback_hash", sa.Unicode(40), nullable=False, server_default=""),
        sa.Column(
            "start_time", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("end_time", sa.DateTime()),
        sa.Column(
            "report_group_time",
            sa.DateTime,
            index=True,
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("duration", sa.Float(), nullable=False, server_default="0"),
        sa.Column("http_status", sa.Integer, index=True),
        sa.Column("url_domain", sa.Unicode(128)),
        sa.Column("url_path", sa.UnicodeText),
        sa.Column("language", sa.Integer, server_default="0"),
    )
    op.create_index(None, "reports", [sa.text("(tags ->> 'server_name')")])
    op.create_index(None, "reports", [sa.text("(tags ->> 'view_name')")])

    op.create_table(
        "reports_assignments",
        sa.Column("group_id", sa.types.BigInteger, nullable=False, primary_key=True),
        sa.Column(
            "owner_id",
            sa.Integer,
            sa.ForeignKey("users.id", onupdate="cascade", ondelete="cascade"),
            nullable=False,
            primary_key=True,
        ),
        sa.Column("report_time", sa.DateTime, nullable=False),
    )

    op.create_table(
        "reports_comments",
        sa.Column("comment_id", sa.Integer, primary_key=True),
        sa.Column("body", sa.UnicodeText, nullable=False, server_default=""),
        sa.Column(
            "owner_id",
            sa.Integer,
            sa.ForeignKey("users.id", onupdate="cascade", ondelete="set null"),
            nullable=True,
        ),
        sa.Column(
            "created_timestamp",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("report_time", sa.DateTime, nullable=False),
        sa.Column("group_id", sa.types.BigInteger, nullable=False),
    )

    op.create_table(
        "reports_stats",
        sa.Column("resource_id", sa.Integer, nullable=False, index=True),
        sa.Column("start_interval", sa.DateTime, nullable=False, index=True),
        sa.Column("group_id", sa.types.BigInteger, index=True),
        sa.Column(
            "occurences", sa.Integer, nullable=False, server_default="0", index=True
        ),
        sa.Column("owner_user_id", sa.Integer),
        sa.Column("type", sa.Integer, index=True, nullable=False),
        sa.Column("duration", sa.Float(), server_default="0"),
        sa.Column("server_name", sa.Unicode(128), server_default=""),
        sa.Column("view_name", sa.Unicode(128), server_default=""),
        sa.Column("id", sa.BigInteger(), nullable=False, primary_key=True),
    )
    op.create_index(
        "ix_reports_stats_start_interval_group_id",
        "reports_stats",
        ["start_interval", "group_id"],
    )

    op.create_table(
        "slow_calls",
        sa.Column("id", sa.types.BigInteger, primary_key=True),
        sa.Column(
            "report_id",
            sa.types.BigInteger,
            sa.ForeignKey("reports.id", onupdate="cascade", ondelete="cascade"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "duration", sa.Float(), nullable=False, server_default="0", index=True
        ),
        sa.Column(
            "timestamp",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
            index=True,
        ),
        sa.Column(
            "report_group_time",
            sa.DateTime,
            index=True,
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("type", sa.Unicode(16), nullable=False, index=True),
        sa.Column("statement", sa.UnicodeText, nullable=False, server_default=""),
        sa.Column("parameters", sa.dialects.postgresql.JSON, nullable=False),
        sa.Column("location", sa.UnicodeText, server_default=""),
        sa.Column("subtype", sa.Unicode(16), nullable=False, index=True),
        sa.Column("resource_id", sa.Integer, nullable=False, index=True),
        sa.Column("statement_hash", sa.Unicode(60), index=True),
    )

    op.create_table(
        "tags",
        sa.Column("id", sa.types.BigInteger, primary_key=True),
        sa.Column(
            "resource_id",
            sa.Integer,
            sa.ForeignKey(
                "resources.resource_id", onupdate="cascade", ondelete="cascade"
            ),
        ),
        sa.Column(
            "first_timestamp", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "last_timestamp", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column("name", sa.Unicode(32), nullable=False),
        sa.Column("value", sa.dialects.postgresql.JSON, nullable=False),
        sa.Column("times_seen", sa.Integer, nullable=False, server_default="1"),
    )

    op.create_table(
        "auth_tokens",
        sa.Column("id", sa.Integer, nullable=False, primary_key=True),
        sa.Column("token", sa.Unicode),
        sa.Column(
            "creation_date", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column("expires", sa.DateTime),
        sa.Column(
            "owner_id",
            sa.Integer,
            sa.ForeignKey("users.id", onupdate="cascade", ondelete="cascade"),
        ),
        sa.Column("description", sa.Unicode),
    )

    op.create_table(
        "channels_actions",
        sa.Column(
            "channel_pkey",
            sa.Integer,
            sa.ForeignKey(
                "alert_channels.pkey", ondelete="CASCADE", onupdate="CASCADE"
            ),
        ),
        sa.Column(
            "action_pkey",
            sa.Integer,
            sa.ForeignKey(
                "alert_channels_actions.pkey", ondelete="CASCADE", onupdate="CASCADE"
            ),
        ),
    )

    op.create_table(
        "config",
        sa.Column("key", sa.Unicode(128), primary_key=True),
        sa.Column("section", sa.Unicode(128), primary_key=True),
        sa.Column("value", sa.dialects.postgresql.JSON, server_default="{}"),
    )

    op.create_table(
        "plugin_configs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("plugin_name", sa.Unicode(128)),
        sa.Column("section", sa.Unicode(128)),
        sa.Column("config", sa.dialects.postgresql.JSON, server_default="{}"),
        sa.Column(
            "resource_id",
            sa.Integer(),
            sa.ForeignKey(
                "resources.resource_id", onupdate="cascade", ondelete="cascade"
            ),
        ),
        sa.Column(
            "owner_id",
            sa.Integer(),
            sa.ForeignKey("users.id", onupdate="cascade", ondelete="cascade"),
        ),
    )

    op.create_table(
        "rc_versions",
        sa.Column("name", sa.Unicode(40), primary_key=True),
        sa.Column("value", sa.Unicode(40)),
    )
    version_table = sa.table(
        "rc_versions",
        sa.Column("name", sa.Unicode(40)),
        sa.Column("value", sa.Unicode(40)),
    )

    insert = version_table.insert().values(name="es_reports")
    op.execute(insert)
    insert = version_table.insert().values(name="es_reports_groups")
    op.execute(insert)
    insert = version_table.insert().values(name="es_reports_stats")
    op.execute(insert)
    insert = version_table.insert().values(name="es_logs")
    op.execute(insert)
    insert = version_table.insert().values(name="es_metrics")
    op.execute(insert)
    insert = version_table.insert().values(name="es_slow_calls")
    op.execute(insert)

    op.execute(
        """
        CREATE OR REPLACE FUNCTION floor_time_5min(timestamp without time zone)
          RETURNS timestamp without time zone AS
        $BODY$SELECT date_trunc('hour', $1) + INTERVAL '5 min' * FLOOR(date_part('minute', $1) / 5.0)$BODY$
          LANGUAGE sql VOLATILE;
    """
    )

    op.execute(
        """
    CREATE OR REPLACE FUNCTION partition_logs() RETURNS trigger
        LANGUAGE plpgsql SECURITY DEFINER
        AS $$
    DECLARE
    main_table         varchar := 'logs';
    partitioned_table  varchar := '';
    BEGIN

    IF NEW.permanent THEN
        partitioned_table := main_table || '_p_' || date_part('year', NEW.timestamp)::TEXT || '_' || DATE_part('month', NEW.timestamp);
    ELSE
        partitioned_table := main_table || '_p_' || date_part('year', NEW.timestamp)::TEXT || '_' || DATE_part('month', NEW.timestamp) || '_' || DATE_part('day', NEW.timestamp);
    END IF;

    BEGIN
    EXECUTE 'INSERT INTO ' || partitioned_table || ' SELECT(' || TG_TABLE_NAME || ' ' || quote_literal(NEW) || ').*;';
    EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'A partition has been created %', partitioned_table;
        IF NEW.permanent THEN
        EXECUTE format('CREATE TABLE  IF NOT EXISTS %s ( CHECK( timestamp >= DATE %s AND timestamp < DATE %s)) INHERITS (%s)',
                partitioned_table,
                quote_literal(date_trunc('month', NEW.timestamp)::date) ,
                quote_literal((date_trunc('month', NEW.timestamp)::date  + interval '1 month')::text),
                main_table);
        EXECUTE format('ALTER TABLE %s ADD CONSTRAINT pk_%s PRIMARY KEY(log_id);', partitioned_table, partitioned_table);
        EXECUTE format('ALTER TABLE %s ADD CONSTRAINT fk_%s_resource_id FOREIGN KEY (resource_id) REFERENCES resources (resource_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;', partitioned_table, partitioned_table);
        EXECUTE format('CREATE INDEX ix_%s_timestamp ON %s (timestamp);', partitioned_table, partitioned_table);
        EXECUTE format('CREATE INDEX ix_%s_namespace_resource_id ON %s (namespace, resource_id);', partitioned_table, partitioned_table);
        EXECUTE format('CREATE INDEX ix_%s_resource_id ON %s (resource_id);', partitioned_table, partitioned_table);
        EXECUTE format('CREATE INDEX ix_%s_pkey_namespace ON %s (primary_key, namespace);', partitioned_table, partitioned_table);
        ELSE
        EXECUTE format('CREATE TABLE  IF NOT EXISTS %s ( CHECK( timestamp >= DATE %s AND timestamp < DATE %s)) INHERITS (%s)',
                partitioned_table,
                quote_literal(date_trunc('day', NEW.timestamp)::date) ,
                quote_literal((date_trunc('day', NEW.timestamp)::date  + interval '1 day')::text),
                main_table);
        EXECUTE format('ALTER TABLE %s ADD CONSTRAINT pk_%s_ PRIMARY KEY(log_id);', partitioned_table, partitioned_table);
        EXECUTE format('ALTER TABLE %s ADD CONSTRAINT fk_%s_resource_id FOREIGN KEY (resource_id) REFERENCES resources (resource_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;', partitioned_table, partitioned_table);
        EXECUTE format('CREATE INDEX ix_%s_timestamp ON %s (timestamp);', partitioned_table, partitioned_table);
        EXECUTE format('CREATE INDEX ix_%s_namespace_resource_id ON %s (namespace, resource_id);', partitioned_table, partitioned_table);
        EXECUTE format('CREATE INDEX ix_%s_resource_id ON %s (resource_id);', partitioned_table, partitioned_table);
        EXECUTE format('CREATE INDEX ix_%s_primary_key_namespace ON %s (primary_key,namespace);', partitioned_table, partitioned_table);
        END IF;


        EXECUTE 'INSERT INTO ' || partitioned_table || ' SELECT(' || TG_TABLE_NAME || ' ' || quote_literal(NEW) || ').*;';
    END;


    RETURN NULL;
    END
    $$;
    """
    )

    op.execute(
        """
    CREATE TRIGGER partition_logs BEFORE INSERT ON logs FOR EACH ROW EXECUTE PROCEDURE partition_logs();
    """
    )

    op.execute(
        """
    CREATE OR REPLACE FUNCTION partition_metrics() RETURNS trigger
        LANGUAGE plpgsql SECURITY DEFINER
        AS $$
        DECLARE
        main_table         varchar := 'metrics';
        partitioned_table  varchar := '';
        BEGIN

        partitioned_table := main_table || '_p_' || date_part('year', NEW.timestamp)::TEXT || '_' || DATE_part('month', NEW.timestamp) || '_' || DATE_part('day', NEW.timestamp);

    BEGIN
    EXECUTE 'INSERT INTO ' || partitioned_table || ' SELECT(' || TG_TABLE_NAME || ' ' || quote_literal(NEW) || ').*;';
    EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'A partition has been created %', partitioned_table;
        EXECUTE format('CREATE TABLE  IF NOT EXISTS %s ( CHECK( timestamp >= DATE %s AND timestamp < DATE %s)) INHERITS (%s)',
                partitioned_table,
                quote_literal(date_trunc('day', NEW.timestamp)::date) ,
                quote_literal((date_trunc('day', NEW.timestamp)::date  + interval '1 day')::text),
                main_table);
        EXECUTE format('ALTER TABLE %s ADD CONSTRAINT pk_%s PRIMARY KEY(pkey);', partitioned_table, partitioned_table);
        EXECUTE format('ALTER TABLE %s ADD CONSTRAINT fk_%s_resource_id FOREIGN KEY (resource_id) REFERENCES resources (resource_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;', partitioned_table, partitioned_table);
        EXECUTE format('CREATE INDEX ix_%s_timestamp ON %s (timestamp);', partitioned_table, partitioned_table);
        EXECUTE format('CREATE INDEX ix_%s_resource_id ON %s (resource_id);', partitioned_table, partitioned_table);
        EXECUTE 'INSERT INTO ' || partitioned_table || ' SELECT(' || TG_TABLE_NAME || ' ' || quote_literal(NEW) || ').*;';
    END;

    RETURN NULL;
    END
    $$;
    """
    )

    op.execute(
        """
    CREATE TRIGGER partition_metrics BEFORE INSERT ON metrics FOR EACH ROW EXECUTE PROCEDURE partition_metrics();
    """
    )

    op.execute(
        """
    CREATE FUNCTION partition_reports_stats() RETURNS trigger
        LANGUAGE plpgsql SECURITY DEFINER
        AS $$
        DECLARE
            main_table         varchar := 'reports_stats';
            partitioned_table  varchar := '';
        BEGIN

            partitioned_table := main_table || '_p_' || date_part('year', NEW.start_interval)::TEXT || '_' || DATE_part('month', NEW.start_interval);

            BEGIN
                EXECUTE 'INSERT INTO ' || partitioned_table || ' SELECT(' || TG_TABLE_NAME || ' ' || quote_literal(NEW) || ').*;';
            EXCEPTION
            WHEN undefined_table THEN
                RAISE NOTICE 'A partition has been created %', partitioned_table;
                EXECUTE format('CREATE TABLE  IF NOT EXISTS %s ( CHECK( start_interval >= DATE %s AND start_interval < DATE %s )) INHERITS (%s)',
                    partitioned_table,
                    quote_literal(date_trunc('month', NEW.start_interval)::date) ,
                    quote_literal((date_trunc('month', NEW.start_interval)::date  + interval '1 month')::text),
                    main_table);
                EXECUTE format('ALTER TABLE %s ADD CONSTRAINT pk_%s PRIMARY KEY(id);', partitioned_table, partitioned_table);
                EXECUTE format('CREATE INDEX ix_%s_start_interval ON %s USING btree (start_interval);', partitioned_table, partitioned_table);
                EXECUTE format('CREATE INDEX ix_%s_type ON %s USING btree (type);', partitioned_table, partitioned_table);
                EXECUTE format('CREATE INDEX ix_%s_resource_id ON %s USING btree (resource_id);', partitioned_table, partitioned_table);
                EXECUTE 'INSERT INTO ' || partitioned_table || ' SELECT(' || TG_TABLE_NAME || ' ' || quote_literal(NEW) || ').*;';
            END;
            RETURN NULL;
        END
        $$;
    """
    )

    op.execute(
        """
    CREATE TRIGGER partition_reports_stats BEFORE INSERT ON reports_stats FOR EACH ROW EXECUTE PROCEDURE partition_reports_stats();
    """
    )

    op.execute(
        """
    CREATE OR REPLACE FUNCTION partition_reports_groups() RETURNS trigger
        LANGUAGE plpgsql SECURITY DEFINER
        AS $$
    DECLARE
        main_table         varchar := 'reports_groups';
        partitioned_table  varchar := '';
    BEGIN

        partitioned_table := main_table || '_p_' || date_part('year', NEW.first_timestamp)::TEXT || '_' || DATE_part('month', NEW.first_timestamp);

        BEGIN
            EXECUTE 'INSERT INTO ' || partitioned_table || ' SELECT(' || TG_TABLE_NAME || ' ' || quote_literal(NEW) || ').*;';
        EXCEPTION
        WHEN undefined_table THEN
            RAISE NOTICE 'A partition has been created %', partitioned_table;
            EXECUTE format('CREATE TABLE  IF NOT EXISTS %s ( CHECK( first_timestamp >= DATE %s AND first_timestamp < DATE %s )) INHERITS (%s)',
                partitioned_table,
                quote_literal(date_trunc('month', NEW.first_timestamp)::date) ,
                quote_literal((date_trunc('month', NEW.first_timestamp)::date  + interval '1 month')::text),
                main_table);
            EXECUTE format('ALTER TABLE %s ADD CONSTRAINT pk_%s PRIMARY KEY(id);', partitioned_table, partitioned_table);
            EXECUTE format('ALTER TABLE %s ADD CONSTRAINT fk_%s_resource_id FOREIGN KEY (resource_id) REFERENCES resources (resource_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;', partitioned_table, partitioned_table);
            EXECUTE 'INSERT INTO ' || partitioned_table || ' SELECT(' || TG_TABLE_NAME || ' ' || quote_literal(NEW) || ').*;';
        END;
        RETURN NULL;
    END
    $$;
    """
    )

    op.execute(
        """
    CREATE TRIGGER partition_reports_groups BEFORE INSERT ON reports_groups FOR EACH ROW EXECUTE PROCEDURE partition_reports_groups();
    """
    )

    op.execute(
        """
    CREATE OR REPLACE FUNCTION partition_reports() RETURNS trigger
        LANGUAGE plpgsql SECURITY DEFINER
        AS $$
    DECLARE
        main_table         varchar := 'reports';
        partitioned_table  varchar := '';
        partitioned_parent_table  varchar := '';
    BEGIN

        partitioned_table := main_table || '_p_' || date_part('year', NEW.report_group_time)::TEXT || '_' || DATE_part('month', NEW.report_group_time);
        partitioned_parent_table := 'reports_groups_p_' || date_part('year', NEW.report_group_time)::TEXT || '_' || DATE_part('month', NEW.report_group_time);

        BEGIN
            EXECUTE 'INSERT INTO ' || partitioned_table || ' SELECT(' || TG_TABLE_NAME || ' ' || quote_literal(NEW) || ').*;';
        EXCEPTION
        WHEN undefined_table THEN
            RAISE NOTICE 'A partition has been created %', partitioned_table;
            EXECUTE format('CREATE TABLE  IF NOT EXISTS %s ( CHECK( report_group_time >= DATE %s AND report_group_time < DATE %s )) INHERITS (%s)',
                partitioned_table,
                quote_literal(date_trunc('month', NEW.report_group_time)::date) ,
                quote_literal((date_trunc('month', NEW.report_group_time)::date  + interval '1 month')::text),
                main_table);
            EXECUTE format('ALTER TABLE %s ADD CONSTRAINT pk_%s PRIMARY KEY(id);', partitioned_table, partitioned_table);
            EXECUTE format('ALTER TABLE %s ADD CONSTRAINT fk_%s_resource_id FOREIGN KEY (resource_id) REFERENCES resources (resource_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;', partitioned_table, partitioned_table);
            EXECUTE format('ALTER TABLE %s ADD CONSTRAINT fk_%s_group_id FOREIGN KEY (group_id) REFERENCES %s (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;', partitioned_table, partitioned_table, partitioned_parent_table);
            EXECUTE format('CREATE INDEX ix_%s_report_group_time ON %s USING btree (report_group_time);', partitioned_table, partitioned_table);
            EXECUTE format('CREATE INDEX ix_%s_group_id ON %s USING btree (group_id);', partitioned_table, partitioned_table);
            EXECUTE format('CREATE INDEX ix_%s_resource_id ON %s USING btree (resource_id);', partitioned_table, partitioned_table);
            EXECUTE 'INSERT INTO ' || partitioned_table || ' SELECT(' || TG_TABLE_NAME || ' ' || quote_literal(NEW) || ').*;';
        END;
        RETURN NULL;
    END
    $$;
    """
    )

    op.execute(
        """
    CREATE TRIGGER partition_reports BEFORE INSERT ON reports FOR EACH ROW EXECUTE PROCEDURE partition_reports();
    """
    )

    op.execute(
        """
    CREATE OR REPLACE FUNCTION partition_slow_calls() RETURNS trigger
        LANGUAGE plpgsql SECURITY DEFINER
        AS $$
    DECLARE
        main_table         varchar := 'slow_calls';
        partitioned_table  varchar := '';
        partitioned_parent_table  varchar := '';
    BEGIN

        partitioned_table := main_table || '_p_' || date_part('year', NEW.report_group_time)::TEXT || '_' || DATE_part('month', NEW.report_group_time);
        partitioned_parent_table := 'reports_p_' || date_part('year', NEW.report_group_time)::TEXT || '_' || DATE_part('month', NEW.report_group_time);

        BEGIN
            EXECUTE 'INSERT INTO ' || partitioned_table || ' SELECT(' || TG_TABLE_NAME || ' ' || quote_literal(NEW) || ').*;';
        EXCEPTION
        WHEN undefined_table THEN
            RAISE NOTICE 'A partition has been created %', partitioned_table;
            EXECUTE format('CREATE TABLE  IF NOT EXISTS %s ( CHECK( report_group_time >= DATE %s AND report_group_time < DATE %s )) INHERITS (%s)',
                partitioned_table,
                quote_literal(date_trunc('month', NEW.report_group_time)::date) ,
                quote_literal((date_trunc('month', NEW.report_group_time)::date  + interval '1 month')::text),
                main_table);
            EXECUTE format('ALTER TABLE %s ADD CONSTRAINT pk_%s PRIMARY KEY(id);', partitioned_table, partitioned_table);
            EXECUTE format('ALTER TABLE %s ADD CONSTRAINT fk_%s_resource_id FOREIGN KEY (resource_id) REFERENCES resources (resource_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;', partitioned_table, partitioned_table);
            EXECUTE format('ALTER TABLE %s ADD CONSTRAINT fk_%s_report_id FOREIGN KEY (report_id) REFERENCES %s (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;', partitioned_table, partitioned_table, partitioned_parent_table);
            EXECUTE format('CREATE INDEX ix_%s_resource_id  ON %s USING btree (resource_id);', partitioned_table, partitioned_table);
            EXECUTE format('CREATE INDEX ix_%s_report_id ON %s USING btree (report_id);', partitioned_table, partitioned_table);
            EXECUTE format('CREATE INDEX ix_%s_timestamp ON %s USING btree (timestamp);', partitioned_table, partitioned_table);
            EXECUTE 'INSERT INTO ' || partitioned_table || ' SELECT(' || TG_TABLE_NAME || ' ' || quote_literal(NEW) || ').*;';
        END;
        RETURN NULL;
    END
    $$;
    """
    )

    op.execute(
        """
    CREATE TRIGGER partition_slow_calls BEFORE INSERT ON slow_calls FOR EACH ROW EXECUTE PROCEDURE partition_slow_calls();
    """
    )


def downgrade():
    pass
