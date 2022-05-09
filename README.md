# project_linux_backend

This is the back-end of the web app for user deck management. Where a user can manage simple CRUD operations
on decks that can be used for simple memory training.
- It has been developed using flask. 
- sqlite database used for development benefits.
- redis-server used for task queues and caching.

# run on linux

```
sh local_setup.sh
sh local_run.sh
sh local_workers.sh
sh local_beat.sh
```
