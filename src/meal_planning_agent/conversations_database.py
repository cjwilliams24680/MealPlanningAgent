import asyncio

import aioboto3

from meal_planning_agent.utils import assert_key_exists

AWS_REGION = assert_key_exists("AWS_REGION")

TABLE_NAME = assert_key_exists("CONVERSATIONS_DB_NAME")
ENDPOINT_URL = f"http://{assert_key_exists('CONVERSATIONS_DB_ENDPOINT')}"

SESSION = aioboto3.Session(
    aws_access_key_id=assert_key_exists("CONVERSATIONS_DB_USERNAME"),
    aws_secret_access_key=assert_key_exists("CONVERSATIONS_DB_PASSWORD"),
    region_name=AWS_REGION,
)


def get_resource():
    return SESSION.resource("dynamodb", endpoint_url=ENDPOINT_URL)


async def create_db_and_tables():
    async with SESSION.client("dynamodb", endpoint_url=ENDPOINT_URL) as client:
        try:
            await client.create_table(
                TableName=TABLE_NAME,
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST",
            )
        except client.exceptions.ResourceInUseException:
            return

        while True:
            description = await client.describe_table(TableName=TABLE_NAME)
            if description["Table"]["TableStatus"] == "ACTIVE":
                return
            await asyncio.sleep(0.5)
