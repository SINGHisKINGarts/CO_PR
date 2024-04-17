class RISCV_Simulator:
    def __init__(self):
        self.registers = [0] * 32
        self.memory = [0] * 128  # Data memory size: 128 bytes
        self.pc = 0  # Program Counter

    def execute_instruction(self, instruction):
        opcode = instruction[:7]
        funct3 = instruction[17:20]
        rd = int(instruction[20:25], 2)
        rs1 = int(instruction[12:17], 2)
        rs2 = int(instruction[7:12], 2)
        imm_i = (int(instruction[0]) << 11) | int(instruction[0]) * 20 + int(instruction[24:])
        imm_s = (int(instruction[0]) << 11) | (int(instruction[31]) << 5) | int(instruction[25:31], 2) | (int(instruction[12:20], 2) << 5)
        imm_b = (int(instruction[0]) << 12) | (int(instruction[31]) << 11) | (int(instruction[7]) << 10) | (int(instruction[25:31], 2) << 4) | (int(instruction[8:12], 2) << 8) | (int(instruction[12:20], 2) << 1)
        imm_u = int(instruction[0:20], 2) << 12
        imm_j = (int(instruction[0]) << 19) | (int(instruction[31]) << 11) | (int(instruction[12:20], 2) << 1) | (int(instruction[20:31], 2) << 12)

        if opcode == '0110011':  # R-type instruction
            if funct3 == '000':  # add
                self.registers[rd] = self.registers[rs1] + self.registers[rs2]
            elif funct3 == '001':  # sll
                self.registers[rd] = self.registers[rs1] << self.registers[rs2]
            elif funct3 == '010':  # slt
                self.registers[rd] = int(self.registers[rs1] < self.registers[rs2])
            elif funct3 == '011':  # sltu
                self.registers[rd] = int(self.registers[rs1] < self.registers[rs2])
            elif funct3 == '100':  # xor
                self.registers[rd] = self.registers[rs1] ^ self.registers[rs2]
            elif funct3 == '101':  # srl/sra
                self.registers[rd] = self.registers[rs1] >> self.registers[rs2]
            elif funct3 == '110':  # or
                self.registers[rd] = self.registers[rs1] | self.registers[rs2]
            elif funct3 == '111':  # and
                self.registers[rd] = self.registers[rs1] & self.registers[rs2]

        elif opcode == '0010011':  # I-type instruction
            if funct3 == '000':  # addi
                self.registers[rd] = self.registers[rs1] + imm_i
            elif funct3 == '010':  # sltiu
                self.registers[rd] = int(self.registers[rs1] < imm_i)
            elif funct3 == '011':  # slti
                self.registers[rd] = int(self.registers[rs1] < imm_i)
            elif funct3 == '100':  # xori
                self.registers[rd] = self.registers[rs1] ^ imm_i
            elif funct3 == '110':  # ori
                self.registers[rd] = self.registers[rs1] | imm_i
            elif funct3 == '111':  # andi
                self.registers[rd] = self.registers[rs1] & imm_i
            elif funct3 == '001':  # slli
                self.registers[rd] = self.registers[rs1] << self.registers[rs2]
            elif funct3 == '101' and instruction[30:32] == '00':  # srli
                self.registers[rd] = self.registers[rs1] >> self.registers[rs2]
            elif funct3 == '101' and instruction[30:32] == '10':  # srai
                self.registers[rd] = self.registers[rs1] >> self.registers[rs2]  # Arithmetic shift right

        elif opcode == '0100011':  # S-type instruction
            address = self.registers[rs1] + imm_s
            if funct3 == '010':  # sw
                self.memory[address] = self.registers[rs2]

        
        elif opcode == '1100011':  # B-type instruction
            if funct3 == '000':  # beq
                if self.registers[rs1] == self.registers[rs2]:
                    self.pc += imm_b - 1  # PC will be incremented after this instruction, so decrement by 1
            elif funct3 == '001':  # bne
                if self.registers[rs1] != self.registers[rs2]:
                    self.pc += imm_b - 1  # PC will be incremented after this instruction, so decrement by 1
            elif funct3 == '100':  # blt
                if self.registers[rs1] < self.registers[rs2]:
                    self.pc += imm_b - 1  # PC will be incremented after this instruction, so decrement by 1
            elif funct3 == '101':  # bge
                if self.registers[rs1] >= self.registers[rs2]:
                    self.pc += imm_b - 1  # PC will be incremented after this instruction, so decrement by 1
            elif funct3 == '110':  # bltu
                if self.registers[rs1] < self.registers[rs2]:
                    self.pc += imm_b - 1  # PC will be incremented after this instruction, so decrement by 1
            elif funct3 == '111':  # bgeu
                if self.registers[rs1] >= self.registers[rs2]:
                    self.pc += imm_b - 1  # PC will be incremented after this instruction, so decrement by 1



        elif opcode == '1101111':  # J-type instruction (JAL)
            self.registers[rd] = self.pc + 4  # Store address of next instruction in rd
            self.pc += imm_j



        elif opcode == '0110111':  # U-type instruction (LUI)
            self.registers[rd] = imm_u

        elif opcode == '0010111':  # U-type instruction (AUIPC)
            self.registers[rd] = self.pc + imm_u

        elif opcode == '0000011':  # Load instruction (e.g., lw)
            address = self.registers[rs1] + imm_i
            self.registers[rd] = self.memory[address]

        elif opcode == '0100011':  # Store instruction (e.g., sw)
            address = self.registers[rs1] + imm_s
            self.memory[address] = self.registers[rs2]

        elif opcode == '1100011':  # Conditional branch instruction
            if funct3 == '000':  # beq
                if self.registers[rs1] == self.registers[rs2]:
                    self.pc += imm_b
            # Add more conditional branch instructions here

        elif opcode == '1101111':  # Jump and link (jal) instruction
            self.registers[rd] = self.pc + 4  # Store the return address
            self.pc += imm_j

    def simulate(self, program):
        instructions = [program[i:i+32] for i in range(0, len(program), 32)]

        while self.pc < len(instructions):
            instruction = instructions[self.pc]
            self.execute_instruction(instruction)
            self.pc += 1

        self.print_registers()
        self.print_memory()

    def print_registers(self):
        print("Register Values:")
        for i, value in enumerate(self.registers):
            print(f"x{i}: {value}")

    def print_memory(self):
        print("Memory Contents:")
        for i, value in enumerate(self.memory):
            print(f"Address {i}: {value}")

if __name__ == "__main__":
    file_path = "path"
    

    simulator = RISCV_Simulator()
    simulator.simulate(file_path)



