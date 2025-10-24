# morpc-purpleair-fetch

This repository stores the process for fetching air quality data from the purple air API and storing it in a local sqlite database. 

## Introduction

In July 2025, MORPC Data Team began a process to update process which fetched, stored, and process air quaility sensor data. At the time, Ramboll was collecting data from the purple air API and MORPC was getting data from their Google Cloud database (see [morpc-airquality-shair(](https://github.com/morpc/morpc-airquality-shair)). This script fetches data from three sources (data previously stored locally on MORPC Sharepoint, Ramboll data, and PurpleAir API sensor) and stores them in a SQLite database with SpatiaLite extionsion support. 

## Roadmap

 - [ ] 1. Develop air quality sensor model for sqlite database, including Sensor Deployment Tracking sheet.
 - [ ] 2. Fetch script for Ramboll database and input into MORPC sqlite database.
 - [ ] 3. Input data from MORPC sharepoint into sqlite database. This may also act as a script for manual downloads using the [PurpleAir Data Download tool](https://gitlab.com/purpleair-api-clients/data-download-tool/-/tree/main)
 - [X] 4. Fetch data directly from PurpleAir API.
 - [ ] 5. Automate fetch to pull data from PurpleAir.
