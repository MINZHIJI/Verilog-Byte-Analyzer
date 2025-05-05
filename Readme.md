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

---

## 🖥️ CLI Mode

```bash
python analyzer.py

### Available Commands: