import sys
import sqlite3
import datetime
import time
# print(sys.argv)
length = len(sys.argv)


# Create a connection to the SQLite3 database in the current folder
conn = sqlite3.connect('reminders.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        NEXT_REMINDER TIMESTAMP NOT NULL,
        MADE_ON TIMESTAMP NOT NULL,
        reminder TEXT NOT NULL
    )
    ''')
except sqlite3.OperationalError as e:
    print(f"An error occurred while creating the table: {e}")
    exit(1)
except Exeption as e:
    print(f"An error occurred: {e}")
    exit(1)

def print_reminders(reminders):
    # Print the reminders
    for reminder in reminders:
        assert len(reminder) == 4, "Reminder tuple must have exactly 4 elements."
        assert isinstance(reminder[0], int), "ID must be an integer."
        assert isinstance(reminder[1], str), "Next Reminder must be a string."
        assert isinstance(reminder[2], str), "Made On must be a string."
        assert isinstance(reminder[3], str), "Reminder must be a string."
        print(f"ID: {reminder[0]}, Next Reminder: {reminder[1]}, Made On: {reminder[2]}, \033[93mReminder: {reminder[3]}\033[0m")

def print_help():
    print("Usage: python cli_tool.py [command] [args]")
    print("Commands:")
    print("  help - Show this help message")
    print("  remind - Show all reminders due")
    print("  add <reminder> <time_in_minutes> - Add a new reminder. You can use double quotes to add a reminder with spaces")
    print("  delete <id> - Delete a reminder by ID. USe when a task is completed")
    print("  complete <id> - Alias for delete")
    print("  delay <id> <time_in_minutes> - Delay a reminder by ID")
    print("  showall - Show all reminders")
    print("  remind_by_id <id> - Show a reminder by ID")

try:
    if length == 1:
        print_help()

    elif length >1:
        command = sys.argv[1]
        if command in ["delete", 'complete', 'done', 'completed', 'clear']:
            reminder_id = sys.argv[2]
            cursor.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
            print(f"Reminder with ID {reminder_id} deleted.")
        elif command == "remind_by_id":
            reminder_id = sys.argv[2]
            cursor.execute('SELECT * FROM reminders WHERE id = ?', (reminder_id,))
            reminder = cursor.fetchone()
            if reminder:
                print(f"Reminder with ID {reminder_id}: {reminder[3]}")
            else:
                print(f"No reminder found with ID {reminder_id}.")
        elif command in ["remind", "remindme", "remind_me", 'show_due']:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('SELECT * FROM reminders WHERE NEXT_REMINDER <= ?', (current_time,))  # only show reminders that are due
            reminders = cursor.fetchall()
            if reminders:
                print("Reminders due:")
                print_reminders(reminders)
            else:
                print("No reminders due.")
        elif command in ["add", "add_reminder", "add_remind", "add_remind_me", 'new', 'new_remind']:
            new_reminder = sys.argv[2]
            until_reminder = sys.argv[3]
            until_reminder = int(until_reminder) * 60
            current_time = datetime.datetime.now()
            until_reminder = current_time + datetime.timedelta(seconds=until_reminder)
            until_reminder = until_reminder.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('INSERT INTO reminders (NEXT_REMINDER, MADE_ON, reminder) VALUES (?, ?, ?)', (until_reminder, current_time, new_reminder))
            print(f"New reminder added: {new_reminder}")
        elif command in ["delay", 'pushback', 'postpone', 'wait']:
            reminder_id = sys.argv[2]
            delay_time = sys.argv[3]
            # Convert the time to seconds and add it to the current time
            delay_time = int(delay_time) * 60
            current_time = datetime.datetime.now()
            delay_time = current_time + datetime.timedelta(seconds=delay_time)
            delay_time = delay_time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('UPDATE reminders SET NEXT_REMINDER = ? WHERE id = ?', 
                        (delay_time, reminder_id))
            print(f"Reminder with ID {reminder_id} delayed to {delay_time}.")
        elif command in ["showall", "show_all", "show"]:
            cursor.execute('SELECT * FROM reminders')
            reminders = cursor.fetchall()
            if reminders:
                print("All reminders:")
                print_reminders(reminders)
            else:
                print("No reminders found.")
        elif command == "help":
            print_help()
        else:
            print("Invalid command. Use 'help' to see available commands.")
    conn.commit()

except sqlite3.Error as db_error:
    print(f"Database error: {db_error}. Use 'help' to see available commands.")
    conn.rollback()

except IndexError:
    print("Not enough arguments provided. Use 'help' to see available commands.")
except ValueError:
    print("Invalid value provided. Use 'help' to see available commands.")
except Exception as e:
    print(f"An error occurred: {e}. Use 'help' to see available commands.")


# Commit the changes and close the connection
finally:
    conn.close()