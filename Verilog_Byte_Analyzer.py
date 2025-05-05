import re
import argparse
import tkinter as tk
from tkinter import ttk, messagebox

# ───── Bit Field Mapping ─────
BIT_FIELD_MAP = {
    (8, 12): "opcode",
    (0, 3): "valid",
    (4, 7): "flag",
    (16, 23): "address",
    (24, 31): "immediate",
}
FIELD_NAME_MAP = {v: k for k, v in BIT_FIELD_MAP.items()}
RESERVED_WORDS = {
    "hex", "dec", "bin",
    "to_hex", "to_bin", "to_dec",
    "byte_align", "dw_align",
    "q"
}

# ───── Core Functions ─────
def parse_by_mode(input_str, mode):
    input_str = input_str.strip().lower()
    if mode == 'hex':
        match = re.search(r"(?:\d+)?'h([0-9a-fA-F_]+)", input_str)
        hex_digits = match.group(1) if match else input_str
        hex_digits = hex_digits.replace("_", "")
        if re.fullmatch(r'[0-9a-fA-F]+', hex_digits):
            return int(hex_digits, 16)
    elif mode == 'dec':
        if input_str.isdigit():
            return int(input_str)
    elif mode == 'bin':
        match = re.search(r"(?:\d+)?'b([01_]+)", input_str)
        bin_digits = match.group(1) if match else input_str
        bin_digits = bin_digits.replace("_", "")
        if re.fullmatch(r'[01]+', bin_digits):
            return int(bin_digits, 2)
    return None

def convert_to_bytes(value):
    if value == 0:
        return [0]
    result = []
    while value > 0:
        result.append(value & 0xFF)
        value >>= 8
    return result

def display_bytes(bytes_list, output_format, align_mode, bits_per_row=16):
    output = []
    if align_mode == 'byte_align':
        for i, b in enumerate(bytes_list):
            if output_format == 'hex':
                output.append(f"byte{i}: 8'h{b:02x}")
            elif output_format == 'dec':
                output.append(f"byte{i}: {b}")
            elif output_format == 'bin':
                bin_str = f"{b:08b}"
                bit_labels = "".join([f"{'bit'+str(7-j):>6}" for j in range(8)])
                bit_values = "".join([f"{bit:>6}" for bit in bin_str])
                output.append(f"byte{i}:\n  {bit_labels}\n  {bit_values}")
        output.append(f"--- Total {len(bytes_list)} bytes ---")

    elif align_mode == 'dw_align':
        word_count = (len(bytes_list) + 3) // 4
        for i in range(word_count):
            word_bytes = bytes_list[i*4 : i*4+4]
            while len(word_bytes) < 4:
                word_bytes.append(0)
            word = (word_bytes[3] << 24) | (word_bytes[2] << 16) | (word_bytes[1] << 8) | word_bytes[0]

            if output_format == 'hex':
                output.append(f"dw{i}: 32'h{word:08x}")
            elif output_format == 'dec':
                output.append(f"dw{i}: {word}")
            elif output_format == 'bin':
                bin_str = f"{word:032b}"
                lines = [f"dw{i}:"]
                for row_start in range(0, 32, bits_per_row):
                    row_bits = bin_str[row_start:row_start + bits_per_row]
                    bit_labels = "".join([f"{'b'+str(31 - (row_start + j)):>6}" for j in range(len(row_bits))])
                    bit_values = "".join([f"{bit:>6}" for bit in row_bits])
                    lines.append(f"  {bit_labels}\n  {bit_values}")
                output.extend(lines)
        output.append(f"--- Total {len(bytes_list)} bytes, {word_count} x 32-bit words ---")
    return "\n".join(output)

def extract_bit_range(value, start_bit, end_bit):
    width = abs(end_bit - start_bit) + 1
    mask = (1 << width) - 1
    low = min(start_bit, end_bit)
    extracted = (value >> low) & mask
    return extracted, low, low + width - 1

def print_status(input_mode, output_format, align_mode):
    print("\nCommands:")
    print("  hex / dec / bin          - Switch input mode")
    print("  to_hex / to_bin / to_dec - Switch output format")
    print("  byte_align / dw_align    - Switch alignment mode")
    print("  r<low>-<high>            - Extract bit range from last value")
    print("  <field_name>             - Extract predefined field (if not a reserved word)")
    print("  list                     - Show predefined bit field names")
    print("  q                        - Quit")
    print(f"Current settings: input = {input_mode}, output = {output_format}, alignment = {align_mode}\n")

# ───── CLI Mode ─────
def interactive_loop():
    current_input_mode = 'hex'
    current_output_format = 'hex'
    current_align_mode = 'byte_align'
    last_value = None

    print("Verilog Byte Analyzer (Terminal Mode)")
    print_status(current_input_mode, current_output_format, current_align_mode)

    while True:
        user_input = input("Input or Command: ").strip().lower()

        if user_input == 'q':
            print("Exiting.")
            break
        elif user_input in ['hex', 'dec', 'bin']:
            current_input_mode = user_input
            print(f"Input mode changed to: {current_input_mode}")
            print_status(current_input_mode, current_output_format, current_align_mode)
            continue
        elif user_input in ['to_hex', 'to_bin', 'to_dec']:
            current_output_format = user_input[3:]
            print(f"Output format changed to: {current_output_format}")
            print_status(current_input_mode, current_output_format, current_align_mode)
            continue
        elif user_input in ['byte_align', 'dw_align']:
            current_align_mode = user_input
            print(f"Alignment mode changed to: {current_align_mode}")
            print_status(current_input_mode, current_output_format, current_align_mode)
            continue
        elif user_input == 'list':
            if last_value is not None:
                print("Last parsed value per field:")
                for (low, high), name in BIT_FIELD_MAP.items():
                    extracted, _, _ = extract_bit_range(last_value, low, high)
                    width = abs(high - low) + 1
                    print(f"  {name}: 0b{extracted:0{width}b} (dec = {extracted})")
            else:
                print("Predefined bit fields:")
                for (low, high), name in BIT_FIELD_MAP.items():
                    print(f"  {name}: bit {low}-{high}")
            continue
        elif re.fullmatch(r"r\d+-\d+", user_input):
            m = re.match(r"r(\d+)-(\d+)", user_input)
            start, end = int(m.group(1)), intｓ(m.group(2))
        elif user_input in FIELD_NAME_MAP and user_input not in RESERVED_WORDS:
            start, end = FIELD_NAME_MAP[user_input]
        else:
            value = parse_by_mode(user_input, current_input_mode)
            if value is None:
                print("Invalid input or reserved word.")
                continue
            last_value = value
            bytes_list = convert_to_bytes(value)
            print(f"[Result] Input mode = {current_input_mode}, Output = {current_output_format}, Alignment = {current_align_mode}")
            print(display_bytes(bytes_list, current_output_format, current_align_mode))
            continue

        extracted, low, high = extract_bit_range(last_value, start, end)
        width = high - low + 1
        label = f"bit {low}-{high}"
        if user_input in FIELD_NAME_MAP:
            label += f" [{user_input}]"
        print(f"{label} = 0b{extracted:0{width}b} (dec = {extracted})")

# ───── GUI Mode ─────
def run_gui():
    last_value = {'int': None}

    def on_analyze(event=None):
        input_text = input_entry.get().strip()
        mode = input_mode.get()
        output = output_mode.get()
        align = align_mode.get()
        value = parse_by_mode(input_text, mode)
        if value is None:
            messagebox.showerror("Error", f"Invalid input: '{input_text}' as {mode}")
            return
        last_value['int'] = value
        bytes_list = convert_to_bytes(value)
        result = f"[Result] Input mode = {mode}, Output = {output}, Align = {align}\n\n"
        result += display_bytes(bytes_list, output, align)
        result_box.delete(1.0, tk.END)
        result_box.insert(tk.END, result)

    def on_extract(event=None):
        if last_value['int'] is None:
            messagebox.showwarning("Warning", "No parsed value yet.")
            return
        key = extract_entry.get().strip()

        if re.fullmatch(r"\d+-\d+", key):
            start, end = map(int, key.split("-"))
        elif key in FIELD_NAME_MAP and key not in RESERVED_WORDS:
            start, end = FIELD_NAME_MAP[key]
        else:
            messagebox.showerror("Error", "Enter bit range (e.g., 12-8) or field name (e.g., opcode)")
            return

        extracted, low, high = extract_bit_range(last_value['int'], start, end)
        width = high - low + 1
        label = f"Bit {low}-{high}"
        if key in FIELD_NAME_MAP:
            label += f" [{key}]"
        result_box.insert(tk.END, f"\n{label} = 0b{extracted:0{width}b} (dec = {extracted})\n")

    def on_list():
        result_box.insert(tk.END, "\n")
        if last_value['int'] is not None:
            result_box.insert(tk.END, "Last parsed value per field:\n")
            for (low, high), name in BIT_FIELD_MAP.items():
                extracted, _, _ = extract_bit_range(last_value['int'], low, high)
                width = abs(high - low) + 1
                result_box.insert(tk.END, f"  {name}: 0b{extracted:0{width}b} (dec = {extracted})\n")
        else:
            result_box.insert(tk.END, "Predefined bit fields:\n")
            for (low, high), name in BIT_FIELD_MAP.items():
                result_box.insert(tk.END, f"  {name}: bit {low}-{high}\n")

    root = tk.Tk()
    root.title("Verilog Byte Analyzer")

    frame = ttk.Frame(root, padding=10)
    frame.grid()

    ttk.Label(frame, text="Input Value:").grid(column=0, row=0, sticky="w")
    input_entry = ttk.Entry(frame, width=40)
    input_entry.grid(column=1, row=0, columnspan=2)
    input_entry.bind("<Return>", on_analyze)

    ttk.Label(frame, text="Input Mode:").grid(column=0, row=1, sticky="w")
    input_mode = ttk.Combobox(frame, values=["hex", "dec", "bin"], width=10, state="readonly")
    input_mode.set("hex")
    input_mode.grid(column=1, row=1)

    ttk.Label(frame, text="Output Format:").grid(column=0, row=2, sticky="w")
    output_mode = ttk.Combobox(frame, values=["hex", "dec", "bin"], width=10, state="readonly")
    output_mode.set("bin")
    output_mode.grid(column=1, row=2)

    ttk.Label(frame, text="Align Mode:").grid(column=0, row=3, sticky="w")
    align_mode = ttk.Combobox(frame, values=["byte_align", "dw_align"], width=12, state="readonly")
    align_mode.set("byte_align")
    align_mode.grid(column=1, row=3)

    ttk.Button(frame, text="Analyze", command=on_analyze).grid(column=2, row=1, rowspan=2)

    ttk.Label(frame, text="Bit Range or Field:").grid(column=0, row=4, sticky="w")
    extract_entry = ttk.Entry(frame, width=20)
    extract_entry.grid(column=1, row=4)
    extract_entry.bind("<Return>", on_extract)
    ttk.Button(frame, text="Extract", command=on_extract).grid(column=2, row=4)

    ttk.Button(frame, text="List", command=on_list).grid(column=2, row=5)

    result_box = tk.Text(frame, width=100, height=25, wrap="none")
    result_box.grid(column=0, row=6, columnspan=3, pady=10)

    root.mainloop()

# ───── Entry ─────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-gui", action="store_true", help="Run in GUI mode")
    args = parser.parse_args()

    if args.gui:
        run_gui()
    else:
        interactive_loop()