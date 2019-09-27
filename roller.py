import random
import re

def roll_output_parser(results):
    print('Rolled values:',results["rolled_values"])
    print('Modifier applied:',results["modifier_applied"])
    print('Total:',results["total"])
    print('')

def roller(inputvar):

    diceRegex = re.compile(r'''
    (  # wrapping capture group for the entire requested dice roll
    (\d+) # number of dice
    d #literal d
    (\d+) # die faces
    (\+|\-)? # optional modifier operators
    (\d+)? # optional modifier value
    ) ''',re.X)

    # join input vars
    sep = ''
    roll_request = sep.join(inputvar)

    # extract & convert type and number of dice to roll
    to_roll = re.split(diceRegex, roll_request)
    numdie = int(to_roll[2])
    dieface = int(to_roll[3])

    # initialize variables
    result = 0
    rolls = []
    diemodifier = None

    # iterate through number of dice to roll, adding results to running tally and a list of all roll results
    while numdie > 0:
        roll_value = random.randint(1,dieface)
        rolls.append(roll_value)
        result += roll_value
        numdie -= 1

    # determine if an operator was used
    if to_roll[4] != None:
        dieoperator = to_roll[4]

        # check if a modifier was used
        if to_roll[5] != None:
            diemod = int(to_roll[5])

            # apply proper operation for the modifier selected
            if dieoperator == "+":
                result = result + diemod
            elif dieoperator == "-":
                result = result - diemod
        else:
            diemodifier = "Unset"
    else:
        diemodifier = "Unset"

    # establish result dictionary
    results = {}
    # return raw roll results...
    results["rolled_values"] = rolls

    # quick validation if a modifier was used or not
    if diemodifier == "Unset":
        results["modifier_applied"] = "None"
    #output appropriate modifier
    else:
        results["modifier_applied"] = dieoperator + str(diemod)

    results["total"] = result

    #mostly just temp
    #roll_output_parser(results)

    #not currently needed but available for if used in game
    return results

if __name__=="__main__":
    import sys
    if len(sys.argv) > 1:
        print(roller(sys.argv[1]))
