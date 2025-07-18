# Snipper-Snippets-API

## Activity Overview
You have been contracted to produce Snippr, a tool which allows users to save their useful code snippets. You will be making an MVP.
**GOAL:** Create endpoints to POST code snippets and then GET them back.
***

## Specification
#### User Stories
As a user, I can add a snippet to the data store, so that I can look it up again when I need it
As a user, I can request a snippet by its ID, so that I can see the snippet again

#### Functional Requirements
- Users can make POST request to /snippets to create a new snippet
- Users can make a GET request to /snippets to get all the snippets currently in the data store
- Users can make a GET request to e.g. /snippets/3 to retrieve the snippet with the ID of 3
- Bonus: Users can make a GET request to e.g. /snippets?lang=python to retrieve all the Python snippets
***
