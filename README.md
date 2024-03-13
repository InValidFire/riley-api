# Riley's API

Personal API used for personal website guestbook service, status log, and more!
Currently a work in progress.

## Planned Features
- Authenticate with IndieLogin, enabling users to manage their website interactivity.
  - Create posts to a status log that can be embedded to a website.
  - Manage guestbook comments and ban users (via IP address) if necessary.
- Admin users can delete users and view other user data.
- Anyone can comment on a user's guestbook via POST requests.
- Store Minecraft stats by username for display on a personal website.

## Deployment

The application can be deployed using `uvicorn` following the instructions here: https://fastapi.tiangolo.com/deployment/manually/

You should use another service such as Docker or systemd to manage the process.
A guide for deployment shall be added at a later date.

## TO-DO
- Split main.py into FastAPI Routers for more structure
- Get OAuth and session management 100% working (almost there!)