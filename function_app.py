import logging
import azure.functions as func
from datetime import datetime, time
import pytz
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient

app = func.FunctionApp()
load_dotenv()

# Access the environment variables
subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
res_group_name = os.getenv('RESOURCE_GROUP_NAME')
debug_mode = os.getenv('DEBUG_MODE')
run_at_startup = debug_mode == 'True'                   # This way the function runs when testing locally but not in production

# make the schedule
#sched = "0 0 11 * * *"  # 11:00 AM UTC --> 6:00 AM EST

# Test schedule - run every minute
sched = "0 * * * * *"

@app.schedule(schedule=sched, arg_name="myTimer", run_on_startup=run_at_startup,
              use_monitor=False) 
def CS2ContainerPrune(myTimer: func.TimerRequest) -> None:
    # if myTimer.past_due:
    #     # Convert current UTC time to EST
    #     current_time = datetime.now(pytz.timezone('US/Eastern')).time()

    #     # Define the time range
    #     start_time = time(6, 0)  # 6:00 AM
    #     end_time = time(13, 0)  # 1:00 PM
    #     logging.info('The timer is past due!')

    #     # Check if the current time outside the time range
    #     if current_time < start_time or current_time > end_time:
    #         logging.info('The timer is not within the time range. Exiting the function.')
    #         return

    # Authenticate and create a client
    credentials = DefaultAzureCredential(
        exclude_visual_studio_code_credential=True,
        exclude_visual_studio_credential=True
    )

    client = ContainerInstanceManagementClient(credentials, subscription_id)

    # List all container groups in the resource group
    container_groups = client.container_groups.list_by_resource_group(res_group_name)

    # Iterate over the container groups
    for container_group in container_groups:
        if ('cs2containergroup' in container_group.name):

            # TODO: If ever we feel so inclined we can add more logic here to RCON into the server and check if it's empty

            # Delete the container group
            logging.info(f"Deleting the container group: {container_group.name}")
            client.container_groups.begin_delete(res_group_name, container_group.name)