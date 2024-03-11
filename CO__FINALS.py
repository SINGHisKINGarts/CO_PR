types = {
    'R': ['add', 'sub', 'sll', 'slt', 'sltu', 'xor', 'srl', 'or', 'and'],
    'I': ['lw', 'addi', 'sltiu', 'jalr'],
    'S': ['sw'],
    'B': ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu'],
    'U': ['lui', 'auipc'],
    'J': ['jal'],
}

funct3s = {
    'add': '000', 'sub': '000', 'sll': '001', 'slt': '010', 'sltu': '011', 'xor': '100', 'srl': '101', 'or': '110', 'and': '111',
    'lw': '010', 'addi': '000', 'sltiu': '011', 'jalr': '000',
    'sw': '010',
    'beq': '000', 'bne': '001', 'blt': '100', 'bge': '101', 'bltu': '110', 'bgeu': '111',
}

opcodes = {
    'add': '0110011', 'sub': '0110011', 'sll': '0110011', 'slt': '0110011', 'sltu': '0110011', 'xor': '0110011',
    'srl': '0110011', 'or': '0110011', 'and': '0110011',
    'lw': '0000011', 'addi': '0010011', 'sltiu': '0010011', 'jalr': '1100111',
    'sw': '0100011',
    'beq': '1100011', 'bne': '1100011', 'blt': '1100011', 'bge': '1100011', 'bltu': '1100011', 'bgeu': '1100011',
    'lui': '0110111', 'auipc': '0010111',
    'jal': '1101111',
}

VIRTUAL_HALT_INSTRUCTION_BIN = "00000000000000000000000001100011"
errMsg = ""


def b_to_d(binary_str):
    if binary_str[0] == "1":
        inverted_binary = "".join(["1" if bit == "0" else "0" for bit in binary_str])
        decimal_value = int(inverted_binary, 2) + 1
        return -decimal_value
    else:
        return int(binary_str, 2)


def convert_to_binary(num, num_bits, validate=True):
    binary_string = None
    try:
        num = int(num)
        binary_string = bin(num & int("1" * num_bits, 2))[2:]
    except:
        binary_string = custom_binary_conversion(num)

    padded_binary = binary_string.zfill(num_bits)

    if validate and b_to_d(padded_binary) != num:
        global error_message
        error_message = "Invalid Immediate Value"
        return None

    return str(padded_binary)


def custom_binary_conversion(s):
    if s == 'zero':
        return '00000'
    if s == 'ra':
        return '00001'
    if s == 'sp':
        return '00010'
    if s == 'gp':
        return '00011'
    if s == 'tp':
        return '00100'
    if s == 't0':
        return '00101'
    if s == 't1' or s == 't2':
        return '00' + convert_to_binary(int(s[1:]) + 5, 3, False)
    if s == 's0' or s == 'fp':
        return '01000'
    if s == 's1':
        return '01001'
    if s == 'a0' or s == 'a1':
        return '0101' + convert_to_binary(int(s[1:]), 1, False)
    if s[0] == 'a':
        if 2 <= int(s[1:]) <= 5:
            return '011' + convert_to_binary(int(s[1:]) - 2, 2, False)
        if 6 <= int(s[1:]) <= 7:
            return '1000' + convert_to_binary((int(s[1:]) - 6), 1, False)
    if s[0] == 's' and 2 <= int(s[1:]) <= 11:
        return '1' + convert_to_binary(int(s[1:]), 4, False)
    if s[0] == 't' and 3 <= int(s[1:]) <= 6:
        return '111' + convert_to_binary(int(s[1:]) - 3, 2, False)

    global errMsg
    errMsg = f"Invalid Register '{s}'"
    return None


def parse_r_type(tokens):
    try:
        instruction, rd, rs1, rs2 = tokens
        funct7 = '0100000' if instruction == 'sub' else '0000000'
        return funct7 + custom_binary_conversion(rs2) + custom_binary_conversion(rs1) + funct3s[instruction] + custom_binary_conversion(rd) + opcodes[instruction]
    except:
        global errMsg
        if errMsg == "": errMsg = "Invalid Instruction Format"
        return None


def parse_i_type(tokens):
    try:
        instruction, rd, rs, imm = tokens
        if instruction == 'lw':
            rs, imm = imm, rs
        return convert_to_binary(imm, 12) + custom_binary_conversion(rs) + funct3s[instruction] + custom_binary_conversion(
            rd) + opcodes[instruction]
    except:
        global errMsg
        if errMsg == "": errMsg = "Invalid Instruction Format"
        return None


def parse_s_type(tokens):
    try:
        instruction, rs2, imm, rs1 = tokens
        bin_imm = convert_to_binary(imm, 12)
        return bin_imm[0:7] + custom_binary_conversion(rs2) + custom_binary_conversion(rs1) + funct3s[
            instruction] + bin_imm[7:] + opcodes[instruction]
    except:
        global errMsg
        if errMsg == "": errMsg = "Invalid Instruction Format"
        return None


def parse_b_type(tokens):
    try:
        instruction, rs1, rs2, imm = tokens
        bin_imm = convert_to_binary(imm, 16)
        return bin_imm[3] + bin_imm[5:11] + custom_binary_conversion(rs2) + custom_binary_conversion(
            rs1) + funct3s[instruction] + bin_imm[11:15] + bin_imm[4] + opcodes[instruction]
    except:
        global errMsg
        if errMsg == "": errMsg = "Invalid Instruction Format"
        return None


def parse_u_type(tokens):
    try:
        instruction, rd, imm = tokens
        return convert_to_binary(imm, 32)[:20] + custom_binary_conversion(rd) + opcodes[instruction]
    except:
        global errMsg
        if errMsg == "": errMsg = "Invalid Instruction Format"
        return None


def parse_j_type(tokens):
    try:
        instruction, rd, imm = tokens
        bin_imm = convert_to_binary(imm, 21)
        return bin_imm[0] + bin_imm[10:20] + bin_imm[9] + bin_imm[1:9] + custom_binary_conversion(
            rd) + opcodes[instruction]
    except:
        global errMsg
        if errMsg == "": errMsg = "Invalid Instruction Format"
        return None


def convert_instruction(instruction):
    global errMsg

    tokens = instruction.split()

    if tokens[0] in types['R']:
        binary = parse_r_type(tokens)
    elif tokens[0] in types['I']:
        binary = parse_i_type(tokens)
    elif tokens[0] in types['S']:
        binary = parse_s_type(tokens)
    elif tokens[0] in types['B']:
        binary = parse_b_type(tokens)
    elif tokens[0] in types['U']:
        binary = parse_u_type(tokens)
    elif tokens[0] in types['J']:
        binary = parse_j_type(tokens)
    else:
        errMsg = f"Invalid Instruction '{tokens[0]}'"
        binary = None

    if binary is not None and errMsg == "":
        return f"Binary representation: {binary}"
    else:
        return f"ERROR: {errMsg}"


def process_instructions_from_file(file_path):
    with open(file_path, 'r') as file:
        instructions = file.readlines()

    for instruction in instructions:
        result = convert_instruction(instruction.strip())
        print(result)


file_path = 'tests1.txt'
process_instructions_from_file(file_path)
