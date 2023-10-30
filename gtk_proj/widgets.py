from gi.repository import Gtk

from matplotlib.backends.backend_gtk4agg import \
    FigureCanvasGTK4Agg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
import numpy as np
from .jsonshower import view
from .model import PlotData

class Notebook(Gtk.Notebook):
    pass

class Confirm(Gtk.MessageDialog):
    def __init__(self):
        Gtk.MessageDialog.__init__(self)
        self.set_markup('are u sure about it?')
        self.add_button('YES YES YES', 1)
        self.add_button('NO!!!!!!!!!', 0)

class Window(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        Gtk.ApplicationWindow.__init__(self, *args, **kwargs)
        app = kwargs['application']

        self.notebook = Notebook()

        intro = Gtk.ScrolledWindow()
        tab_label = Gtk.Label()
        tab_label.set_text("График")
        self.notebook.append_page(intro, tab_label)

        tab_label = Gtk.Label()
        tab_label.set_text("Список")

        self.is_anim_active = False

        self.fig = Figure(figsize=(5, 4), dpi=100, constrained_layout=False)
        self.ax = self.fig.add_subplot()
        self.line = None

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        intro.set_child(vbox)

        color = (0.96, 0.96, 0.96)
        self.fig.set_facecolor(color)
        self.ax.set_facecolor(color)

        sw = Gtk.ScrolledWindow(margin_top=10, margin_bottom=10, margin_start=10, margin_end=10)
        vbox.append(sw)

        self.ani = None

        hb = Gtk.HeaderBar()
        hb.set_show_title_buttons(True)
        self.set_titlebar(hb)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sw.set_child(vbox)

        button_add_point = Gtk.Button()
        button_add_point.set_label("Добавить")

        button_add_point.connect('clicked', self.add_point)

        button_show_anim = Gtk.Button()
        button_show_anim.set_label("Шарики")

        button_show_anim.connect('clicked', self.bouncing_animation)

        self.data = PlotData()

        self.edit_x = Gtk.SpinButton(name="X", value=0)
        self.edit_y = Gtk.SpinButton(name="Y", value=0)

        for edit in {self.edit_x, self.edit_y}:
            edit.set_adjustment(Gtk.Adjustment(upper=100, step_increment=1, page_increment=10))


        hb.pack_start(button_add_point)
        hb.pack_start(self.edit_x)
        hb.pack_start(self.edit_y)
        hb.pack_end(button_show_anim)

        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(800, 600)
        self.app = kwargs['application']
        vbox.append(self.canvas)

        view.show()

        curr_page = 0


        with open("cache.toml", "r") as f:
            curr_page = int(*f)

        self.set_child(self.notebook)
        self.show()

        self.app = kwargs['application']

        self.connect('close-request', self.exitool)

        list_tab = Gtk.ScrolledWindow()
        tab_label = Gtk.Label()
        tab_label.set_text("Список")
        self.notebook.append_page(list_tab, tab_label)
        self.notebook.set_current_page(curr_page)

        list_tab.set_child(view)

    def add_point(self, *args, **kwargs):

        self.data.add_point(self.edit_x.get_value(), self.edit_y.get_value())
        if self.line is not None:
            self.line.remove()

        self.line, = self.ax.plot(*self.data)
        self.canvas.draw()

    def bouncing_animation(self, *args, **kwargs):
        if self.is_anim_active:
            self.ani.event_source.stop()
            self.ax.cla()
            self.ax.plot(*self.data)
            self.is_anim_active = False
        else:
            num_points = 10
            x = np.random.rand(num_points) * 10
            y = np.random.rand(num_points) * 10
            x_velocities = np.random.rand(num_points) * 0.2
            y_velocities = np.random.rand(num_points) * 0.2

            scat = self.ax.scatter(x, y, c="b", s=30)

            self.is_anim_active = True
            last_x = 0
            last_y = 0

            def update(frame):
                nonlocal x, y, x_velocities, y_velocities, last_x, last_y

                x += x_velocities
                y += y_velocities

                for i in range(num_points):
                    if x[i] < 0 or x[i] > 10:
                        x_velocities[i] *= -1
                    if y[i] < 0 or y[i] > 10:
                        y_velocities[i] *= -1

                scat.set_offsets(np.array([x, y]).T)

                last_x, last_y = x[-1], y[-1]

                return [scat]

            self.ani = animation.FuncAnimation(fig=self.fig, func=update, frames=200, interval=50)

            self.add_point(last_x, last_y)

            self.canvas.draw()

    def exitool(self, _):
        confirm = Confirm()
        confirm.set_transient_for(self)
        confirm.show()
        confirm.connect('response', self.exit)
        return True

    def exit(self, widget, response):
        with open("cache.toml", "w") as f:
            f.write(str(self.notebook.get_current_page()))

        if response == 1:
            self.app.quit()
        widget.destroy()