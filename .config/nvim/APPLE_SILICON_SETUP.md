# Apple Silicon (ARM64) Setup for nvim-treesitter

## Problem
On Apple Silicon Macs (M1/M2/M3), Mason may install the x86_64 version of `tree-sitter-cli`, which causes nvim-treesitter to compile parsers for the wrong architecture. This results in "no test found" errors in neotest because the parsers fail to load.

## Solution
The configuration has been updated to automatically handle ARM64 compilation:

### 1. Removed tree-sitter-cli from Mason
**File**: `.config/nvim/lua/plugins/mason-tool-installer.lua`

The `tree-sitter-cli` has been removed from Mason's `ensure_installed` list because Mason installs the x86_64 version on some setups, which causes architecture incompatibility issues.

### 2. Updated nvim-treesitter Configuration  
**File**: `.config/nvim/lua/plugins/nvim-treesitter.lua`

The nvim-treesitter plugin now:
- Detects if running on Apple Silicon
- Sets `CFLAGS="-arch arm64"` to force ARM64 compilation
- Sets `prefer_git = true` to use git clones instead of the tree-sitter CLI
- Applies these settings in both the `build` and `config` functions

This ensures that all tree-sitter parsers are compiled for the correct architecture automatically.

## Fresh Install Instructions

When setting up on a new Apple Silicon Mac:

1. Clone and install your dot configuration as normal:
   ```bash
   cd ~/src/dusktreader
   git clone https://github.com/dusktreader/dot.git
   cd dot
   ./install.sh
   ```

2. The nvim configuration will automatically:
   - Install all plugins via Lazy.nvim
   - Detect ARM64 architecture
   - Compile all treesitter parsers for ARM64
   - Skip installing x86_64 tree-sitter-cli from Mason

3. **First time opening nvim**:
   - You may see parsers being compiled on first launch
   - This is normal - let it complete
   - After all installations finish, restart nvim: `:qa` then reopen

4. **Verification**:
   ```bash
   ~/.config/nvim/verify-neotest-go.sh
   ```
   
   This script checks:
   - Go parser exists and is ARM64
   - Parser loads correctly in neovim
   - neotest-golang is version 2.7.1+

## Troubleshooting

If you still get "no test found" errors after setup:

1. **Check parser architecture**:
   ```bash
   file ~/.local/share/nvim/lazy/nvim-treesitter/parser/go.so
   ```
   Should show: `Mach-O 64-bit dynamically linked shared library arm64`

2. **If parser is x86_64**, manually recompile:
   ```bash
   # Remove wrong-architecture parser
   rm ~/.local/share/nvim/lazy/nvim-treesitter/parser/go.so
   
   # Reinstall with forced ARM64
   nvim --headless -c "TSInstall! go" -c "qa"
   ```

3. **If tree-sitter CLI got installed by Mason**:
   ```bash
   # Check if it exists and is x86_64
   file ~/.local/share/nvim/mason/bin/tree-sitter
   
   # If x86_64, remove it
   rm ~/.local/share/nvim/mason/bin/tree-sitter
   
   # Reinstall parsers
   nvim --headless -c "TSUpdate" -c "qa"
   ```

4. **Always restart neovim** after any parser changes:
   - Don't just reload config
   - Fully quit (`:qa`) and reopen

## Technical Details

### Why This Happens
- Neovim and nvim-treesitter support ARM64 natively
- However, Mason (the tool installer) sometimes installs x86_64 binaries
- When tree-sitter-cli is x86_64, it compiles parsers as x86_64
- ARM64 neovim cannot load x86_64 shared libraries
- Result: "Go tree-sitter parser not found" errors

### The Fix
By setting `CFLAGS="-arch arm64"` and `prefer_git = true`:
- nvim-treesitter clones parser sources via git
- Compiles them directly using the system compiler
- The system compiler respects CFLAGS and builds ARM64
- No dependency on the tree-sitter CLI
- Parsers match neovim's architecture

### Parser Locations
Neovim 0.11+ may use either location:
- `~/.local/share/nvim/lazy/nvim-treesitter/parser/` (preferred)
- `~/.local/share/nvim/site/parser/` (fallback)

The nvim-treesitter plugin manages these automatically.

## See Also
- Full troubleshooting guide: `~/.config/nvim/neotest-fixes.md`
- Verification script: `~/.config/nvim/verify-neotest-go.sh`
