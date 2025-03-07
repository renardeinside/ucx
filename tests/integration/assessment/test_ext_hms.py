import dataclasses
import datetime as dt

from databricks.labs.lsql.backends import CommandExecutionBackend
from databricks.sdk.service.iam import PermissionLevel


def test_running_real_assessment_job_ext_hms(
    ws,
    installation_ctx,
    env_or_skip,
    make_cluster_policy,
    make_cluster_policy_permissions,
):
    cluster_id = env_or_skip('TEST_EXT_HMS_CLUSTER_ID')
    ext_hms_ctx = installation_ctx.replace(
        sql_backend=CommandExecutionBackend(ws, cluster_id),
        config_transform=lambda wc: dataclasses.replace(
            wc,
            override_clusters=None,
        ),
        extend_prompts={
            r"Instance pool id to be set.*": env_or_skip("TEST_INSTANCE_POOL_ID"),
            r".*Do you want to update the existing installation?.*": 'yes',
            r".*connect to the external metastore?.*": "yes",
            r"Choose a cluster policy": "0",
        },
    )
    ws_group_a, _ = ext_hms_ctx.make_ucx_group(wait_for_provisioning=True)

    cluster_policy = make_cluster_policy()
    make_cluster_policy_permissions(
        object_id=cluster_policy.policy_id,
        permission_level=PermissionLevel.CAN_USE,
        group_name=ws_group_a.display_name,
    )
    ext_hms_ctx.__dict__['include_object_permissions'] = [f"cluster-policies:{cluster_policy.policy_id}"]
    ext_hms_ctx.workspace_installation.run()

    # Under ideal circumstances this can take 10-16 minutes (depending on whether there are compute instances available
    # via the integration pool). Allow some margin to reduce spurious failures.
    ext_hms_ctx.deployed_workflows.run_workflow("assessment", max_wait=dt.timedelta(minutes=25))

    # assert the workflow is successful. the tasks on sql warehouse will fail so skip checking them
    assert ext_hms_ctx.deployed_workflows.validate_step("assessment")

    after = ext_hms_ctx.generic_permissions_support.load_as_dict("cluster-policies", cluster_policy.policy_id)
    assert ws_group_a.display_name in after, f"Group {ws_group_a.display_name} not found in cluster policy"
    assert after[ws_group_a.display_name] == PermissionLevel.CAN_USE
