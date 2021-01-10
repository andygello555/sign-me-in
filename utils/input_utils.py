import re
import getpass
from time import sleep


EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
Y_OR_N = ['y', 'n']

def ask_for(question: str, answers: list):
    """ 
        Given a question and a list of answers it will return the answer. 
        
        Args:
            question: the question to diplay when asking for input
            answers: the list of possible answers to listen for
        
        Returns:
            If the list of answers has only 2 elements then if the answer is 
            equal to the first element it will return True and False otherwise
    """
    answer = str(input(question + " " + str(answers) + ": ")).lower()
    while answer not in answers:
        print("Don't understand that input")
        answer = str(input(question + " " + str(answers))).lower()
    return answer if len(answers) > 2 else answers[0] == answer

def handle_multiple_range(question1: str, question2: str, yes_no: list, lines: list):
    """
        Handles input for a list of possible answers. Multple answers can be given.

        Args:
            question1: the question asked when asking the user for input
            question2: the question asked when asking the user for confirmation
            yes_no: the list of answers in yes no questions (usually ['y', 'n'])
            lines: the list of possible answers

        Returns:
            A list of all the answers given
    """
    answer_no = 0
    answers = [None for _ in range(len(lines))]

    while True:
        if answer_no < len(lines):
            try:
                answers[answer_no] = input((f'{question1}: '))
                if answers[answer_no] in '*q':
                    if answers[answer_no] == '*' and ask_for('Are you sure you want to add all?', yes_no):
                        answers = [i+1 for i in range(len(lines))]
                        break
                    if ask_for('Are you sure you want to exit?', yes_no):
                        break
                elif int(answers[answer_no]) > len(lines) or int(answers[answer_no]) - 1 < 0:
                    print('List number is out of range. Try again.')
                else:
                    if ask_for(question2, yes_no):
                        answers[answer_no] = int(answers[answer_no])
                        answer_no += 1
                    if not ask_for('Do you want to pick another?', yes_no):
                        break
            except ValueError:
                print('List number is not a integer. Try again.')
        else:
            print('No more to pick from.')
            break
    return list(filter(lambda x: x is not None, answers))

def handle_multiple_inputs(command: str, max: int = None) -> list:
    """
        Enables the user to input multiple string answers.

        Args:
            command: what the user needs to do
            max: the maximum number of responses, None = Unlimited
        
        Returns:
            The list of input strings
    """
    output = []

    while True:
        if max is None or len(output) < max:
            print(f'\nYou have currently input: {output}')
            current = [sub.lstrip() for sub in str(input(f'{command}: ')).split(',')]
            if len(current):
                if ask_for('Is \"{}\" ok?'.format("\" and \"".join(current)), Y_OR_N):
                    for curr in current:
                        if curr not in output:
                            output.append(curr)
                if not ask_for('Do you want to add more?', Y_OR_N):
                    break
            else:
                if ask_for('Nothing has been entered do you want to exit inputting?', Y_OR_N):
                    break
        else:
            print('You have reached the maximum number of entries.')
    return output

def password_input(what_for: str, first_time: bool = True) -> str:
    """A standard password re-entry prompt

    Args:
        what_for (str): a string which describes what the password is for
        first_time (bool): whether or not a user is asked to re-enter password

    Returns:
        str: the entered password
    """
    while True:
        password = str(getpass.getpass(prompt=f'Enter password for {what_for}: '))
        if first_time:
            reenterred_pass = str(getpass.getpass(prompt='Re-enter password: '))
            if password == reenterred_pass:
                break
            print('Passwords don\'t match. Try again.')
        else:
            if ask_for("Do you want to peek your password? (Will appear for 5 seconds)", Y_OR_N):
                print(password, end='\r')
                sleep(5)
                if ask_for('Are these details correct?', Y_OR_N):
                    break
            else:
                break
    return password

def handle_user_pass(command: str):
    """
        Asks for user to input a username and password

        Args:
            command: what the user needs to do/why are they doing it

        Returns:
            Chosen email and password
    """
    while True:
        print(f'\n{command}')
        email = str(input('Enter email: '))
        if bool(EMAIL_REGEX.match(email)):
            password = str(getpass.getpass(prompt='Enter password: '))
            if ask_for("Do you want to peek your password? (Will appear for 5 seconds)", Y_OR_N):
                print(password, end='\r')
                sleep(5)
            if ask_for('Are these details correct?', Y_OR_N):
                break
        else:
            print('Email is not valid check again.')
    return email, password
