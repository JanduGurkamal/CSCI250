import sys
import re

def usage():
    print("Usage: python3 asm_arm16.py SRC_CODE [-o OUT_FILE]")
    sys.exit(1)

if len(sys.argv) < 2:
    usage()

src_file = sys.argv[1]
out_file = "./a.out"
if "-o" in sys.argv:
    idx = sys.argv.index("-o")
    if idx < len(sys.argv)-1:
        out_file = sys.argv[idx+1]

with open(src_file, 'r') as f:
    lines = f.readlines()

clean_lines = []
for line in lines:
    line = line.split(';', 1)[0].strip()
    if line:
        clean_lines.append(line)

def parse_imm(token):
    val_str = token.strip()
    if val_str.startswith('#'):
        val_str = val_str[1:]
    if val_str.startswith('0x'):
        return int(val_str,16)
    elif val_str.startswith('0b'):
        return int(val_str,2)
    else:
        return int(val_str,10)

def parse_reg(token):
    token = token.strip().lower().strip(',')
    if token == 'pc':
        return 7
    if token.startswith('x') or token.startswith('r'):
        num = int(token[1:])
        if 0 <= num <= 6:
            return num
    raise ValueError("Invalid register: " + token)

def is_register(token):
    t = token.lower().strip(',')
    if t == 'pc':
        return True
    if (t.startswith('x') or t.startswith('r')) and t[1:].isdigit():
        num = int(t[1:])
        return 0 <= num <= 6
    return False

def instruction_size(line):
    parts = line.split()
    if not parts:
        return 0
    if line.endswith(':'):
        return 0
    instr = parts[0].upper()
    if instr == '.GLOBAL':
        return 0
    # Assume MOV, ADD, SUB, HALT, B => 2 bytes
    # BL => 4 bytes
    if instr == 'BL':
        return 4
    return 2

# First pass
symbols = {}
current_address = 0
globals_set = set()

for line in clean_lines:
    if line.endswith(':'):
        label = line[:-1].strip()
        symbols[label] = current_address
    else:
        parts = line.split()
        if parts and parts[0].lower() == '.global':
            if len(parts) > 1:
                globals_set.add(parts[1])
        else:
            current_address += instruction_size(line)

if '_main' not in symbols:
    print("Error: _main not defined.")
    sys.exit(1)
if '_main' not in globals_set:
    print("Error: _main not declared global.")
    sys.exit(1)

binary = bytearray()
current_address = 0

def encode_mov(parts, pc):
    if len(parts) != 3:
        raise ValueError("MOV syntax: MOV <dest>, <src/imm>")
    dest = parse_reg(parts[1].strip(','))
    src = parts[2]

    # If dest is PC, only MOV PC, x6 allowed
    if dest == 7:
        if is_register(src):
            src_reg = parse_reg(src)
            if src_reg == 6:
                return bytes([0x10, ((7<<3)|6)])
            else:
                raise ValueError("Direct PC modification not allowed except via MOV PC, x6.")
        else:
            raise ValueError("Direct PC modification not allowed except via MOV PC, x6.")

    if is_register(src):
        src_reg = parse_reg(src)
        return bytes([0x10, ((dest&0x7)<<3)|(src_reg&0x7)])
    else:
        imm = parse_imm(src)
        if imm < 0 or imm > 31:
            raise ValueError("Immediate out of range for MOV.")
        return bytes([0x11, ((dest&0x7)<<5)|(imm&0x1F)])

def encode_add(parts, pc):
    if len(parts) != 4:
        raise ValueError("ADD syntax: ADD <dest>, <src1>, <src2/imm>")
    dest = parse_reg(parts[1].strip(','))
    src1 = parse_reg(parts[2].strip(','))
    op3 = parts[3]

    if is_register(op3):
        src2 = parse_reg(op3)
        return bytes([0x20, ((dest&0x7)<<6)|((src1&0x7)<<3)|(src2&0x7)])
    else:
        imm = parse_imm(op3)
        if imm < 0 or imm > 255:
            raise ValueError("Immediate too large for ADD.")
        return bytes([0x21, ((dest&0x7)<<3)|(src1&0x7), imm&0xFF])

def encode_sub(parts, pc):
    if len(parts) != 4:
        raise ValueError("SUB syntax: SUB <dest>, <src1>, <src2/imm>")
    dest = parse_reg(parts[1].strip(','))
    src1 = parse_reg(parts[2].strip(','))
    op3 = parts[3]
    if is_register(op3):
        src2 = parse_reg(op3)
        return bytes([0x22, ((dest&0x7)<<6)|((src1&0x7)<<3)|(src2&0x7)])
    else:
        imm = parse_imm(op3)
        if imm < 0 or imm > 255:
            raise ValueError("Immediate too large for SUB.")
        return bytes([0x23, ((dest&0x7)<<3)|(src1&0x7), imm&0xFF])

def encode_b(parts, pc):
    if len(parts) != 2:
        raise ValueError("B syntax: B <label>")
    label = parts[1]
    if label not in symbols:
        raise ValueError("Undefined label: " + label)
    target = symbols[label]
    offset = (target - (pc+2))//2
    if offset < 0 or offset > 255:
        raise ValueError("Branch out of range.")
    return bytes([0x30, offset & 0xFF])

def encode_bl(parts, pc):
    if len(parts) != 2:
        raise ValueError("BL syntax: BL <label>")
    label = parts[1]
    if label not in symbols:
        raise ValueError("Undefined label: " + label)
    target = symbols[label]
    ret_addr = pc+4
    ret_imm = ret_addr & 0x1F
    mov_ins = bytes([0x11, (6<<5)|ret_imm])
    offset = (target-(pc+4))//2
    if offset < 0 or offset > 255:
        raise ValueError("Branch out of range for BL.")
    b_ins = bytes([0x30, offset & 0xFF])
    return mov_ins + b_ins

def encode_halt():
    return bytes([0xFF,0x00])

def encode_instruction(line, pc):
    parts = line.split()
    instr = parts[0].upper()
    if instr == '.GLOBAL' or line.endswith(':'):
        return None
    if instr == 'MOV':
        return encode_mov(parts, pc)
    elif instr == 'ADD':
        return encode_add(parts, pc)
    elif instr == 'SUB':
        return encode_sub(parts, pc)
    elif instr == 'B':
        return encode_b(parts, pc)
    elif instr == 'BL':
        return encode_bl(parts, pc)
    elif instr == 'HALT':
        return encode_halt()
    else:
        raise ValueError("Unknown instruction: " + instr)

current_address = 0
for line in clean_lines:
    if line.endswith(':'):
        continue
    parts = line.split()
    if not parts:
        continue
    if parts[0].lower() == '.global':
        continue
    ins = encode_instruction(line, current_address)
    if ins:
        binary.extend(ins)
        current_address += len(ins)

# Let's say we want 256 words total (512 bytes), with 8 words per line.
total_words = 256
words_per_line = 8

# Ensure even length of binary for 16-bit words
if len(binary) % 2 != 0:
    binary.append(0)

num_instructions = len(binary)//2
output_lines = []

for i in range(total_words):
    if i < num_instructions:
        high = binary[i*2]
        low = binary[i*2+1]
        word_val = (high << 8) | low
        word_str = f"{word_val:04X}"
    else:
        word_str = "XXXX"
    output_lines.append(word_str)

# Write to a.out
with open(out_file, 'w') as f:
    for i in range(0, total_words, words_per_line):
        row = output_lines[i:i+words_per_line]
        f.write(" ".join(row) + "\n")

print(f"Assembled {src_file} successfully to {out_file}")
