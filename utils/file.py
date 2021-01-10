from utils.input_utils import password_input
from utils.time_utils import get_utc_now
from utils.config import CONFIG
from os import listdir
from os.path import basename, isfile, join, dirname, realpath, splitext
import time
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import json

SAVED_CALENDAR_PATH = CONFIG.SAVED_CALENDAR_PATH

class IncorrectPassword(Exception):
    def __init__(self, **kwargs):
        super(IncorrectPassword, self).__init__('Decrypted text could not be converted json, therefore it\'s assumed that the password is incorrect', **kwargs)

def get_calendars(path: str = SAVED_CALENDAR_PATH) -> list:
    """Gets all the filenames of the calendar infos inside the given path

    Args:
        path (str, optional): The path to check for calendaro info. Defaults to SAVED_CALENDAR_PATH.

    Returns:
        list: a list of all the relevent filenames in which calendar infos are kept
    """
    if not path:
        path = dirname(dirname(realpath(__file__)))
    return [f for f in listdir(path) if isfile(join(path, f)) and splitext(f)[1] == '.pickle' and f != 'token.pickle']

def get_latest_calendar_file(path: str = SAVED_CALENDAR_PATH) -> str:
    """Gets the latest calendar file in the given path

    Args:
        path (str, optional): The path to check for calendar info. Defaults to SAVED_CALENDAR_PATH.

    Returns:
        str: the path of the most recent calendar info file
    """
    try:
        most_recent = max([int(splitext(file)[0]) for file in get_calendars(path)])
    except ValueError:
        return None
    return join(dirname(dirname(realpath(__file__))), f'{most_recent}.pickle')

def calendars_exists(path: str = SAVED_CALENDAR_PATH) -> bool:
    """Checks whether any calendars exist in the given path

    Args:
        path (str, optional): The path in which to save the calendar info files. Defaults to SAVED_CALENDAR_PATH.

    Returns:
        bool: whether or not any calendar infos exist or not
    """
    return bool(len(get_calendars(path)))

def save_encrypted(calendars: list):
    """Saves a calendar info list to an encrypted file of the user's choice of password

    Will save the calendar info files to SAVE_CALENDAR_PATH

    Args:
        calendars (list): the list of calendar infos to save
    """
    output_file = f'{int(time.time())}.pickle'
    IV = Random.new().read(16)
    password = password_input('encryption of calendar login details')

    hash_pass = SHA256.new()
    hash_pass.update(bytes(password, 'utf-8'))

    encryptor = AES.new(hash_pass.digest(), AES.MODE_CBC, IV)
    calendar_info = json.dumps(calendars, indent=4, sort_keys=True).encode('utf-8')

    # Pad the data with the number of bytes to pad by
    length = 16 - (len(calendar_info) % 16)
    calendar_info += bytes([length]) * length

    if not SAVED_CALENDAR_PATH:
        save_path = join(dirname(dirname(realpath(__file__))), output_file)
    else:
        save_path = join(SAVED_CALENDAR_PATH, output_file)

    with open(save_path, 'wb+') as out_file:
        ciphertext = encryptor.encrypt(calendar_info)
        out_file.write(IV)
        out_file.write(ciphertext)

def load_latest_calendar(path: str = SAVED_CALENDAR_PATH) -> list:
    """Loads the latest calendar info file, by asking for the decryption password

    Args:
        path (str, optional): The path of the saved calendars. Defaults to SAVED_CALENDAR_PATH.

    Raises:
        IncorrectPassword: If the decrypted file cannot be decoded to JSON, it is assumed that the password is incorrect

    Returns:
        list: the list of calendar infos
    """
    recent_calendar = get_latest_calendar_file(path)
    calendar_info = []

    if recent_calendar is not None:
        with open(recent_calendar, 'rb') as in_file:
            IV = in_file.read(16)
            hash_pass = SHA256.new()
            hash_pass.update(bytes(password_input(f'decrypting previous calendar info file ({basename(recent_calendar)})', False), 'utf-8'))
            decryptor = AES.new(hash_pass.digest(), AES.MODE_CBC, IV)
            data = decryptor.decrypt(in_file.read())
        data = data[:-data[-1]].decode('utf-8')
        try:
            calendar_info = json.loads(data)
        except:
            raise IncorrectPassword()
    return calendar_info

if __name__ == '__main__':
    print(get_calendars())
    print(get_latest_calendar_file())
    # save_encrypted(example_cal)
    print(load_latest_calendar())
