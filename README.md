# Mastermind
Python implementation of [Mastermind](https://en.wikipedia.org/wiki/Mastermind_(board_game)) board game. Both roles may be played by either the user or computer. Furthermore, computer code breaker uses a greedy guessing algorithm.

# Rules
User may assume any of the two roles: code maker or code breaker. Role(s) not selected by the user will be played by computer.
        
Code maker invents a secret code and provides feedback to the code breaker. Code breaker tries to guess the secret code invented by the code maker.
        
By default, code is a combination of 4 colors numbered from 1 to 6. Colors may repeat.
        
Feedback is a sequence of markers for each position. There are three valid markers:
* `b`   right color in the right position
* `w`   right color in a wrong position
* `.`  wrong color

# Usage
```
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
```

# Example
`python3 mastermind.py --maker --auto_feedback` output:
```
Code maker is played by the user.
Code breaker is played by computer.
Enter secret code: 3546
2465 .www
1346 .wbb
4646 wwbb
3546 bbbb
```
