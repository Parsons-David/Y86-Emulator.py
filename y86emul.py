from sys import argv
import logging, sys, signal

# Directives
def textDirective(directive):
    # Defines Global References
    global iPtr, memory

    # Sets Instruction Pointer
    iPtr = 2 * int(directive.split('\t')[1], 16)
    logging.info('\t\t\tInitial Instruction Pointer Set to: %d' % iPtr)

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
    tempPtr = 2 * int(directive.split('\t')[1], 16)

    # Copies both hex characters representing the byte into the given location in memory
    logging.info('\t\t\tPlacing %c at %d', directive.split('\t')[2][0], tempPtr)
    memory[tempPtr] = directive.split('\t')[2][0]
    logging.info('\t\t\tPlacing %c at %d', directive.split('\t')[2][1], tempPtr + 1)
    memory[tempPtr + 1] = directive.split('\t')[2][1]

def stringDirective(directive):
    # Defines Global Reference
    global memory

    # Stores Location for string to be stored
    tempPtr = 2 * int(directive.split('\t')[1], 16)

    # String with "" removed
    st = directive.split('\t')[2].replace("\"", "")

    # Places every char in memory stored as its hex ascii representation
    for c in st:
        logging.info('\t\t\tPlacing %c at %d', hex(ord(c)).split('x')[1][0], tempPtr)
        memory[tempPtr] = hex(ord(c)).split('x')[1][0]
        logging.info('\t\t\tPlacing %c at %d', hex(ord(c)).split('x')[1][1], tempPtr + 1)
        memory[tempPtr + 1] = hex(ord(c)).split('x')[1][1]
        tempPtr += 2

def longDirective(directive):
    # Defines Global Reference
    global memory

    # Stores Location for long to be stored
    tempPtr = 2 * int(directive.split('\t')[1], 16)

    # Writes Decimal Int to given memory loaction
    logging.info('\t\t\tStoring %d at %d', int(directive.split('\t')[2]), tempPtr)
    writeInteger (tempPtr, int(directive.split('\t')[2]))

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

    output = int(hexStr, 16)

    if output > 0x7FFFFFFF:
        output -= 0x100000000

    return output

def writeInteger(localPtr, value):
    global memory

    if value < 0:
        logging.debug('\t\t\tValue written to memory was negative: %d', value)

    # integer value cast to its string representation
    hexStr = hex(value).split('x')[1]

    # extends hex string
    while len(hexStr) < 8 :
        # Sign Extends the integer
        hexStr = ('1' if value < 0 else '0') + hexStr

    finalStr = ''
    for i in xrange(3, -1, -1):
        for j in xrange(0, 2, 1):
            finalStr  = finalStr + hexStr[((2 * i) + j)]

    logging.info('\t\t\tWriting %d -> %s -> %s to %d' % (value, hexStr, finalStr, localPtr))

    for i in xrange(0, 8, 1):
        memory[localPtr + i] = finalStr[i]

def nop(): # add 00 check
    global iPtr
    iPtr += 2
    logging.info('\t\tnop Operation Performed')

def halt(): # add 10 check
    global iPtr
    iPtr += 2
    logging.info('\t\thalt Operation Performed')

def rrmovl(): # add 20 and reg check
    global iPtr, reg
    # rb = rA
    reg[memory[iPtr + 3]] = reg[memory[iPtr + 2]]
    logging.info('\t\trrmovl Operation Performed\n\t\t\treg[%s] = %d' % (memory[iPtr + 3], reg[memory[iPtr + 2]]))
    iPtr += 4

def irmovl(): # add 30F and reg check
    global iPtr, memory, reg
    # rB = [0x01234567]
    reg[memory[iPtr + 3]] = readInteger(iPtr + 4)
    logging.info('\t\tirmovl Operation Performed\n\t\t\treg[%s] = %d' % (memory[iPtr + 3],  readInteger(iPtr + 4)))
    iPtr += 12

def rmmovl(): # add 50 check
    global iPtr, memory, reg
    # memory[rB + 0x01234567] = rA
    tempPtr = 2 * (readInteger(iPtr + 4) + reg[memory[iPtr + 3]])

    logging.info('\t\trmmovl Operation Performed\n\t\t\tmemory[2 * (reg[%s] + %d)] = %d' % (memory[iPtr + 3], readInteger(iPtr + 4), reg[memory[iPtr + 2]]))
    writeInteger(tempPtr, reg[memory[iPtr + 2]])
    iPtr += 12

def mrmovl():
    global iPtr, memory, reg

    logging.info('\t\tmrmovl Operation Performed\n\t\t\treg[%s] = memory[reg[%s] + %d] -> %d' % (memory[iPtr + 2], memory[iPtr + 3], readInteger(iPtr + 4), readInteger(reg[memory[iPtr + 3]] + readInteger(iPtr + 4))))

    reg[memory[iPtr + 2]] = readInteger(2 * (reg[memory[iPtr + 3]] + readInteger(iPtr + 4)))

    iPtr += 12

def addl(rA, rB):
    global reg, OF, SF, ZF

    if((reg[rA] > 0 and reg[rB] > 0 and (reg[rA] + reg[rB]) < 0) or (reg[rA] < 0 and reg[rB] < 0 and (reg[rA] + reg[rB]) > 0)):
      OF = 1
    else:
      OF = 0

    reg[rB] += reg[rA]

    logging.info('\t\taddl Operation Performed\n\t\t\treg[%s] = reg[%s] + reg[%s]' % (rB, rA, rB))

    SF = 1 if (0 > reg[rB]) else 0

    ZF = 1 if (0 == reg[rB]) else 0

def subl(rA, rB):
    global reg, OF, SF, ZF

    if((reg[rA] < 0 and reg[rB] > 0 and (reg[rA] - reg[rB]) > 0) or (reg[rA] > 0 and reg[rB] < 0 and (reg[rA] - reg[rB]) < 0)):
      OF = 1
    else:
      OF = 0

    reg[rB] -= reg[rA]

    logging.info('\t\tsubl Operation Performed\n\t\t\treg[%s] = reg[%s] - reg[%s]' % (rB, rA, rB))

    SF = 1 if (0 > reg[rB]) else 0

    ZF = 1 if (0 == reg[rB]) else 0

def andl(rA, rB):
    global reg, OF, SF, ZF

    OF = 0

    logging.info('\t\tandl Operation Performed\n\t\t\treg[%s] & reg[%s]' % (rA, rB))

    SF = 1 if (0 > (reg[rB] & reg[rA])) else 0

    ZF = 1 if (0 == (reg[rB] & reg[rA])) else 0

def xorl(rA, rB):
    global reg, OF, SF, ZF

    OF = 0

    logging.info('\t\txorl Operation Performed\n\t\t\treg[%s] xor reg[%s]' % (rA, rB))

    SF = 1 if (0 > (reg[rB] ^ reg[rA])) else 0

    ZF = 1 if (0 == (reg[rB] ^ reg[rA])) else 0

def mull(rA, rB):
    global reg, OF, SF, ZF

    if((reg[rA] > 0 and reg[rB] > 0 and (reg[rA] * reg[rB]) < 0) or (reg[rA] < 0 and reg[rB] < 0 and (reg[rA] * reg[rB]) < 0) or (reg[rA] > 0 and reg[rB] < 0 and (reg[rA] * reg[rB]) > 0) or (reg[rA] < 0 and reg[rB] > 0 and (reg[rA] * reg[rB]) > 0)) :
      OF = 1
    else :
      OF = 0

    reg[rB] *= reg[rA]

    logging.info('\t\tmull Operation Performed\n\t\t\treg[%s] = reg[%s] * reg[%s]' % (rB, rA, rB))

    SF = 1 if (0 > reg[rB]) else 0

    ZF = 1 if (0 == reg[rB]) else 0

def cmpl(rA, rB):
    global reg, OF, SF, ZF

    OF = 0

    logging.info('\t\tcmpl Operation Performed\n\t\t\treg[%s] == reg[%s]' % (rA, rB))

    SF = 1 if (0 > (reg[rB] - reg[rA])) else 0

    ZF = 1 if (0 == (reg[rB] - reg[rA])) else 0

def op1():
    global iPtr, memory, reg
    if(memory[iPtr] is not '6'):
        logging.debug('\tSYNTAX ERROR: 6fn expected for op1')
    try:
        ops[memory[iPtr + 1]](memory[iPtr + 2], memory[iPtr + 3])
    except KeyError:
        print 'Op not found'
    iPtr += 4

def jXX():
    global iPtr

    destination = 2 * readInteger(iPtr + 2)

    jmpType = memory[iPtr + 1]

    if jmpType is '0' :
        logging.info('\t\tjmp Operation Performed\n\t\t\tjumping to %d' % (destination))
        iPtr = destination
        return
    elif jmpType is '1' :
        logging.info('\t\tjle Operation Performed')
        if ((SF ^ OF) or ZF):
            iPtr = destination
            logging.info('\t\t\tJumping to %d' % (destination))
            return
    elif jmpType is '2' :
        logging.info('\t\tjl Operation Performed')
        if (SF ^ OF):
            iPtr = destination
            logging.info('\t\t\tJumping to %d' % (destination))
            return
    elif jmpType is '3' :
        logging.info('\t\tje Operation Performed\n\t\t\tZF = %d' % (ZF))
        if (ZF == 1):
            iPtr = destination
            logging.info('\t\t\tJumping to %d' % (destination))
            return
    elif jmpType is '4' :
        logging.info('\t\tjne Operation Performed\n\t\t\tZF = %d' % (ZF))
        if (ZF == 0):
            iPtr = destination
            logging.info('\t\t\tJumping to %d' % (destination))
            return
    elif jmpType is '5' :
        logging.info('\t\tjge Operation Performed')
        if (not(SF ^ OF)):
            iPtr = destination
            logging.info('\t\t\tJumping to %d' % (destination))
            return
    elif jmpType is '6' :
        logging.info('\t\tjg Operation Performed')
        if ((not(SF ^ OF)) or (not ZF)):
            iPtr = destination
            logging.info('\t\t\tJumping to %d' % (destination))
            return

    iPtr += 10

def call():
    global iPtr, memory, reg

    destination = 2 * readInteger(iPtr + 2)

    reg['4'] -= 4

    iPtr += 10

    logging.info('\t\tcall Operation Performed\n\t\t\tPushed %d to memory[%d]\n\t\t\tiPtr now: %d' % ((iPtr/2), 2 * reg['4'], destination))

    writeInteger(2 * reg['4'], iPtr/2)

    iPtr = destination


def ret():
    global iPtr, reg

    iPtr = 2 * readInteger(2 * reg['4'])

    logging.info('\t\tret Operation Performed\n\t\t\tiPtr now: %d' % (iPtr/2))

    reg['4'] += 4


def pushl():
    global iPtr

    reg['4'] -= 4

    logging.info('\t\tpushl Operation Performed\n\t\t\tPushed reg[%s] = %d to memory[%d]' % (memory[iPtr + 2], reg[memory[iPtr + 2]], 2 * reg['4']))

    writeInteger(2 * reg['4'], reg[memory[iPtr + 2]])

    iPtr += 4

def popl():
    global iPtr, reg, memory

    reg[memory[iPtr + 2]] = readInteger(2 * reg['4'])

    logging.info('\t\tpopl Operation Performed\n\t\t\treg[%s] = %d ' % (memory[iPtr + 2], readInteger(reg['4'])))

    reg['4'] += 4

    iPtr += 4

def readX():
    global iPtr, memory, reg, ZF

    # Location in Memory for byte or int to be written
    tempPtr = 2 * (readInteger(iPtr + 4) + reg[memory[iPtr + 2]])
    ZF = 0

    try:
        inVal = raw_input("")
    except KeyboardInterrupt:
        inVal = ""
        ZF = 1
        logging.debug('\t\t\tCaught KeyboardInterrupt')


    logging.info('\t\treadx Operation Performed')

    if(memory[iPtr + 1] == '0'):
        # Gets only the first byte
        inVal = hex(ord(inVal[0])).split('x')[1]

        # Stores byte at tempPtr
        logging.info('\t\t\tPlacing %c at %d', inVal[0], tempPtr)
        memory[tempPtr] = inVal[0]
        logging.info('\t\t\tPlacing %c at %d', inVal[1], tempPtr + 1)
        memory[tempPtr + 1] = inVal[1]

    elif (memory[iPtr + 1] == '1'):
        try:
            inVal = int(inVal)
        except ValueError:
            inVal = -1
        logging.info('\t\t\tPlacing %d at %d', inVal, tempPtr)
        writeInteger(tempPtr, inVal)
    else:
        #Error
        a = 9

    iPtr += 12

def writeX():
    global iPtr, reg, memory
    localPtr = 2 * (reg[memory[iPtr + 2]]  + readInteger(iPtr + 4))

    if(memory[iPtr + 1] == '0'):

        byte = memory[localPtr] + memory[localPtr + 1]

        sys.stdout.write(chr(int(byte, 16)))

        logging.info('\t\twriteb Operation Performed\n\t\t\tChar @%d = %s (ASCII %d, Hex %s, Chars %c%c)' % (localPtr/2, chr(int(byte, 16)), int(byte, 16), byte, memory[localPtr], memory[localPtr + 1]))

    elif(memory[iPtr + 1] == '1'):

        val = readInteger(localPtr)

        sys.stdout.write('%d' % val)

        logging.info('\t\twritel Operation Performed\n\t\t\tInt @%d = %d' % (localPtr/2, val))
    #
    # else:
    #     # Error
    iPtr += 12

def movsbl():
    global iPtr, reg, memory

    localPtr = 2 * (reg[memory[iPtr + 3]]  + readInteger(iPtr + 4))

    byte = int((memory[localPtr] + memory[localPtr + 1]), 16)

    logging.info('\t\tmovsbl Operation Performed\n\t\t\treg[%s] = %d -> %s' % (memory[iPtr + 2], byte, memory[localPtr] + memory[localPtr + 1]))

    reg[memory[iPtr + 2]] = byte

    iPtr += 12

def run():
    global memory, iPtr, reg, instructMethods

    while memory[iPtr] is not '1':
        instructMethods[memory[iPtr]]()
    # else:
    #     instructMethods[memory[iPtr]]()
    #     break
    instructMethods[memory[iPtr]]()

# End Operation Methods

# Global Variables

memory = None # Reference to "Memory" for the emulator.
iPtr = 0 # Reference to the current Instruction Pointer for the emulator.
reg = {'0':0, '1':0, '2':0, '3':0, '4':0, '5':0, '6':0, '7':0}
ops = {'0' : addl, '1' : subl, '2' : andl, '3' : xorl, '4' : mull, '5' : cmpl}
directMethods = {'.text' : textDirective, '.size' : sizeDirective, '.byte' : byteDirective, '.string' : stringDirective,
                '.long' : longDirective}
instructMethods = {'0' : nop, '1' : halt, '2' : rrmovl, '3' : irmovl, '4' : rmmovl, '5' : mrmovl, '6' : op1, '7' : jXX,
             '8' : call, '9' : ret, 'a' : pushl, 'b' : popl, 'c' : readX, 'd' : writeX, 'e' : movsbl}

OF = 0
SF = 0
ZF = 0


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
