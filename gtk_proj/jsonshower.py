from gi.repository import Gtk
import json

with open("jojo.json") as file:
    jojo_data = json.load(file)

tree_store = Gtk.TreeStore(str)

def add_items(parent_iter, data):
    if isinstance(data, dict):
        for data_key, data_value in data.items():
            item_iter = tree_store.append(parent_iter, [str(data_key)])
            add_items(item_iter, data_value)
    elif isinstance(data, list):
        for item in data:
            item_iter = tree_store.append(parent_iter, [""])
            add_items(item_iter, item)
    else:
        tree_store.append(parent_iter, [str(data)])

root_iter = tree_store.append(None, ["characters"])
print(jojo_data)
add_items(root_iter, jojo_data)


view = Gtk.TreeView(model=tree_store)

renderer = Gtk.CellRendererText()
column = Gtk.TreeViewColumn("JoJo Reference", renderer, text=0)
view.append_column(column)
