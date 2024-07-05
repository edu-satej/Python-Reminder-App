import sqlite3 as sql

class Database:
    def __init__(self, file):
        self.conn = sql.connect(file)
        self.cur = self.conn.cursor()
        self._initialize_tables()

    def _initialize_tables(self):
        self.cur.execute('''
        CREATE TABLE IF NOT EXISTS "activities" (
        "id"    INTEGER NOT NULL UNIQUE,
        "task_id"    INTEGER,
        "time"    TEXT,
        "status"    INTEGER,
        PRIMARY KEY("id" AUTOINCREMENT))
        ''')
        self.cur.execute('''
        CREATE TABLE IF NOT EXISTS "tasks" (
        "id"    INTEGER NOT NULL UNIQUE,
        "desc"    TEXT,
        PRIMARY KEY("id" AUTOINCREMENT))
        ''')

    def query(self, cmd, params=None):
        try:
            if params:
                self.cur.execute(cmd, params)
            else:
                self.cur.execute(cmd)
            self.conn.commit()
            return self.cur.fetchone()
        except sql.Error as e:
            print(f"An error occurred: {e}")
            return None

    def query_all(self, cmd, params=None):
        try:
            if params:
                self.cur.execute(cmd, params)
            else:
                self.cur.execute(cmd)
            self.conn.commit()
            return self.cur.fetchall()
        except sql.Error as e:
            print(f"An error occurred: {e}")
            return None

    def silentquery(self, cmd, params=None):
        try:
            if params:
                self.cur.execute(cmd, params)
            else:
                self.cur.execute(cmd)
            self.conn.commit()
        except sql.Error as e:
            print(f"An error occurred: {e}")

    def __del__(self):
        self.cur.close()
        self.conn.close()

class Time:
    def __init__(self, time_str):
        self.hours, self.minutes, self.sign = self._parse_time(time_str)
        self.hours24 = self._convert_to_24_hour_format()
        self.realtime = self.hours24 * 60 + self.minutes

    def _parse_time(self, time_str):
        hours, minutes = map(int, time_str.split()[0].split(":"))
        sign = time_str.split()[1]
        return hours, minutes, sign

    def _convert_to_24_hour_format(self):
        if self.sign == "PM" and self.hours != 12:
            return self.hours + 12
        elif self.sign == "AM" and self.hours == 12:
            return 0
        else:
            return self.hours

    def decode(self, total_minutes):
        total_minutes = int(total_minutes)
        sign = "PM" if total_minutes >= 720 else "AM"
        hours = (total_minutes // 60) % 12
        hours = 12 if hours == 0 else hours
        minutes = total_minutes % 60
        return f"{hours}:{minutes:02d} {sign}"

class TaskManager:
    def __init__(self, db):
        self.db = db

    def create_task(self, task_desc, time_str):
        time = Time(time_str)
        if not self.db.query("SELECT * FROM tasks WHERE desc = ?", (task_desc,)):
            self.db.silentquery("INSERT INTO tasks (desc) VALUES (?)", (task_desc,))
        task_id = self.db.query("SELECT id FROM tasks WHERE desc = ?", (task_desc,))[0]
        self.db.silentquery("INSERT INTO activities (task_id, time, status) VALUES (?, ?, ?)", (task_id, time.realtime, 0))

    def read_task(self, activity_id):
        activity = self.db.query("SELECT * FROM activities WHERE id = ?", (activity_id,))
        if activity:
            task_id, raw_time, status = activity[1], activity[2], activity[3]
            task_desc = self.db.query("SELECT desc FROM tasks WHERE id = ?", (task_id,))[0]
            time = Time("12:00 AM").decode(raw_time)
            status_str = ["NOT STARTED", "IN PROGRESS", "COMPLETED"][status]
            return {"task": task_desc, "time": time, "status": status_str}
        return None

    def read_all_tasks(self):
        tasks = self.db.query_all('''
        SELECT activities.id, tasks.desc, activities.time, activities.status
        FROM activities
        JOIN tasks ON activities.task_id = tasks.id
        ''')
        result = []
        if tasks:
            for task in tasks:
                task_id, task_desc, raw_time, status = task
                time = Time("12:00 AM").decode(raw_time)
                status_str = ["NOT STARTED", "IN PROGRESS", "COMPLETED"][status]
                result.append({"id": task_id, "task": task_desc, "time": time, "status": status_str})
        return result

    def generate_html_table(self):
        tasks = self.read_all_tasks()
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
        <title>Python Tasks App</title>
        <style>
        html, body {
            height: 100%;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: Arial, sans-serif;
            text-align: center;
        }
        </style>
        </head>
        <body>
        <table border="1">
            <tr>
                <th>ID</th>
                <th>Task</th>
                <th>Time</th>
                <th>Status</th>
            </tr>
        '''
        for task in tasks:
            html += f'''
            <tr>
                <td>{task["id"]}</td>
                <td>{task["task"]}</td>
                <td>{task["time"]}</td>
                <td>{task["status"]}</td>
            </tr>
            '''
        html += '</table></body></html>'
        return html

    def update_status(self, activity_id, new_status):
        self.db.silentquery("UPDATE activities SET status = ? WHERE id = ?", (new_status, activity_id))

    def delete_task(self, activity_id):
        self.db.silentquery("DELETE FROM activities WHERE id = ?", (activity_id,))
        
taskDB = Database("data.db")
shell = TaskManager(taskDB)

while True:
    action = input("ACTION?\n>").lower()
    if action == "create":
        desc = input("TASK DESCRIPTION?\n>").lower()
        time = input("TIME DUE? (HH:MM AM/PM)\n>")
        shell.create_task(desc, time)
        print("CREATED TASK")
    elif action == "view":
        handle = open("tasks.htm", "w")
        handle.write(shell.generate_html_table())
        handle.close()
        print("CHECK TASKS.HTM FOR UPDATED TASKS")
    elif action == "update":
        act_id = int(input("ACTIVITIY ID?\n>"))
        progress = int(input("NEW PROGRESS?\n0 FOR NOT STARTED\n1 FOR IN PROGRESS\n2 FOR COMPLETED\n>"))
        shell.update_status(act_id, progress)
        print("PROGRESS UPDATED")
    elif action == "delete":
        act_id = int(input("ACTIVITY ID?\n>"))
        shell.delete_task(act_id)
        print("TASK DELETED")
    elif action == "quit":
        break
    
taskDB = None
input("TERMINATED CONNECTION WITH DATABASE\nPRESS [ENTER] TO EXIT")