library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity ALU is
    Port (
        opcodeB : in std_logic_vector(2 downto 0);  -- 3-bit opcode for the operation
        mode    : in std_logic_vector(1 downto 0);  -- Mode selection (used for immediate)
        imm3    : in std_logic_vector(2 downto 0);  -- 3-bit immediate value
        Rn_data : in std_logic_vector(15 downto 0); -- 16-bit Rn data input
        Rm_data : in std_logic_vector(15 downto 0); -- 16-bit Rm data input
        Rd_data : out std_logic_vector(15 downto 0) -- 16-bit Rd data output
    );
end ALU;

architecture Behavioral of ALU is
begin
    process(opcodeB, mode, imm3, Rn_data, Rm_data)
    begin
        case opcodeB is
            when "011" =>  -- Addition and Subtraction Operations
                case mode is
                    when "00" =>  -- Addition: Rd_data <= Rn_data + Rm_data
                        Rd_data <= std_logic_vector(unsigned(Rn_data) + unsigned(Rm_data));
                    when "01" =>  -- Subtraction: Rd_data <= Rn_data - Rm_data
                        Rd_data <= std_logic_vector(unsigned(Rn_data) - unsigned(Rm_data));
                    when "10" =>  -- Addition with Immediate: Rd_data <= Rn_data + Imm(2 downto 0)
                        Rd_data <= std_logic_vector(unsigned(Rn_data) + unsigned("000000000000" & imm3));
                    when "11" =>  -- Subtraction with Immediate: Rd_data <= Rn_data - Imm(2 downto 0)
                        Rd_data <= std_logic_vector(unsigned(Rn_data) - unsigned("000000000000" & imm3));
                    when others =>
                        Rd_data <= (others => '0');  -- Default case
                end case;
            when others =>
                Rd_data <= (others => '0');  -- Default case for other opcodeB values
        end case;
    end process;
end Behavioral;
