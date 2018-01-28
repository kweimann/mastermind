import random


class CodeMaker(object):
    def make_code(self):
        """
        code maker invents a secret code
        """
        raise NotImplemented()

    def give_feedback(self, guess):
        """
        :param guess: guess made by code breaker
        :return: feedback that evaluates guess against secret code
        """
        raise NotImplemented()


class CodeBreaker(object):
    def make_guess(self):
        """
        :return: guess code
        """
        raise NotImplemented()

    def receive_feedback(self, guess, feedback):
        """
        code breaker may use feedback information to select next guess code
        :param guess: last guess made by code breaker
        :param feedback: feedback information from code maker
        """
        raise NotImplemented()


class HumanCodeMaker(CodeMaker):
    def __init__(self, game_utils, auto_feedback=False):
        self._game_utils = game_utils
        self._auto_feedback = auto_feedback
        self._code = None

    def make_code(self):
        # user enters secret code
        while self._code is None:
            try:
                self._code = self._game_utils.validate_code(input("Enter secret code: "))
            except ValueError as e:
                print("Entered code is invalid: {}".format(e))

    def give_feedback(self, guess):
        # user enters feedback for guess code based on his secret code
        if self._code is not None:
            if self._auto_feedback:
                return _auto_feedback(self._code, guess)
            else:
                while True:
                    try:
                        guess_as_string = "".join([str(color) for color in guess])
                        return self._game_utils.validate_feedback(
                            input("Enter feedback for {}: ".format(guess_as_string)))
                    except ValueError as e:
                        print("Entered feedback is invalid: {}".format(e))
        else:
            raise ValueError("no code to provide feedback for")


class ComputerCodeMaker(CodeMaker):
    def __init__(self, game_utils):
        self._game_utils = game_utils
        self._code = None

    def make_code(self):
        # computer invents a random secret code
        self._code = self._game_utils.random_code()

    def give_feedback(self, guess):
        # computer gives automated feedback based on guess and secret code
        if self._code is not None:
            return _auto_feedback(self._code, guess)
        else:
            raise ValueError("no code to provide feedback for")


class HumanCodeBreaker(CodeBreaker):
    def __init__(self, game_utils):
        self._game_utils = game_utils

    def make_guess(self):
        # user enters next guess
        while True:
            try:
                return self._game_utils.validate_code(input("Enter code: "))
            except ValueError as e:
                print("Entered code is invalid: {}".format(e))

    def receive_feedback(self, guess, feedback):
        # user receives feedback (already made visible by the game master)
        pass


class ComputerCodeBreaker(CodeBreaker):
    def __init__(self, game_utils):
        self._game_utils = game_utils
        # valid_guess matrix (n_positions, n_colors) describes
        # all possible guesses by enumerating (position, color) pairs
        self._valid_guess = [[True for _ in range(game_utils.n_colors)] for _ in range(game_utils.n_positions)]
        # set of all yet unseen colors
        self._unseen_colors = set([color for color in range(game_utils.n_colors)])
        # set of all right colors
        self._right_colors = set()
        # flag whether all right colors have been found
        self._right_colors_found = False

    def make_guess(self):
        current_guess = [None] * self._game_utils.n_positions
        # remove colors that are wrong
        colors_to_check = [color in self._right_colors or color in self._unseen_colors for color in
                           range(self._game_utils.n_colors)]
        # make a greedy guess based on the information provided by code maker so far
        return self._make_guess(current_guess, colors_to_check)

    def _make_guess(self, current_guess, colors_to_check, current_position=0):
        # performs depth first search for a valid guess using information in the guess matrix
        # for selecting a color in any given position
        if current_position == self._game_utils.n_positions:
            # guess has been made so return it
            return current_guess
        else:
            # prepare all viable colors at this position given information so far
            valid_colors = [color for color in range(self._game_utils.n_colors)
                            if colors_to_check[color] and self._valid_guess[current_position][color]]
            # shuffle colors to add some randomness to the selection
            # then prioritize colors according to following rules (highest priority is smallest):
            #   0   color has not been tried so far
            #   1   color is right
            #   2   color has not been tried but will be in current guess
            random.shuffle(valid_colors)
            valid_colors.sort(
                key=lambda color: 2 * int(color + 1 in current_guess) if color in self._unseen_colors else 1)
            # try each valid color in current position until a valid guess has been found
            if self._game_utils.duplicates_allowed:
                for color in valid_colors:
                    current_guess[current_position] = color + 1
                    if self._make_guess(current_guess, colors_to_check, current_position + 1) is not None:
                        return current_guess
            else:
                for color in valid_colors:
                    colors_to_check[color] = False
                    current_guess[current_position] = color + 1
                    if self._make_guess(current_guess, colors_to_check, current_position + 1) is not None:
                        return current_guess
                    else:
                        colors_to_check[color] = True
            # no color was valid in this position so go back to previous position and continue search from there
            return None

    def receive_feedback(self, guess, feedback):
        # updates guess matrix according to the information from code maker
        for pos, (peg, color) in enumerate(zip(feedback, guess)):
            if color - 1 in self._unseen_colors:
                self._unseen_colors.remove(color - 1)
            # guessed color is in the right position
            if peg == 'b':
                if not self._game_utils.duplicates_allowed:
                    # guessed color may not be repeated in another position
                    # invalidate corresponding matrix entries
                    for _pos in range(self._game_utils.n_positions):
                        self._valid_guess[_pos][color - 1] = False
                # no other color may be used for this position
                # invalidate corresponding matrix entries
                for _col in range(self._game_utils.n_colors):
                    self._valid_guess[pos][_col] = False
                # update matrix entry to reflect correctly guessed color in this position
                self._valid_guess[pos][color - 1] = True
                self._right_colors.add(color - 1)
            # guessed color is right but in a wrong position
            elif peg == 'w':
                # this color must appear in some other position
                self._valid_guess[pos][color - 1] = False
                self._right_colors.add(color - 1)
            # wrong color
            else:
                # guessed color does not appear in the code
                # invalidate all entries corresponding to this color
                for _pos in range(0, self._game_utils.n_positions):
                    self._valid_guess[_pos][color - 1] = False
        # if all guessed colors are right there is no need to check yet unseen colors
        if not self._right_colors_found:
            if self._check_right_colors_found():
                self._unseen_colors = set()
                self._right_colors_found = True

    def _check_right_colors_found(self):
        if not self._game_utils.duplicates_allowed:
            # if duplicates are not allowed check if right color for each position was found
            return len(self._right_colors) == self._game_utils.n_positions
        else:
            # else make sure there are no unseen colors
            return not self._unseen_colors


class MastermindGameUtils(object):
    def __init__(self, n_colors=6, n_positions=4, duplicates_allowed=True):
        if not duplicates_allowed and n_positions > n_colors:
            raise ValueError("not enough colors for this number of positions")
        self.n_colors = n_colors
        self.n_positions = n_positions
        self.duplicates_allowed = duplicates_allowed

    def validate_code(self, code):
        try:
            code = [int(color) for color in code]
        except (TypeError, ValueError):
            raise ValueError("code must be an iterable of numbers")
        if len(code) != self.n_positions:
            raise ValueError("code must consist of exactly {} colors".format(self.n_positions))
        if not self.duplicates_allowed and len(set(code)) != self.n_positions:
            raise ValueError("duplicates are not allowed")
        for color in code:
            if not 1 <= color <= self.n_colors:
                raise ValueError("color must be a number between 1 and {} (inclusive)".format(self.n_colors))
        return code

    def validate_feedback(self, feedback):
        if len(feedback) != self.n_positions:
            raise ValueError("feedback must consist of exactly {} pegs".format(self.n_positions))
        for peg in feedback:
            if peg not in "bw.":
                raise ValueError("peg must be one of following: 'b', 'w', '.'")
        return feedback

    def random_code(self, duplicates_allowed=None):
        if duplicates_allowed is None:
            duplicates_allowed = self.duplicates_allowed
        elif duplicates_allowed is True and self.duplicates_allowed is False:
            raise ValueError("duplicates are not allowed")
        if duplicates_allowed:
            return [random.randint(1, self.n_colors) for _ in range(self.n_positions)]
        else:
            return random.sample(range(1, self.n_colors + 1), self.n_positions)


def _is_guess_correct(feedback):
    if feedback is not None:
        for peg in feedback:
            if peg != 'b':
                return False
        return True
    return False


def _auto_feedback(code, guess):
    feedback = ""
    for guessed_color, actual_color in zip(guess, code):
        if guessed_color == actual_color:
            feedback += 'b'
        elif guessed_color in code:
            feedback += 'w'
        else:
            feedback += '.'
    return feedback


def play_mastermind(code_maker, code_breaker):
    code_maker.make_code()
    while True:
        guess = code_breaker.make_guess()
        if guess is not None:
            feedback = code_maker.give_feedback(guess)
            guess_as_string = "".join([str(color) for color in guess])
            print(guess_as_string, feedback)
            if _is_guess_correct(feedback):
                break
            else:
                code_breaker.receive_feedback(guess, feedback)
        else:
            print("Guess could not be made. Make sure your input is valid.")
            break


if __name__ == "__main__":
    """
    usage: mastermind.py [-h] [-colors COLORS] [-positions POSITIONS] [--maker]
                         [--breaker] [--no_duplicates] [--auto_feedback] [--rules]
    
    play mastermind board game
    
    optional arguments:
      -h, --help            show this help message and exit
      -colors COLORS        number of colors
      -positions POSITIONS  number of positions in code
      --maker               play as code maker
      --breaker             play as code breaker
      --no_duplicates       disallow duplicate colors
      --auto_feedback       automatically give feedback when user is playing as
                            code maker
      --rules               show rules and exit
    """
    import argparse

    _parser = argparse.ArgumentParser(description="play mastermind board game")
    _parser.add_argument("-colors", type=int, default=6, help="number of colors")
    _parser.add_argument("-positions", type=int, default=4, help="number of positions in code")
    _parser.add_argument("--maker", action="store_true", default=False, help="play as code maker")
    _parser.add_argument("--breaker", action="store_true", default=False, help="play as code breaker")
    _parser.add_argument("--no_duplicates", action="store_true", default=False, help="disallow duplicate colors")
    _parser.add_argument("--auto_feedback", action="store_true", default=False,
                         help="automatically give feedback when user is playing as code maker")
    _parser.add_argument("--rules", action="store_true", default=False, help="show rules and exit")
    _args = _parser.parse_args()

    if _args.rules:
        print("""Rules:
        User may assume any of the two roles: code maker or code breaker.
        Role(s) not selected by the user will be played by computer.
        
        Code maker invents a secret code and provides feedback to the code breaker.
        Code breaker tries to guess the secret code invented by the code maker.
        
        Code is a combination of {} colors numbered from 1 to {}. 
        Colors may{}repeat.
        
        Feedback is a sequence of markers for each position.
        There are three valid markers:
            b   right color in the right position
            w   right color in a wrong position
            .   wrong color""".format(_args.positions, _args.colors, " not " if _args.no_duplicates else " "))
        exit()

    _game_utils = MastermindGameUtils(_args.colors, _args.positions, not _args.no_duplicates)

    if _args.maker:
        print("Code maker is played by the user.")
        _code_maker = HumanCodeMaker(_game_utils, _args.auto_feedback)
    else:
        print("Code maker is played by computer.")
        _code_maker = ComputerCodeMaker(_game_utils)

    if _args.breaker:
        print("Code breaker is played by the user.")
        _code_breaker = HumanCodeBreaker(_game_utils)
    else:
        print("Code breaker is played by computer.")
        _code_breaker = ComputerCodeBreaker(_game_utils)

    play_mastermind(_code_maker, _code_breaker)
