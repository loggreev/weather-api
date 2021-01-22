# asks the user to enter a choice from the given options
# returns the users choice
def get_choice(options):
    if len(options) < 1:
        raise Exception('get_choice must contain at least 1 option!')
    # loop until a valid option is selected
    while True:
        # for every given option
        for index, option in enumerate(options):
            print(f'{index+1}: {option}')
        try:
            # user enters a number corresponding to the displayed option
            choice = int(input()) - 1
            if choice not in range(len(options)):
                raise ValueError
        except ValueError:
            print('Invalid choice.\n')
            continue
        choice = options[choice]
        return choice