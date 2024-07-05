# Python Reminder App
A simple project created by Satej Gandre to demonstrate a small portion of what the University of Michigan's course on Python Databases teaches the student.

## Installation
To install the reminder app on your machine, simply download the .zip file from this github repository. Extracting the files will reveal 3 core components: `structure.py`, `data.db`, and  `tasks.htm`. The last two files can be deleted without error, but doing so would erase the data vital to the app's performance.
## Instructions
To use the reminder app, launch the file `structure.py` with a python interpreter. This would prompt the user to enter ana ction command. There are 5 options for the user to pick. The user can either `CREATE` a task, `VIEW` all tasks (which simply updates the file tasks.htm with the task data in the form of a table), `UPDATE` the status of a task (0 is NOT STARTED, 1 is IN PROGRESS, 2 is COMPLETED), and lastly the user can `DELETE` a task given its activity ID. Additionally, the user can `QUIT` the application, terminating the connection with the database whilst also retaining the data.
