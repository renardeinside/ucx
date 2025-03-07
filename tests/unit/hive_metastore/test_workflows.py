import pytest
from databricks.labs.ucx.hive_metastore.workflows import (
    TableMigration,
    MigrateExternalTablesCTAS,
    MigrateHiveSerdeTablesInPlace,
    MigrateTablesInMounts,
    ScanTablesInMounts,
)


def test_migrate_external_tables_sync(run_workflow):
    ctx = run_workflow(TableMigration.migrate_external_tables_sync)
    ctx.workspace_client.catalogs.list.assert_called_once()


def test_migrate_dbfs_root_delta_tables(run_workflow):
    ctx = run_workflow(TableMigration.migrate_dbfs_root_delta_tables)
    ctx.workspace_client.catalogs.list.assert_called_once()


def test_migrate_dbfs_root_non_delta_tables(run_workflow):
    ctx = run_workflow(TableMigration.migrate_dbfs_root_non_delta_tables)
    ctx.workspace_client.catalogs.list.assert_called_once()


def test_migrate_tables_views(run_workflow):
    ctx = run_workflow(TableMigration.migrate_views)
    ctx.workspace_client.catalogs.list.assert_called()


def test_migrate_hive_serde_in_place(run_workflow):
    ctx = run_workflow(MigrateHiveSerdeTablesInPlace.migrate_hive_serde_in_place)
    ctx.workspace_client.catalogs.list.assert_called_once()


def test_migrate_hive_serde_views(run_workflow):
    ctx = run_workflow(MigrateHiveSerdeTablesInPlace.migrate_views)
    ctx.workspace_client.catalogs.list.assert_called()


def test_migrate_other_external_ctas(run_workflow):
    ctx = run_workflow(MigrateExternalTablesCTAS.migrate_other_external_ctas)
    ctx.workspace_client.catalogs.list.assert_called_once()


def test_migrate_hive_serde_ctas(run_workflow):
    ctx = run_workflow(MigrateExternalTablesCTAS.migrate_hive_serde_ctas)
    ctx.workspace_client.catalogs.list.assert_called_once()


def test_migrate_ctas_views(run_workflow):
    ctx = run_workflow(MigrateExternalTablesCTAS.migrate_views)
    ctx.workspace_client.catalogs.list.assert_called()


@pytest.mark.parametrize(
    "workflow",
    [
        TableMigration,
        MigrateHiveSerdeTablesInPlace,
        MigrateExternalTablesCTAS,
        ScanTablesInMounts,
        MigrateTablesInMounts,
    ],
)
def test_update_migration_status(run_workflow, workflow):
    """Migration status is refreshed by deleting and showing new tables"""
    ctx = run_workflow(getattr(workflow, "update_migration_status"))
    assert "TRUNCATE TABLE hive_metastore.ucx.migration_status" in ctx.sql_backend.queries
    assert "SHOW DATABASES" in ctx.sql_backend.queries
