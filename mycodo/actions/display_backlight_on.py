# coding=utf-8
import threading

from flask_babel import lazy_gettext
from mycodo.utils.functions import parse_function_information
from mycodo.config_translations import TRANSLATIONS
from mycodo.databases.models import Actions
from mycodo.databases.models import CustomController
from mycodo.actions.base_action import AbstractFunctionAction
from mycodo.utils.database import db_retrieve_table_daemon

ACTION_INFORMATION = {
    'name_unique': 'display_backlight_on',
    'name': f"{TRANSLATIONS['display']['title']}: {lazy_gettext('Backlight')}: {lazy_gettext('On')}",
    'library': None,
    'manufacturer': 'Mycodo',
    'application': ['functions'],

    'url_manufacturer': None,
    'url_datasheet': None,
    'url_product_purchase': None,
    'url_additional': None,

    'message': 'Turn display backlight on',

    'usage': 'Executing <strong>self.run_action("ACTION_ID")</strong> will turn the backlight on for the selected display. '
             'Executing <strong>self.run_action("ACTION_ID", value={"display_id": "959019d1-c1fa-41fe-a554-7be3366a9c5b"})</strong> will turn the backlight on for the controller with the specified ID.',

    'custom_options': [
        {
            'id': 'controller',
            'type': 'select_device',
            'default_value': '',
            'options_select': [
                'Function'
            ],
            'name': lazy_gettext('Display'),
            'phrase': 'Select the display to turn the backlight on'
        }
    ]
}


class ActionModule(AbstractFunctionAction):
    """Function Action: Turn the Display Backlight On."""
    def __init__(self, action_dev, testing=False):
        super().__init__(action_dev, testing=testing, name=__name__)

        self.controller_id = None

        action = db_retrieve_table_daemon(
            Actions, unique_id=self.unique_id)
        self.setup_custom_options(
            ACTION_INFORMATION['custom_options'], action)

        if not testing:
            self.try_initialize()

    def initialize(self):
        self.action_setup = True

    def run_action(self, message, dict_vars):
        try:
            controller_id = dict_vars["value"]["display_id"]
        except:
            controller_id = self.controller_id

        display = db_retrieve_table_daemon(
            CustomController, unique_id=controller_id)

        if not display:
            msg = f" Error: Display with ID '{controller_id}' not found."
            message += msg
            self.logger.error(msg)
            return message

        functions = parse_function_information()
        if display.device in functions and "function_actions" in functions[display.device]:
            if "backlight_on" not in functions[display.device]["function_actions"]:
                msg = " Selected display is not capable of turning the backlight on"
                message += msg
                self.logger.error(msg)
                return message

        message += f" Display {controller_id} ({display.name}) Backlight On."

        start_flashing = threading.Thread(
            target=self.control.module_function,
            args=("Function", controller_id, "backlight_on", {},))
        start_flashing.start()

        self.logger.debug(f"Message: {message}")

        return message

    def is_setup(self):
        return self.action_setup
