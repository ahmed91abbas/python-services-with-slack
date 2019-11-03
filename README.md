
# Python Services With Slack
A Slack bot with several services. Once the application is running you can invite your bot to any Workspace and start taking advantage of the services it provides. More on the services available can be found once the app is running.

## Setup
### Creating the Slack App
1. Start by creating a [new Slack App](https://api.slack.com/apps/new) for your workspace
2. In the settings page you'll find the **Bot Users** tab where you can setup a new **Bot User** in order to enable our newly created app to communicate on Slack.
3. Navigate to **OAuth & Permissions** tab in the setting page and note down the **Bot User OAuth Access Token** as we are going to need that later.

### Preparing the run environment
1. Create a new virtual environment running the following commands from the root of your project directory:

        virtualenv env
2. Activate your new virtual environment:

        source env/bin/activate
3. Install all the Python packages needed for this application:

        pip install -r requirements.txt

### Creating the app resources
1. Create SQLite database which is going to be used by the app services:

        python db/create_db.py
    This will create a new database file called *services_db.db*
2. Rename *.env.example* to *.env* and edit the values inside it:

    * **SERVICES_BOT_ACCESS_TOKEN** value should be the **Bot User OAuth Access Token** you noted when you created the Slack app.
    * **DB_FILE** value is the absolute path to *services_db.db* which have been created in the previous step.

## Run the application
Now all what is left is to run the application:

        python app.py
You should see the Bot status as online now. The Bot will listen to all channels it is invited to.
Start by sending the message `Help` to get a list of available services.

All done :tada: now you can take advantage of all the services this Slack Bot provides.
