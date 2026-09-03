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

viewid = ''
picked_to_delete = ''
goalstodelete = []

dpg.create_context()

# with dpg.font_registry():
#     with dpg.font('DMSans-Regular.ttf', 18, default_font=True) as default_font:
#         pass

# dpg.bind_font(default_font)

def addgoal(sender, app_data):
    newgoal = dpg.get_value('New goal')
    newgoaldesc = dpg.get_value('New goal details')
    cursor.execute('INSERT INTO goals (title, details, status) VALUES (?, ?, ?)', (newgoal, newgoaldesc, 'current'))
    conn.commit()
    dpg.delete_item('currentgoals', children_only=True)
    dpg.delete_item('completedgoals', children_only=True)
    cursor.execute('SELECT * FROM goals')
    allentries = cursor.fetchall()
    for row in allentries:
        if row[3] == 'current':
            goaltag = str(row[0])
            dpg.add_selectable(label=row[1], callback=opendetails, tag=goaltag, parent='currentgoals')
        else:
            goaltag = str(row[0])
            dpg.add_selectable(label=row[1], callback=opendetails, tag=goaltag, parent='completedgoals')
    dpg.configure_item('modal_create', show=False)

def opendetails(sender, app_data):
    cursor.execute('SELECT * FROM goals')
    allentries = cursor.fetchall()
    global viewid
    dpg.configure_item('modal_id', show=True)
    for row in allentries:
        if row[0] == int(sender):
            viewid = row[0]
            title = row[1]
            details = row[2]
            status = row[3]
    dpg.configure_item('Goal title', default_value=title)
    dpg.configure_item('Goal details', default_value=details)
    if status == 'current':
        dpg.configure_item('marker', default_value=False)
    else:
        dpg.configure_item('marker', default_value=True)

def creategoal(sender, app_data):
    dpg.configure_item('modal_create', show=True)
    dpg.configure_item('New goal', default_value='')
    dpg.configure_item('New goal details', default_value='')

def opendeletegoal(sender, app_data):
    global goalstodelete
    dpg.configure_item('modal_delete', show=True)
    cursor.execute('SELECT * FROM goals')
    allentries = cursor.fetchall()
    goalstodelete = []
    for row in allentries:
        goalstodelete.append(row[1])
    dpg.configure_item('deletelist', items=goalstodelete)

def picktodelete(sender, app_data):
    global picked_to_delete
    picked_to_delete = app_data

def deletegoal(sender, app_data):
    global goalstodelete
    global picked_to_delete
    cursor.execute('DELETE FROM goals WHERE title = ?', (picked_to_delete,))
    conn.commit()
    dpg.delete_item('currentgoals', children_only=True)
    dpg.delete_item('completedgoals', children_only=True)
    cursor.execute('SELECT * FROM goals')
    allentries = cursor.fetchall()
    print(allentries)
    for row in allentries:
        if row[3] == 'current':
            goaltag = str(row[0])
            dpg.add_selectable(label=row[1], callback=opendetails, tag=goaltag, parent='currentgoals')
        else:
            goaltag = str(row[0])
            dpg.add_selectable(label=row[1], callback=opendetails, tag=goaltag, parent='completedgoals')
    dpg.configure_item('modal_delete', show=False)

def windowexit(sender, app_data):
    dpg.configure_item('modal_create', show=False)
    dpg.configure_item('modal_id', show=False)
    dpg.configure_item('modal_delete', show=False)

def editgoal(sender, app_data):
    newtitle = dpg.get_value('Goal title')
    newdetails = dpg.get_value('Goal details')
    newstatus = dpg.get_value('marker')
    if newstatus:
        newstatus = 'completed'
    else:
        newstatus = 'current'
    cursor.execute("""
        UPDATE goals
        SET title = ?, details = ?, status = ?
        WHERE id = ?
    """, (newtitle, newdetails, newstatus, viewid)
    )
    conn.commit()
    dpg.delete_item('currentgoals', children_only=True)
    dpg.delete_item('completedgoals', children_only=True)
    cursor.execute('SELECT * FROM goals')
    allentries = cursor.fetchall()
    for row in allentries:
        if row[3] == 'current':
            goaltag = str(row[0])
            dpg.add_selectable(label=row[1], callback=opendetails, tag=goaltag, parent='currentgoals')
        else:
            goaltag = str(row[0])
            dpg.add_selectable(label=row[1], callback=opendetails, tag=goaltag, parent='completedgoals')
    dpg.configure_item('modal_id', show=False)

# Window responsible for creating a new goal. Appears after clicking on the '+ goal' button.
with dpg.window(label='Create goal', modal=True, show=False, tag='modal_create', no_title_bar=True, width=408, height=288):
    dpg.add_text('Creating a goal...')
    dpg.add_separator()
    theinput = dpg.add_input_text(label='', hint='Enter your goal...', tag='New goal')
    theinputdesc = dpg.add_input_text(label='', multiline=True, hint='Enter details (optional)...', tag='New goal details')
    with dpg.group(horizontal=True):
        dpg.add_button(label='Add goal', callback=addgoal)
        dpg.add_button(label='Cancel', callback=windowexit)

# Window responsible for viewing/editing a goal. Appears after clicking on an existing goal.
with dpg.window(label='View goal', modal=True, show=False, tag='modal_id', no_title_bar=True, width=408, height=288):
    dpg.add_text('Viewing this goal...')
    dpg.add_separator()
    vtheinput = dpg.add_input_text(label='', default_value='', hint='Enter your goal...', tag='Goal title')
    vtheinputdesc = dpg.add_input_text(label='', default_value='', multiline=True, hint='Enter details (optional)...', tag='Goal details')
    with dpg.group(horizontal=True):
        dpg.add_button(label='Edit goal', callback=editgoal)
        dpg.add_button(label='Cancel', callback=windowexit)
        dpg.add_checkbox(label='Mark complete', default_value=False, tag='marker')
    
with dpg.window(label='Delete goal', modal=True, show=False, tag='modal_delete', no_title_bar=True, width=408, height=288):
    dpg.add_text('Deleting a goal...')
    dpg.add_separator()
    dpg.add_listbox(items=['Test1', 'Test2', 'Test3'], tag='deletelist', num_items=8, callback=picktodelete)
    with dpg.group(horizontal=True):
        dpg.add_button(label='Delete goal', callback=deletegoal)
        dpg.add_button(label='Cancel', callback=windowexit)

# Main application window where goal groups and goals within are displayed, as well as the button to create a new goal.
with dpg.window(tag='MAIN'):

    with dpg.group(tag='enterdata', horizontal=True):
        dpg.add_button(label='+ goal', callback=creategoal)
        dpg.add_button(label='- goal', callback=opendeletegoal)

    with dpg.collapsing_header(label='Current goals', tag='currentgoals', default_open=True):
        for row in allentries:
            if row[3] == 'current':
                goaltag = str(row[0])
                dpg.add_selectable(label=row[1], callback=opendetails, tag=goaltag, parent='currentgoals')

    with dpg.collapsing_header(label='Completed goals', tag='completedgoals', default_open=True):
        for row in allentries:
            if row[3] == 'completed':
                goaltag = str(row[0])
                dpg.add_selectable(label=row[1], callback=opendetails, tag=goaltag, parent='completedgoals')

dpg.create_viewport(title='goal', width=488, height=488)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window('MAIN', True)
dpg.start_dearpygui()
dpg.destroy_context()