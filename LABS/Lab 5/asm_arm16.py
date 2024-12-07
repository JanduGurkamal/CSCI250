import sys

def usage():
    print("Usage: python3 asm_arm16.py SRC_CODE [-o OUT_FILE]")
    sys.exit(1)

if len(sys.argv) < 2:
    usage()

src_file = sys.argv[1]
out_file = "./a.out"
if "-o" in sys.argv:
    idx = sys.argv.index("-o")
    if idx < len(sys.argv) - 1:
        out_file = sys.argv[idx + 1]

with open(src_file, 'r') as f:
    lines = f.readlines()

clean_lines = []
for line in lines:
    line = line.split(';', 1)[0].strip()  # Strip comments and whitespace
    if line:
        clean_lines.append(line)

def parse_imm(token):
    val_str = token.strip()
    if val_str.startswith('#'):
        val_str = val_str[1:]
    if val_str.startswith('0x'):
        return int(val_str, 16)
    elif val_str.startswith('0b'):
        return int(val_str, 2)
    else:
        return int(val_str, 10)

def parse_reg(token):
    token = token.strip().lower().strip(',')
    if token == 'pc':
        return 7
    if token.startswith('r') or token.startswith('x'):
        num = int(token[1:])
        if 0 <= num <= 6:
            return num
    raise ValueError("Invalid register: " + token)

def reg_name(num):
    return 'pc' if num == 7 else f'r{num}'

def is_register(token):
    t = token.lower().strip(',')
    if t == 'pc':
        return True
    if (t.startswith('r') or t.startswith('x')) and t[1:].isdigit():
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
    return 4 if instr == 'BL' else 2

# First pass: Symbol resolution
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

# Instruction encoders
def encode_mov(parts, pc):
    if len(parts) != 3:
        raise ValueError("MOV syntax: MOV <dest>, <src/imm>")
    dest = parse_reg(parts[1].strip(','))
    src = parts[2]
    if is_register(src):
        src_reg = parse_reg(src)
        return bytes([0x10, ((dest & 0x7) << 3) | (src_reg & 0x7)])
    else:
        imm = parse_imm(src)
        if imm < 0 or imm > 31:
            raise ValueError("Immediate out of range for MOV.")
        return bytes([0x11, ((dest & 0x7) << 5) | (imm & 0x1F)])

def encode_add(parts, pc):
    if len(parts) != 4:
        raise ValueError("ADD syntax: ADD <dest>, <src1>, <src2/imm>")
    dest = parse_reg(parts[1].strip(','))
    src1 = parse_reg(parts[2].strip(','))
    op3 = parts[3]
    if is_register(op3):
        src2 = parse_reg(op3)
        return bytes([0x20, ((dest & 0x7) << 6) | ((src1 & 0x7) << 3) | (src2 & 0x7)])
    else:
        imm = parse_imm(op3)
        if imm < 0 or imm > 255:
            raise ValueError("Immediate too large for ADD.")
        return bytes([0x21, ((dest & 0x7) << 3) | (src1 & 0x7), imm & 0xFF])

def encode_mul(parts, pc):
    if len(parts) != 4:
        raise ValueError("MUL syntax: MUL <dest>, <src1>, <src2>")
    dest = parse_reg(parts[1].strip(','))
    src1 = parse_reg(parts[2].strip(','))
    src2 = parse_reg(parts[3].strip(','))
    return bytes([0x40, ((dest & 0x7) << 6) | ((src1 & 0x7) << 3) | (src2 & 0x7)])

def encode_branch(parts, pc):
    if len(parts) != 2:
        raise ValueError("B/B.cond syntax: B[.cond] <label>")
    instr = parts[0].upper()
    label = parts[1]
    if label not in symbols:
        raise ValueError("Undefined label: " + label)
    target = symbols[label]
    offset = (target - (pc + 2)) // 2
    if offset < -128 or offset > 127:
        raise ValueError("Branch out of range.")

    condition_codes = {
        "B": 0b11100,      # Unconditional branch
        "BGT": 0b11010,    # Branch if Greater Than
        "BLE": 0b11011,    # Branch if Less or Equal
        "BEQ": 0b11101,    # Branch if Equal (Z=1)
        "BNE": 0b11110,    # Branch if Not Equal (Z=0)
    }

    if instr not in condition_codes:
        raise ValueError("Unknown branch instruction: " + instr)

    cond = condition_codes[instr]
    return bytes([(cond << 3) | ((offset >> 8) & 0x07), offset & 0xFF])

def encode_bl(parts, pc):
    if len(parts) != 2:
        raise ValueError("BL syntax: BL <label>")
    label = parts[1]
    if label not in symbols:
        raise ValueError("Undefined label: " + label)
    target = symbols[label]
    ret_addr = pc + 4
    ret_imm = ret_addr & 0x1F
    mov_ins = bytes([0x11, (6 << 5) | ret_imm])  # MOV R6, return address
    offset = (target - (pc + 4)) // 2
    if offset < -128 or offset > 127:
        raise ValueError("Branch out of range for BL.")
    b_ins = bytes([0x30, offset & 0xFF])  # Branch to target
    return mov_ins + b_ins

def encode_cmp(parts, pc):
    if len(parts) != 3:
        raise ValueError("CMP syntax: CMP <Rn>, <Rm/imm>")
    rn = parse_reg(parts[1].strip(','))
    op2 = parts[2]
    if is_register(op2):
        rm = parse_reg(op2)
        return bytes([0x50, (rn << 3) | rm])
    else:
        imm = parse_imm(op2)
        if imm < 0 or imm > 255:
            raise ValueError("Immediate too large for CMP.")
        return bytes([0x51, (rn << 3), imm])

def encode_instruction(line, pc):
    parts = line.split()
    instr = parts[0].upper()
    if instr == '.GLOBAL' or line.endswith(':'):
        return None
    elif instr == 'MOV':
        return encode_mov(parts, pc)
    elif instr == 'ADD':
        return encode_add(parts, pc)
    elif instr == 'MUL':
        return encode_mul(parts, pc)  # Added MUL support
    elif instr == 'BL':
        return encode_bl(parts, pc)
    elif instr.startswith('B'):
        return encode_branch(parts, pc)
    elif instr == 'CMP':
        return encode_cmp(parts, pc)
    elif instr == 'HALT':
        return bytes([0xFF, 0x00])
    elif instr == 'NOP':
        return bytes([0x00, 0x00])
    else:
        raise ValueError("Unknown instruction: " + instr)

# Second pass: Encoding
current_address = 0
for line in clean_lines:
    if line.endswith(':'):
        continue
    ins = encode_instruction(line, current_address)
    if ins:
        binary.extend(ins)
        current_address += len(ins)

# Save binary output
if len(binary) % 2 != 0:
    binary.append(0)

with open(out_file, 'w') as f:
    for i in range(0, len(binary), 2):
        word = (binary[i] << 8) | binary[i + 1]
        f.write(f"{word:04X}\n")

print(f"Assembled {src_file} successfully to {out_file}")
