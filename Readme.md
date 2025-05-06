# Verilog Byte Analyzer

A lightweight and interactive Python tool for analyzing Verilog-style values in binary, hex, or decimal form.  
Supports both command-line and GUI modes for debugging, bit-range extraction, and aligned byte/word visualization.

---

## 🔧 Features

- 🖥️ **CLI mode** and 🪟 **GUI mode** (Tkinter)
- 🔢 Input support: `8'hFF`, `'b1010_0011`, `1234` (hex, bin, dec)
- 📤 Output formats: hex / dec / binary with aligned layout
- 📐 Alignment options:
  - `byte_align`: View each byte and its bit positions
  - `dw_align`: View 32-bit words with optional grouping
- 🧠 Bit range extraction: Use `r<low>-<high>` to extract fields
- ⌨️ GUI: Press `Enter` to analyze or extract bits
- 🧩 Dropdowns are fixed (single-choice) to avoid invalid entries
- 📥 Import custom bit field maps using JSONC files (CLI: `-f <file>`, GUI: “Load FieldMap”)
- 🆚 Compare mode: Input two values (CLI or GUI) to visualize bitwise and field-level differences

---

## 🖥️ CLI Mode

```bash
python analyzer.py
```

### Available Commands:

```
hex / dec / bin          - Switch input mode  
to_hex / to_bin / to_dec - Switch output format  
byte_align / dw_align    - Switch alignment mode  
r<low>-<high>            - Extract bit range from last input  
<field_name>             - Extract predefined field (e.g. opcode)  
list                     - Show predefined bit fields and last parsed values  
<val1> <val2>              - Enter two values in sequence to compare field differences
q                        - Quit
```

### 🧪 Example: Compare Mode

```bash
# Compare two hex values and view bit differences
python analyzer.py
> 0x1234 0x1274
```
Output:
```
[Compare Mode] Value 1 vs Value 2
  Value 1: 4660 (0x1234)
  Value 2: 4724 (0x1274)
  flag        : 3 -> 7
----------------------------------------
[Result] Input mode = hex, Output = bin, Alignment = dw_align
...
```

## 🪟 GUI Mode

```bash
python analyzer.py
```

⚠️ GUI mode requires Python's `tkinter` module. If not installed, the program will fall back to CLI mode with a warning.

- Use input field to enter Verilog-style values
- Dropdowns for input mode, output format, and alignment
- Use “Analyze” or press Enter to parse
- Use “Extract” or press Enter to extract a specific bit range (e.g. 15-8)
- Results shown below with proper bit position labeling
- Use “Load FieldMap” to import JSONC file defining bit field names