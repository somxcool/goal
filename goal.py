## Start

import dearpygui.dearpygui as dpg
import sqlite3

conn = sqlite3.connect('goalbase.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        details TEXT,
        status TEXT NOT NULL
    )
"""
)
conn.commit()

cursor.execute('SELECT * FROM goals')
allentries = cursor.fetchall()
print(allentries)

viewid = ''

dpg.create_context()

def addgoal(sender, app_data):
    newgoal = dpg.get_value('New goal')
    newgoaldesc = dpg.get_value('New goal details')
    print(newgoal, newgoaldesc)
    cursor.execute('INSERT INTO goals (title, details, status) VALUES (?, ?, ?)', (newgoal, newgoaldesc, 'current'))
    conn.commit()
    dpg.add_selectable(label=newgoal, parent='currentgoals')
    dpg.configure_item('modal_create', show=False)

def opendetails(sender, app_data):
    global viewid
    dpg.configure_item('modal_id', show=True)
    print('sender', sender)
    pickedentry = allentries[int(sender) - 1]
    viewid = pickedentry[0]
    dpg.configure_item('Goal title', default_value=pickedentry[1])
    dpg.configure_item('Goal details', default_value=pickedentry[2])
    if pickedentry[3] == 'current':
        dpg.configure_item('marker', default_value=False)
    else:
        dpg.configure_item('marker', default_value=True)

def creategoal(sender, app_data):
    dpg.configure_item('modal_create', show=True)

def windowexit(sender, app_data):
    dpg.configure_item('modal_create', show=False)
    dpg.configure_item('modal_id', show=False)

def editgoal(sender, app_data):
    newtitle = dpg.get_value('Goal title')
    newdetails = dpg.get_value('Goal details')
    newstatus = dpg.get_value('marker')
    print('newstatus', newstatus)
    if newstatus:
        newstatus = 'completed'
    else:
        newstatus = 'current'
    print(newtitle, newdetails, newstatus, viewid)
    cursor.execute("""
        UPDATE goals
        SET title = ?, details = ?, status = ?
        WHERE id = ?
    """, (newtitle, newdetails, newstatus, viewid)
    )
    conn.commit()


with dpg.window(label='Create goal', modal=True, show=False, tag='modal_create', no_title_bar=True, width=400, height=200):
    dpg.add_text('Creating a goal...')
    dpg.add_separator()
    theinput = dpg.add_input_text(label='', hint='Enter your goal...', tag='New goal')
    theinputdesc = dpg.add_input_text(label='', multiline=True, hint='Enter details (optional)...', tag='New goal details')
    with dpg.group(horizontal=True):
        dpg.add_button(label='Add goal', callback=addgoal)
        dpg.add_button(label='Cancel', callback=windowexit)


with dpg.window(label='View goal', modal=True, show=False, tag='modal_id', no_title_bar=True, width=400, height=200):
    dpg.add_text('Viewing this goal...')
    dpg.add_separator()
    vtheinput = dpg.add_input_text(label='', default_value='', hint='Enter your goal...', tag='Goal title')
    vtheinputdesc = dpg.add_input_text(label='', default_value='', multiline=True, hint='Enter details (optional)...', tag='Goal details')
    with dpg.group(horizontal=True):
        dpg.add_button(label='Edit goal', callback=editgoal)
        dpg.add_button(label='Cancel', callback=windowexit)
        dpg.add_checkbox(label='Mark complete', default_value=False, tag='marker')
    

with dpg.window(tag='MAIN'):

    with dpg.group(tag='enterdata', horizontal=True):
        dpg.add_button(label='+ goal', callback=creategoal)

    with dpg.collapsing_header(label='Current goals', tag='currentgoals', default_open=True):
        #dpg.add_selectable(label='Create a new app', callback=opendetails, tag='goal0')
        for row in allentries:
            if row[3] == 'current':
                print(row[0])
                goaltag = str(row[0])
                dpg.add_selectable(label=row[1], callback=opendetails, tag=goaltag, parent='currentgoals')

    with dpg.collapsing_header(label='Completed goals', tag='completedgoals', default_open=True):
        for row in allentries:
            if row[3] == 'completed':
                print(row[0])
                goaltag = str(row[0])
                dpg.add_selectable(label=row[1], callback=opendetails, tag=goaltag, parent='completedgoals')

dpg.create_viewport(title='goal', width=488, height=488)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window('MAIN', True)
dpg.start_dearpygui()
dpg.destroy_context()

conn.close()