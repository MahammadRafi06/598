import uuid
from azure.ai.ml.entities import ManagedOnlineEndpoint
from azure.ai.ml.entities import ManagedOnlineDeployment
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential


# authenticate
credential = DefaultAzureCredential()

# Get a handle to the workspace
ml_client = MLClient(
    credential=credential,
    subscription_id="fa87b981-3938-42ad-8bc6-6970be4e7a96",
    resource_group_name="project",
    workspace_name="589project",
)


registered_model_name = "598"

online_endpoint_name = "premiumservice-endpoint-" + str(uuid.uuid4())[:8]
latest_model_version = "1"

try:
    endpoint = ml_client.online_endpoints.get(name=online_endpoint_name)
except Exception as e:

    endpoint = ManagedOnlineEndpoint(
        name=online_endpoint_name,
        description="This is an online endpoint for Carplab Premium Services",
        auth_mode="key",
        tags={
            "Production": "PremiumServices",
        },
    )

    endpoint = ml_client.online_endpoints.begin_create_or_update(endpoint).result()

    model = ml_client.models.get(name=registered_model_name, version=latest_model_version)

    blue_deployment = ManagedOnlineDeployment(
        name="blue",
        endpoint_name=online_endpoint_name,
        model=model,
        instance_type="Standard_D2as_v4",
        instance_count=1,
    )
    blue_deployment = ml_client.online_deployments.begin_create_or_update(
        blue_deployment
    ).result()

    endpoint.traffic = {"blue": 100}
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()