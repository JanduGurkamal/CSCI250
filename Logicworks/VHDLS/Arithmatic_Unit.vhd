library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity ALU is
    Port (
        opcodeB : in std_logic_vector(2 downto 0);  -- 3-bit opcode for the operation
        mode    : in std_logic_vector(1 downto 0);  -- 2-bit mode code
        imm     : in std_logic_vector(7 downto 0);  -- 8-bit immediate value
        Rn_data : in std_logic_vector(15 downto 0); -- 16-bit Rn data input
        Rm_data : in std_logic_vector(15 downto 0); -- 16-bit Rm data input
        Rd_data : out std_logic_vector(15 downto 0) -- 16-bit Rd data output
    );
end ALU;

architecture Behavioral of ALU is
begin
    process(opcodeB, mode, imm, Rn_data, Rm_data)
        variable imm3_16bit : std_logic_vector(15 downto 0);
        variable imm8_16bit : std_logic_vector(15 downto 0);
        variable result     : unsigned(15 downto 0);
    begin
        -- Zero extend the 3-bit immediate value to 16 bits
        imm3_16bit := (others => '0');
        imm3_16bit(2 downto 0) := imm(2 downto 0);

        -- Zero extend the 8-bit immediate value to 16 bits
        imm8_16bit := (others => '0');
        imm8_16bit(7 downto 0) := imm;

        case opcodeB is
            when "011" =>  -- Arithmetic Operations
                case mode is
                    when "00" =>  -- Addition: Rd_data <= Rn_data + Rm_data
                        result := unsigned(Rn_data) + unsigned(Rm_data);
                        Rd_data <= std_logic_vector(result);
                    when "01" =>  -- Subtraction: Rd_data <= Rn_data - Rm_data
                        result := unsigned(Rn_data) - unsigned(Rm_data);
                        Rd_data <= std_logic_vector(result);
                    when "10" =>  -- Addition with 3-bit Immediate: Rd_data <= Rn_data + imm(2 downto 0)
                        result := unsigned(Rn_data) + unsigned(imm3_16bit);
                        Rd_data <= std_logic_vector(result);
                    when "11" =>  -- Subtraction with 3-bit Immediate: Rd_data <= Rn_data - imm(2 downto 0)
                        result := unsigned(Rn_data) - unsigned(imm3_16bit);
                        Rd_data <= std_logic_vector(result);
                    when others =>
                        Rd_data <= (others => '0');  -- Default case for undefined modes
                end case;
            when "100" =>  -- Move Operation (MOV): Rd_data <= imm
                Rd_data <= imm8_16bit;  -- Zero-extend imm to 16 bits
            when "110" =>  -- Immediate Addition: Rd_data <= Rn_data + imm
                result := unsigned(Rn_data) + unsigned(imm8_16bit);
                Rd_data <= std_logic_vector(result);
            when "111" =>  -- Immediate Subtraction: Rd_data <= Rn_data - imm
                result := unsigned(Rn_data) - unsigned(imm8_16bit);
                Rd_data <= std_logic_vector(result);
            when others =>
                Rd_data <= (others => '0');  -- Default case for unimplemented opcodes
        end case;
    end process;
end Behavioral;