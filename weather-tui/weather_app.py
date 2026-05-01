from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static
from textual.reactive import reactive
from textual import work
from textual.message import Message
from weather_service import WeatherService

class WeatherWidget(Static):
    """A custom widget to display weather information."""
    
    weather_data = reactive("")

    def on_mount(self):
        """Start a timer to refresh weather data every 30 seconds."""
        self.set_interval(30, self.refresh_weather)

    @work
    async def refresh_weather(self):
        """Perform the weather API call in a worker thread."""
        weather_text = await self.run_worker(self.fetch_weather_data, thread=True)
        self.weather_data = weather_text

    def fetch_weather_data(self):
        city_name = self.id if self.id else "Unknown"
        return weather_service.get_full_weather(city_name)

    def render(self):
        return self.weather_data

class CityListView(ListView):
    """A list view that emits a custom message when an item is selected."""
    
    class CitySelected(Message):
        def __init__(self, city: str) -> None:
            self.city = city
            super().__init__()

    def on_list_view_selected(self, event: ListView.Selected):
        """Send a CitySelected message when a city is chosen."""
        # The city name is stored in the ListItem's id attribute
        city_name = event.item.id
        self.post_message(self.CitySelected(city_name))

class WeatherApp(App):
    """The main Textual application class."""
    
    CSS_PATH = "css/weather.tcss"
    BINDINGS = [("q", "quit", "Quit")]
    
    def __init__(self):
        super().__init__()
        self.weather_service = WeatherService()
        self.default_cities = ['tehran', 'london', 'new-york', 'tokyo', 'sydney', 
                               'cape-town', 'mumbai', 'beijing', 'rio-de-janeiro', 'cairo']
        self.current_city = "tehran"

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()
        with Container():
            with Horizontal():
                with Vertical(classes="sidebar"):
                    yield Label("Cities", classes="sidebar-title")
                    # Create ListItems with id set to the city name (lowercase)
                    city_items = [ListItem(Label(city.capitalize()), id=city) for city in self.default_cities]
                    yield CityListView(*city_items, id="city-list")
                with Vertical(classes="main-content"):
                    yield WeatherWidget(id=self.current_city)
        yield Footer()

    def on_city_list_view_city_selected(self, message: CityListView.CitySelected):
        """Handle city selection by updating the weather widget."""
        self.current_city = message.city
        # Remove the old widget
        old_widget = self.query_one(f"#{self.current_city}")
        old_widget.remove()
        # Mount a new widget for the selected city
        new_widget = WeatherWidget(id=self.current_city)
        self.query_one(".main-content").mount(new_widget)

if __name__ == "__main__":
    # Create the global weather_service instance used by WeatherWidget
    global weather_service
    weather_service = WeatherService()
    app = WeatherApp()
    app.run()
