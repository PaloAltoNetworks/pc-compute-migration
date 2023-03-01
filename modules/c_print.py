import os
def c_print(*args, **kwargs):
    '''
    Uses ascii codes to enable colored print statements. Works on Mac, Linux and Windows terminals
    '''

    #Magic that makes colors work on windows terminals
    os.system('')
    
    #Define Colors for more readable output
    c_gray = '\033[90m'
    c_red = '\033[91m'
    c_green = '\033[92m'
    c_yellow = '\033[93m'
    c_blue = '\033[94m'
    c_end = '\033[0m'

    color = c_end
    if 'color' in kwargs:
        c = kwargs['color'].lower()
        if c == 'gray' or c == 'grey':
            color = c_gray
        elif c ==  'red':
            color = c_red
        elif c == 'green':
            color = c_green
        elif c == 'yellow':
            color = c_yellow
        elif c == 'blue':
            color = c_blue
        else:
            color = c_end

    _end = '\n'
    if 'end' in kwargs:
        _end = kwargs['end']

    print(f'{color}', end='')
    for val in args:
        print(val, end='')
    print(f'{c_end}', end=_end)