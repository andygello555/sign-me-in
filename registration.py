from typing import Iterable
from utils.config import CONFIG
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, TimeoutException
from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

REGISTER_ATTENDANCE_URL = CONFIG.REGISTER_ATTENDANCE_URL
GET_ATTR_SCRIPT = 'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;'
GET_TEXT_SCRIPT = """
var parent = arguments[0];
var child = parent.firstChild;
var ret = "";
while(child) {
    if (child.nodeType === Node.TEXT_NODE)
        ret += child.textContent;
    child = child.nextSibling;
}
return ret;
"""
HIDDEN_CLASS = 'ng-hide'
TIMEOUT = 10

class CannotLoginException(Exception):
    pass

def start_selenium(headless: bool):
    """
        Starts an instance of selenium

        Args:
            headless: whether or not to run it in headless
        
        Returns:
            The selenium browser driver
    """
    opts = Options()
    opts.headless = headless

    browser = Firefox(options=opts)
    browser.get(REGISTER_ATTENDANCE_URL)
    return browser

def print_attr_elements(browser, elements: Iterable[FirefoxWebElement]):
    """
        Prints all the html attributes in a given list of FireFoxWebElements

        Args:
            browser: the selenium browser driver
            elements: the elements to print the attributes of
    """
    for element in elements:
        print(f'{element.tag_name}: {browser.execute_script(GET_ATTR_SCRIPT, element)}')

def click_button(email: str, password: str, headless: bool = True, verbose: bool = False, course_id: str = None, search_params: list = None) -> bool:
    """
        Uses selenium to browse to attendance page and check whether there are any attendance buttons to click

        Args:
            email: the email to login to campus connect with
            password: the password to login to campus connect with
            headless: whether or not to run selenium in headless mode
            verbose: whether or not to display info (usually regarding scraped elements)
            course_id: the course ID to check sign in for. If None will match all course titles

        Raises:
            CannotLoginException: if the campus connect login was incorrect or could not be found
        
        Returns:
            True if the button was clicked otherwise False (button could not be clicked, no buttons were found, etc...)
    """

    browser = start_selenium(headless)

    WebDriverWait(browser, TIMEOUT).until(EC.presence_of_element_located((By.ID, 'formsAuthenticationArea')))

    try:
        email_form = browser.find_element_by_id('userNameInput')
        password_form = browser.find_element_by_id('passwordInput')
        submit_button = browser.find_element_by_id('submitButton')

        if verbose:
            print('Found login form:')
            print_attr_elements(browser, [email_form, password_form, submit_button])

        email_form.send_keys(email)
        password_form.send_keys(password)
        submit_button.click()

        # Wait until an element with the classes pb-block and mainBlock is found (this is because when the page is loaded both divs have classes 'pb-block ng-hide mainBlock')
        WebDriverWait(browser, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//div[@class='pb-block mainBlock']")))
    except (NoSuchElementException, TimeoutException):
        browser.close()
        raise CannotLoginException('Cannot login to Campus Connect. This could be due to factors other than an incorrect login')


    happening_now_div = browser.find_element_by_id('pbid-blockFoundHappeningNow')
    happened_before_div = browser.find_element_by_id('pbid-blockHappened30MinAgo')
    nothing_now_div = browser.find_element_by_id('pbid-blockNothingHappeningNow')

    if verbose:
        print('\nFound sign-in blocks:')
        print_attr_elements(browser, [happening_now_div, happened_before_div, nothing_now_div])


    button_id = None
    one_button = None
    two_buttons = None

    try:
        # Check if happening now div is hidden
        if HIDDEN_CLASS not in happening_now_div.get_attribute('class'):
            # Find the buttons (can either be one or two)
            one_button = happening_now_div.find_element_by_id('pbid-blockFoundHappeningNowButtonsOne')
            two_buttons = happening_now_div.find_element_by_id('pbid-blockFoundHappeningNowButtonsTwo')

            # Get the course ID
            course_name = happening_now_div.find_element_by_id('pbid-literalHappeningNowTitle')
            course_name = browser.execute_script(GET_TEXT_SCRIPT, course_name).split(' ')[0]

            if course_id is None or course_id.lower() in course_name.lower() or \
               (search_params is not None and any([param.lower() in course_id for param in search_params])):
                if verbose:
                    print('\nHappening now is not hidden:')
                    print_attr_elements(browser, [one_button, two_buttons])

                # Assign button id to the button nested inside the non-hidden element
                button_id = 'pbid-buttonFoundHappeningNowButtonsHere' if HIDDEN_CLASS not in one_button.get_attribute('class') else 'pbid-buttonFoundHappeningNowButtonsTwoOnline'
            elif verbose:
                print('Found block but of the wrong course ID')
        else:
            # Try the Forgetting Something section
            if verbose: print('\nHappening now is hidden, checking happened 30 min ago...')
            raise ElementClickInterceptedException()
    except ElementClickInterceptedException:
        # The button may have been moved to the 'Forgetting Something' section
        if HIDDEN_CLASS not in happened_before_div.get_attribute('class'):
            WebDriverWait(browser, TIMEOUT).until(EC.presence_of_element_located((By.ID, "pbid-blockHappened30MinAgoButtonsOne")))

            one_button = happened_before_div.find_element_by_id('pbid-blockHappened30MinAgoButtonsOne')
            two_buttons = happened_before_div.find_element_by_id('pbid-blockHappened30MinAgoButtonsTwo')

            if verbose:
                print('\nHappened 30 min ago is not hidden:')
                print_attr_elements(browser, [one_button, two_buttons])

            button_id = 'pbid-buttonHappened30MinAgoButtonsOneHere' if HIDDEN_CLASS not in one_button.get_attribute('class') else 'pbid-buttonHappened30MinAgoButtonsTwoOnline'
    except TimeoutException:
        # One of the elements could not be found so continue and return False
        pass


    button = None
    if one_button is not None and button_id is not None:
        try:
            # If there is only one button present press that button
            if HIDDEN_CLASS not in one_button.get_attribute('class'):
                button = WebDriverWait(browser, TIMEOUT).until(EC.element_to_be_clickable((By.ID, button_id)))
            else:
                # Assume that there are two buttons. And press the 'Online' button
                button = WebDriverWait(browser, TIMEOUT).until(EC.element_to_be_clickable((By.ID, button_id)))

            # Finally click the button if found
            button.click()
        except TimeoutException:
            # One of the elements could not be found so continue and return False
            pass
    elif verbose:
        print('Button not found')

    browser.close()
    
    return button is not None

if __name__ == '__main__':
    print('Pressed button' if click_button(input('Enter email: '), input('Enter password: '), verbose=True) else 'Button not pressed')
