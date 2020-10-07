import re
import getpass


EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

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
                if ask_for('Is \"{}\" ok?'.format("\" and \"".join(current)), ['y', 'n']):
                    for curr in current:
                        if curr not in output:
                            output.append(curr)
                if not ask_for('Do you want to add more?', ['y', 'n']):
                    break
            else:
                if ask_for('Nothing has been entered do you want to exit inputting?', ['y', 'n']):
                    break
        else:
            print('You have reached the maximum number of entries.')
    return output

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
            if ask_for('Are these details correct?', ['y', 'n']):
                break
        else:
            print('Email is not valid check again.')
    return email, password
