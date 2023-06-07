import gi
import pathlib
from rdkit import Chem
from rdkit.Chem import Draw
gi.require_version(namespace='Gtk', version='4.0')
gi.require_version(namespace='Adw', version='1')
from gi.repository import Adw, Gtk, Gio, Pango, GObject
Adw.init()


class Widget(GObject.Object):
    __gtype_name__ = 'Widget'
    def __init__(self, name):
        super().__init__()
        self._name = name
    @GObject.Property
    def name(self):
        return self._name


class ExampleWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title(title='Moleculas')
        self.set_default_size(width=int(1366 / 2), height=int(768 / 2))
        self.set_size_request(width=int(1366 / 2), height=int(768 / 2))
        self.buscador = ""
        self.path = None
        self.archivos_mol = []

        header_bar = Gtk.HeaderBar.new()
        self.set_titlebar(titlebar=header_bar)
        menu_button_model = Gio.Menu()
        menu_button_model.append("About", "app.about")
        menu_button = Gtk.MenuButton.new()
        menu_button.set_icon_name(icon_name='open-menu-symbolic')
        menu_button.set_menu_model(menu_model=menu_button_model)
        header_bar.pack_end(child=menu_button)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.main_box)
        self.second_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.main_box.append(self.second_box)

        abrir_button = Gtk.Button(label="Abrir")
        abrir_button.connect('clicked', self.open)
        self.second_box.append(abrir_button)
        self._native2 = self.dialog_open()                                      
        self._native2.connect("response", self.on_file_open_response)

        self.model_widget = Gio.ListStore(item_type=Widget)
        self.filtro_lista = Gtk.FilterListModel(model=self.model_widget)
        self.filtro_lista_custum = Gtk.CustomFilter.new(self.filtrar, self.filtro_lista)
        self.filtro_lista.set_filter(self.filtro_lista_custum)
        self.factory = Gtk.SignalListItemFactory()
        self.factory.connect("setup", self._on_factory_widget_setup)
        self.factory.connect("bind", self._on_factory_widget_bind)
        self.dropdown_2 = Gtk.DropDown(model=self.filtro_lista, factory=self.factory)
        self.dropdown_2.set_enable_search(True)
        self.dropdown_2.connect("notify::selected-item", self.on_notify_seleccion)
        self.second_box.append(self.dropdown_2)
        search_entry = self._get_search_entry_widget(self.dropdown_2)
        search_entry.connect('search-changed', self._on_search_widget_changed)
        
        self.imagen = Gtk.Image.new()
        self.imagen.set_pixel_size(300)
        self.main_box.append(self.imagen)


    def on_notify_seleccion(self, dropdown, data):
        item = self.archivos_mol[dropdown.get_selected()]
        item = f"{item}"
        path = f"{self.path}/{item}"
        path2 = f"{self.path}/{item}.png"
        m = Chem.MolFromMolFile(path)
        img = Draw.MolToImage(m)
        img.save(path2)
        self.imagen.set_from_file(path2)


    def _on_factory_widget_setup(self, factory, list_item):
        box = Gtk.Box()
        label = Gtk.Label()
        box.append(label)
        list_item.set_child(box)


    def _on_factory_widget_bind(self, factory, list_item):
        box = list_item.get_child()
        label = box.get_first_child()
        widget = list_item.get_item()
        label.set_text(widget.name)


    def filtrar(self, item, listmodel):
        return self.buscador.upper() in item.name.upper()


    def _get_search_entry_widget(self, dropdown):
        popover = dropdown.get_last_child()
        box = popover.get_child()
        box2 = box.get_first_child()
        search_entry = box2.get_first_child()
        return search_entry


    def _on_search_widget_changed(self, search_entry):
        self.buscador = search_entry.get_text()
        self.filtro_lista_custum.changed(Gtk.FilterChange.DIFFERENT)


    def open(self, button):
        self._native2.show()


    def dialog_open(self): 
        return Gtk.FileChooserNative(title="Open File",
                                    action=Gtk.FileChooserAction.SELECT_FOLDER,
                                    accept_label="_Open",
                                    cancel_label="_Cancel",
                                    )


    def on_file_open_response(self, native, response):
        if response == Gtk.ResponseType.ACCEPT:
            self.path = native.get_file().get_path()
            directorio = self.path 
            directorio = pathlib.Path(str(directorio))
            self.archivos_mol = [fichero.name for fichero in directorio.iterdir() 
                            if directorio.glob("*.mol")]
            for archivo in self.archivos_mol:
                i = archivo.split(".")
                self.model_widget.append(Widget(name=i[0]))


class ExampleApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id='cl.com.Example',
                        flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.create_action('quit', self.exit_app, ['<primary>q'])
        self.create_action("about", self.on_about_action)


    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = ExampleWindow(application=self)
        win.present()


    def do_startup(self):
        Gtk.Application.do_startup(self)


    def do_shutdown(self):
        Gtk.Application.do_shutdown(self)


    def on_about_action(self, action, param):
        about = Gtk.AboutDialog.new()
        about.set_authors(["Alejandro Ide"])
        about.set_comments("Esta en progreso")
        about.set_program_name("Moleculas")
        about.set_copyright("Ing. Civil en Bioinformática")
        about.set_visible(True)


    def exit_app(self, action, param):
        self.quit()


    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f'app.{name}', shortcuts)


if __name__ == '__main__':
    import sys
    app = ExampleApplication()
    app.run(sys.argv)
