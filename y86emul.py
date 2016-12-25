from sys import argv
import logging

memory = None # Reference to "Memory" for the emulator.
iPtr = 0 # Reference to the current Instruction Pointer for the emulator.

def textDirective(directive):
    # Defines Global References
    global iPtr
    global memory

    # Sets Instruction Pointer
    iPtr = int(directive.split('\t')[1])
    logging.info('\t\t\tInitial Instruction Pointer Set to: %d' % iPtr)
    # print iPtr

    # Reads Instructions from file
    instructions = directive.split('\t')[2]

    # Copies Instructions from File into Memory
    tempPtr = iPtr
    for bit in instructions:
        memory[iPtr] = bit
        iPtr += 1

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
        if dirType == '.byte':
            logging.info('\t\t%s Directive' % dirType)
            byteDirective(directive)
        elif dirType == '.size':
            logging.info('\t\t%s Directive' % dirType)
            sizeDirective(directive)
        elif dirType == '.text':
            logging.info('\t\t%s Directive' % dirType)
            textDirective(directive)
        else:
            logging.debug('\t%s is an Invalid Directive' % dirType)

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

# for line in lines:
#     pieces = line.split('\t')
#     for part in pieces:
#         print part

print memory
