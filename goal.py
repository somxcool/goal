## Start

import dearpygui.dearpygui as dpg
import sqlite3

dpg.create_context()

with dpg.window(tag='Goal'):
    def addgoal(sender, app_data):
        newgoal = dpg.get_value('New goal')
        dpg.add_selectable(label=newgoal, parent='Goal')
        print(dpg.get_value('New goal'))

    dpg.add_text('Hi, Artem')
    theinput = dpg.add_input_text(label='', hint='Enter your name...', tag='New goal')
    dpg.add_button(label='Save', callback=addgoal)
    dpg.add_selectable(label='Create a new app')

dpg.create_viewport(title='My goals', width=600, height=600)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window('Goal', True)
dpg.start_dearpygui()
dpg.destroy_context()