#### NOTE: This is a rough draft. Formal steps and terms have been used at certain places, but not all.

### Bistro_Bookie

- This repository contains the source code and a brief documentation for a `Restaurant Reservation System` built using Django, Telegram, Google App Engine, Google Datastore and Google Memcached, among others.

- The bot was built using following tech/libraries:

```
    1. Telegram's APIs - Using python-telegram-bot
    2. Google App Engine - A PaaS offering by Google used for deploying and running applications in the cloud.
    3. Google Datastore - A NoSQL database that does not work on the Relational Model but stores data as documents.(`Using NDB API`)
    4. Google Memcache - A Caching System to cache an application's data for temporary periods of frequent access.
    5. Django - A high level Web Application Framework.
```

### Deployment

- It is expected here that the `reader` is familiar with:

```
    a. Google App Engine Concepts
    b. Understanding of how Python Applications are deployed and run on the Google App Engine.
    c. Google Memcache
    d. Google Datastore, Concept of Index in Google Datastore.
```

- To deploy this application, following steps must be followed(In Broad Outline)

```
    1. Create a Google App Engine Project.
    2. Enable API Access to relevant services - 
        a. Google App Engine
        b. Google Memcache
        c. Google Datastore
    3. Install gcloud-sdk for your platform and install relevant python libraries.
    4. Create a local gcloud sdk configuration.
    5. Configure Local gCloud SDK to use the project created in Step 1 as the default project.
    5. Create indexes for this project using the following command:
        gcloud datastore create-indexes index.yaml 
    6. Deploy the application using the following command:
        gcloud app deploy
```

### Usage

- This bot can be used to book a table for people at a Fictional restaurant named `The Bistro` using the Telegram Platform.

- Please install the `Telegram` messaging app on your device and search for `@bistro_bookie_bot` to get started with your reservation.

- User interaction takes place using commands and User Inputs are requested, wherever needed.
