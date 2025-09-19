from textual.app import App, ComposeResult
from textual.widgets import Footer, DataTable, Input, RichLog
from textual.containers import Container, VerticalGroup, VerticalScroll, HorizontalGroup, Vertical
from tui_network.features.network_manager import NetworkManager

nm = NetworkManager()

class StatusWidget(VerticalScroll):

    BORDER_TITLE = "Status"

    def compose(self) -> ComposeResult:
        yield DataTable(
            header_height=1,
            show_cursor=False,
            cursor_type='row'
        )

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        try:
            table.add_columns(*nm.get_status_header())
            table.add_rows(nm.get_status())
        except Exception:
            print('Wireless is down...')


class NetworksWidget(VerticalScroll):

    BORDER_TITLE = "Networks"

    def compose(self) -> ComposeResult:
        yield DataTable(
            header_height=1,
            cursor_type='row'
        )

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        try:
            table.add_columns(*nm.get_networks_header())
            table.add_rows(nm.get_networks())
        except:
            print('Wireless is down...')

    def on_data_table_row_selected(self, message: DataTable.RowSelected) -> None:
        self.app.query_one('#network_name').insert_text_at_cursor(message.data_table.get_row_at(message.cursor_row)[0])
        self.app.query_one('#network_passphrase').focus()

class ConnectWidget(HorizontalGroup):

    BORDER_TITLE = "Connect"

    def compose(self) -> ComposeResult:
        yield Input(placeholder='Network name', id='network_name')
        yield Input(placeholder='Network passphrase', password=True, id='network_passphrase')

    def on_input_submitted(self, message: Input.Submitted) -> None:
        if message.input.id == 'network_name':
            self.screen.focus_next()
        if message.input.id == 'network_passphrase':
            network_name = self.parent.query_one('#network_name').value
            network_passphrase = message.value
            nm.connect(network_name, network_passphrase)


class NetworkApp(App):

    BORDER_TITLE = "Network app"
    CSS_PATH = "static/style.tcss"

    BINDINGS = [
        ("q", "quit()", "Quit"),
        ("r", "refresh()", "Rescan"),
        ("d", "toggle('off')", "wifi Down"),
        ("u", "toggle('on')", "wifi Up"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
          #  yield VerticalGroup(NetworksWidget(can_focus=False), id='networks'),
          #  yield VerticalGroup(StatusWidget(can_focus=False, can_focus_children=False), id='status'),
          #  yield VerticalGroup(ConnectWidget(), id='connect'),
            yield StatusWidget(can_focus=False, can_focus_children=False)
            yield NetworksWidget(can_focus=False)
            yield ConnectWidget()
        yield Footer()

    def on_mount(self) -> None:
        self.theme = "tokyo-night"
        self.screen.focus_next()
        #self.app.query_one('NetworksWidget').focus()

    def action_refresh(self) -> None:
        nm.rescan()
        self.refresh(recompose=True)

    def action_toggle(self, direction: str) -> None:
        nm.toggle(direction)
