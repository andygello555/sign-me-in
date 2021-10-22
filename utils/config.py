import os
import json

# All parameters that can be used within the config file
PARAMETERS = {
    'REGISTER_ATTENDANCE_URL',
    'SAVED_CALENDAR_PATH',
    'MIN_CLICK_TIMEOUT',
    'MAX_CLICK_TIMEOUT',
    'STILL_ALIVE',
    'BACKOFF_MULT',
    'LOOP_TIMEOUT',
    'SCHEDULE_START_PERCENT',
    'SCHEDULE_END_PERCENT',
    'HEADLESS',
    'BUTTON_ONE_ID',
    'BUTTON_TWO_ID',
    'BUTTON_30_ONE_ID',
    'BUTTON_30_TWO_ID'
}

class ConfigException(Exception):
    msg = ''

class UnrecognisedConfigParameter(ConfigException):
    def __init__(self, parameter: str, **kwargs):
        self.msg = f'Unrecognised parameter: {parameter}'
        super(UnrecognisedConfigParameter, self).__init__(self.msg, **kwargs)

class ConfigFileException(ConfigException):
    def __init__(self, config_path: str, exception: ConfigException, **kwargs):
        super(ConfigFileException, self).__init__(f'Error in config file: {config_path}, {exception.msg}')

class Config:
    """Stores config parameters used throughout the program
    """

    def __init__(self, **kwargs) -> None:
        for param in kwargs:
            if param in PARAMETERS:
                setattr(self, param, kwargs[param])
            else:
                raise UnrecognisedConfigParameter(param)
    
    def __sub__(self, other):
        """Returns a new Config which has all the parameters possible with the default values being 
        overriden if they exist in 'other'

        Args:
            other: the other config to 'compare'

        Returns:
            A new instance which has all the parameters possible with the default values being 
            overriden by the other given config
        """
        params: dict = self.__dict__
        other_params: dict = other.__dict__
        new_params = params.copy()

        for param in params:
            if param in other_params:
                new_params[param] = other_params[param]
        return Config(**new_params)

DEFAULT_CONFIG = Config(
    REGISTER_ATTENDANCE_URL='https://generalssb-prod.ec.royalholloway.ac.uk/BannerExtensibility/customPage/page/RHUL_Attendance_Student',
    SAVED_CALENDAR_PATH='',
    MIN_CLICK_TIMEOUT=5,  # seconds
    MAX_CLICK_TIMEOUT=360,  # seconds
    STILL_ALIVE=10,  # mins
    BACKOFF_MULT=1.5,  # * seconds
    LOOP_TIMEOUT=5,  # seconds
    # The percentage of the way through that events will be scheduled to be signed into
    SCHEDULE_START_PERCENT=0.1,
    SCHEDULE_END_PERCENT=0.75,
    HEADLESS=True,  # Whether or not to run selenium headless
    BUTTON_ONE_ID='pbid-buttonFoundHappeningNowButtonsHere',  # The ID of the button to click if only one button is found
    BUTTON_TWO_ID='pbid-buttonFoundHappeningNowButtonsTwoInPerson',  # The ID of the button to click if two buttons are found
    BUTTON_30_ONE_ID='pbid-buttonHappened30MinAgoButtonsOneHere',  # The ID of the button to click if only one button is found in 30 mins ago section
    BUTTON_30_TWO_ID='pbid-buttonHappened30MinAgoButtonsTwoInPerson'  # The ID of the button to click if two buttons are found in 30 mins ago section
)

def read_config() -> Config:
    """Reads the config file into a Config instance, inside the program directory

    Raises:
        ConfigFileException: whether or not a ConfigException occurs within the config file

    Returns:
        Config: an empty Config if no config file is found or a Config with some parameters in it
    """
    config = Config()
    current_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    config_path = os.path.join(current_dir, 'config.json')

    if os.path.exists(config_path) and os.path.isfile(config_path):
        with open(config_path) as config_file:
            try:
                config = Config(**json.loads(config_file.read()))
            except ConfigException as e:
                raise ConfigFileException(config_file, e)
    return config

# Find the difference between the default and the config file in the program directory
# What this does is replace all the parameter values that are different in the config file
CONFIG = DEFAULT_CONFIG - read_config()

if __name__ == '__main__':
    print(CONFIG.__dict__)
