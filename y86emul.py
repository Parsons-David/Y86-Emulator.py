from sys import argv
import logging, sys

# Directives
def textDirective(directive):
    # Defines Global References
    global iPtr, memory

    # Sets Instruction Pointer
    iPtr = int(directive.split('\t')[1])
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

    return int(hexStr, 16)

def writeInteger(localPtr, value):
    global memory
    # integer value cast to its string representation
    hexStr = hex(value).split('x')[1]

    # extends hex string
    while len(hexStr) < 8 :
        hexStr = '0' + hexStr

    finalStr = ''
    for i in xrange(3, -1, -1):
        for j in xrange(0, 2, 1):
            finalStr  = finalStr + hexStr[((2 * i) + j)]

    for i in xrange(0, 8, 1):
        memory[localPtr + i] = finalStr[i]

    logging.info('\t\t\tWriting %d -> %s -> %s to %d' % (value, hexStr, finalStr, localPtr))

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
    # Coming back to this for prog2
    global iPtr, memory, reg
    # memory[rB + 0x01234567] = rA
    writeInteger(2 * (reg[memory[iPtr + 3]] + readInteger(iPtr + 4)), reg[memory[iPtr + 2]])
    logging.info('\t\trmmovl Operation Performed\n\t\t\tmemory[2 * (reg[%s] + %d)] = %d' % (memory[iPtr + 3], readInteger(iPtr + 4), reg[memory[iPtr + 2]]))
    iPtr += 12

def mrmovl():
    global iPtr, memory, reg

    logging.info('\t\tmrmovl Operation Performed\n\t\t\treg[%s] = memory[reg[%s] + %d] -> %d' % (memory[iPtr + 3], memory[iPtr + 2], readInteger(iPtr + 4), readInteger(reg[memory[iPtr + 2]] + readInteger(iPtr + 4))))

    reg[memory[iPtr + 3]] = readInteger(2 * (reg[memory[iPtr + 2]] + readInteger(iPtr + 4)))

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
        if ((SF ^ OF) or ZF):
            iPtr = destination
            return
    elif jmpType is '2' :
        if ((SF ^ OF) or ZF):
            iPtr = destination
            return
    elif jmpType is '3' :
        logging.info('\t\tje Operation Performed\n\t\t\tZF = %d' % (ZF))
        if (ZF == 1):
            iPtr = destination
            logging.info('\t\t\tJumping to %d' % (destination))
            return
    elif jmpType is '4' :
        if (ZF == 0):
            iPtr = destination
            return
    elif jmpType is '5' :
        if ((SF ^ OF) or ZF):
            iPtr = destination
            return
    elif jmpType is '6' :
        if ((SF ^ OF) or ZF):
            iPtr = destination
            return

    iPtr += 10

def call():
    global iPtr, memory, reg

    destination = 2 * readInteger(iPtr + 2)

    reg[4] -= 4

    logging.info('\t\tcall Operation Performed\n\t\t\tPushed %d to memory[%d]\n\t\t\tiPtr now: %d' % (iPtr, reg[4], destination))

    writeInteger(reg[4], iPtr)

    iPtr = destination

    # iPtr += 10

def ret():
    global iPtr
    iPtr += 2

def pushl():
    global iPtr

    reg[4] -= 4

    logging.info('\t\tpushl Operation Performed\n\t\t\tPushed reg[%s] = %d to memory[%d]' % (memory[iPtr + 2], reg[memory[iPtr + 2]], reg[4]))

    writeInteger(reg[memory[iPtr + 2]], iPtr)

    iPtr += 4

def popl():
    global iPtr
    iPtr += 4

def readX():
    global iPtr
    iPtr += 12

def writeX():
    global iPtr, reg, memory
    localPtr = 2 * (reg[memory[iPtr + 2]]  + readInteger(iPtr + 4))
    byte = memory[localPtr] + memory[localPtr + 1]

    sys.stdout.write(chr(int(byte, 16)))

    logging.info('\t\twritex Operation Performed\n\t\t\tChar @%d = %s (ASCII %d, Hex %s, Chars %c%c)' % (localPtr/2, chr(int(byte, 16)), int(byte, 16), byte, memory[localPtr], memory[localPtr + 1]))
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
directMethods = {'.text' : textDirective, '.size' : sizeDirective, '.byte' : byteDirective}
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
