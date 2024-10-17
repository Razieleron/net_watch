from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import subprocess
import netifaces
import platform
from datetime import datetime
from log_internet_info import log_internet_info
import pytz


class NetworkMonitorApp(App):
    def build(self):
        """This Application will monitor the network connection and log the information to a CSV file.

        Returns:
            _type_: the root widget of the Kivy app
        """
        self.layout = BoxLayout(orientation='vertical')

        self.status_label = Label(text="Click 'Start' to begin monitoring")
        self.start_button = Button(text="Start", on_press=self.start_monitoring)
        self.stop_button = Button(text="Stop", on_press=self.stop_monitoring)

        self.layout.add_widget(self.status_label)
        self.layout.add_widget(self.start_button)
        self.layout.add_widget(self.stop_button)

        self.monitoring_event = None
        return self.layout

    def start_monitoring(self, instance):
        """Commence the monitoring process

        Args:
            instance (_type_): _description_
        """
        self.status_label.text = "Monitoring started"
        # Schedule the loop every 10 seconds
        self.monitoring_event = Clock.schedule_interval(self.full_loop, 10)

    def stop_monitoring(self, instance):
        """This function will stop the monitoring process

        Args:
            instance (_type_): _description_
        """

        self.status_label.text = "Monitoring stopped"
        if self.monitoring_event:
            self.monitoring_event.cancel()

    def get_router_ip(self) -> str | None:
        """
        Description:
            Get the IP address of the default gateway (router) using netifaces library
            
        Returns:
            str | None: IP address of the router or None if not found
        """
        try:
            gateways = netifaces.gateways()
            default_gateway = gateways.get('default', {})
            router_ip = default_gateway.get(netifaces.AF_INET)[0]
            return router_ip
        except Exception as e:
            return None

    def get_network_name_windows(self) -> str | None:
        """Get the SSID of the connected network on Windows using netsh command

        Returns:
            str: SSID of the connected network or None if not connected
        """
        try:
            result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
            for line in result.stdout.split("\n"):
                if "SSID" in line and "BSSID" not in line:
                    ssid = line.split(":")[1].strip()
                    return ssid
            return None
        except Exception as e:
            return None

    def ping(self, host):
        """_summary_

        Args:
            host (_type_): _description_

        Returns:
            _type_: _description_
        """
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        try:
            output = subprocess.run(["ping", param, "1", host], capture_output=True, text=True)
            if output.returncode == 0:
                return True 
            else:
                return False
        except Exception as e:
            return False

    def get_current_datetime(self):
        """_summary_
            this function returns the current date and time in the format "mm/dd/yyyy hh:mmAM/PM PST"
        Returns:
            _type_: _description_
        """
        timezone = pytz.timezone('US/Pacific')
        now = datetime.now(timezone)
        formatted_datetime = now.strftime("%m/%d/%Y %I:%M%p PST")
        return formatted_datetime

    def full_loop(self):
        """_summary_
            this function will check the router connection, network connection, and internet connection and log the information
        
        
        """
        router_ip = self.get_router_ip()
        router_connected = None
        if router_ip and self.ping(router_ip):
            self.status_label.text = f"Router is connected: {router_ip}"
            router_connected = True
        else:
            self.status_label.text = "Router is not reachable."
            router_connected = False

        network_name = self.get_network_name_windows()
        if network_name:
            self.status_label.text += f"\nConnected to network: {network_name}"
        else:
            self.status_label.text += "\nNot connected to any Wi-Fi network."

        network_connected = None
        if self.ping('www.google.com'):
            self.status_label.text += "\nInternet connection is active."
            network_connected = True
        else:
            self.status_label.text += "\nNo internet connection."
            network_connected = False

        date_time = self.get_current_datetime()
        # Here you can call your log function, such as log_internet_info
        log_internet_info(date_time, router_ip, network_name, router_connected, network_connected)


if __name__ == '__main__':
    NetworkMonitorApp().run()

