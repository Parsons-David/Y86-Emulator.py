from sys import argv
import logging

# Directives
def textDirective(directive):
    # Defines Global References
    global iPtr, memory

    # Sets Instruction Pointer
    iPtr = int(directive.split('\t')[1])
    logging.info('\t\t\tInitial Instruction Pointer Set to: %d' % iPtr)
    # print iPtr

    # Reads Instructions from file
    instructions = directive.split('\t')[2]

    # Copies Instructions from File into Memory
    tempPtr = iPtr
    for bit in instructions:
        memory[tempPtr] = bit
        tempPtr += 1

    logging.info('\t\t\tInstructions Read')

def sizeDirective(directive):
    # Defines Global Reference
    global memory

    # Sets Size to the hex value given in the directive
    size = 2 * int(directive.split('\t')[1],16)
    memory = ['0'] * size

    logging.info('\t\t\tMemory Size Set to: %d' % size)

def byteDirective(directive):
    # Defines Global Reference
    global memory

    # Stores Location for byte to be stored
    tempPtr = int(directive.split('\t')[1], 16)

    # Copies both hex characters representing the byte into the given location in memory
    memory[tempPtr] = directive.split('\t')[2][0]
    memory[tempPtr + 1] = directive.split('\t')[2][1]

# Parameters - 'directives' : array of y86 file directives
# Interprets a list of directives and organizes the
def readDirectives(directives):
    for directive in directives:
        dirType = directive.split('\t')[0]
        try:
            directMethods[dirType](directive)
        except KeyError:
            logging.debug('\t\t\tInvalid Directive Caught')
# End Directives

# Operation Methods

def readInteger(localPtr):
    global memory
    hexStr = ''
    for i in xrange(3, -1, -1):
        for j in xrange(0, 2, 1):
            hexStr  = hexStr + memory[localPtr + ((2 * i) + j)]
    print hexStr
    return int(hexStr, 16)

def writeInteger(localPtr, value):
    global memory
    # integer value cast to its string representation
    decimalStr = chr(hex(value))
    print decimalStr

    # extends hex string
    while len(decimalStr) < 8 :
        decimalStr = '0' + decimalStr

def nop():
    global iPtr
    iPtr += 2
    logging.info('\t\tnop Operation Performed')
    print 'nop'

def halt():
    global iPtr
    iPtr += 2
    logging.info('\t\thalt Operation Performed')
    print 'halt'

def rrmovl():
    global iPtr, reg
    # rb = rA
    reg[memory[iPtr + 3]] = reg[memory[iPtr + 2]]
    iPtr += 4
    logging.info('\t\trrmovl Operation Performed')
    print 'rrmovl'

def irmovl():
    global iPtr, memory, reg
    # rB = [0x01234567]
    reg[memory[iPtr + 3]] = readInteger(iPtr + 4)
    # print reg[memory[iPtr + 3]]
    iPtr += 12
    logging.info('\t\tirmovl Operation Performed')
    print 'irmovl'

def rmmovl():
    global iPtr
    memory[]
    iPtr += 12
    print 'rmmovl'

def mrmovl():
    global iPtr
    iPtr += 12
    print 'mrmovl'

def op1():
    global iPtr
    iPtr += 4
    print 'op1'

def jXX():
    global iPtr
    iPtr += 10
    print 'jXX'

def call():
    global iPtr
    iPtr += 10
    print 'call'

def ret():
    global iPtr
    iPtr += 2
    print 'ret'

def pushl():
    global iPtr
    iPtr += 4
    print 'pushl'

def popl():
    global iPtr
    iPtr += 4
    print 'popl'

def readX():
    global iPtr
    iPtr += 12
    print 'readX'

def writeX():
    global iPtr
    iPtr += 12
    print 'writeX'

def movsbl():
    global iPtr
    iPtr += 12
    print 'movsbl'

def run():
    global memory, iPtr, reg, opMethods

    while memory[iPtr] is not '1':
        opMethods[memory[iPtr]]()
    # else:
    #     opMethods[memory[iPtr]]()
    #     break
    opMethods[memory[iPtr]]()

# End Operation Methods

# Global Variables

memory = None # Reference to "Memory" for the emulator.
iPtr = 0 # Reference to the current Instruction Pointer for the emulator.
reg = {'0':0, '1':0, '2':0, '3':0, '4':0, '5':0, '6':0, '7':0}
directMethods = {'.text' : textDirective, '.size' : sizeDirective, '.byte' : byteDirective}
opMethods = {'0' : nop, '1' : halt, '2' : rrmovl, '3' : irmovl, '4' : rmmovl, '5' : mrmovl, '6' : op1, '7' : jXX,
             '8' : call, '9' : ret, 'a' : pushl, 'b' : popl, 'c' : readX, 'd' : writeX, 'e' : movsbl}

# End Global Variables

# Begin Main
logging.basicConfig(filename = 'emul.log', level = logging.DEBUG, filemode = 'w')

y86Filename = argv[1]

logging.info('\tFile Read -> %s' % y86Filename)

# Assurses that a file of the proper format is being read.
if(not y86Filename.endswith('.y86')):
    logging.debug('\t\tError: Invalid Filename')
    print 'Error Invalid Filename'
    raise SystemExit

# Attempts to open file passed from arguements.
try:
    file = open(y86Filename, 'r')
except IOError:
    # Handles error if file is not found.
    logging.debug('\t\tError: File \'%s\' not found in directory.' % y86Filename)
    print 'Error: File \'%s\' not found in directory.' % y86Filename
    raise SystemExit

lines = file.read().split('\n')

readDirectives(lines)

run()


# for line in lines:
#     pieces = line.split('\t')
#     for part in pieces:
#         print part

# print memory
