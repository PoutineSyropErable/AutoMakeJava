The .project and .classpath are needed, for you own projects.
Then after that, put java files inside src and just to python automake.py "path to file"

You also need to pip install javalang and numpy. Preferably in a python venv so you don't fuck your machine

```bash
pip install javalang numpy
```

# How to create venv

For those of you who don't know python venv use something that's not goated like arch, maybe pip will cause version problems.
So, if you see any weird C/C++/other language library error, like .so or .dll error when you use it, its cause your shit is too old.
Don't change your system python, it might break your machine, and worst case scenario, bye bye.

_YOU'LL NEED A PYTHON PIP OR CONDA VIRTUAL VENV_

Anyway, in that case, you need a pip venv, so i recommend:
(For zshrc, should work in bashrc and fishrc, but at this point, just figure it out)
I mean, like just copy paste to chatgpt 4.0 and ask for a translation to your shell, and in case, say that your is using a
dinosaur old version, so no new fancy shit

```bash
# ─────────────────────────────────────────────────────
# 🚀 3️⃣ Python Virtual Environments
# ─────────────────────────────────────────────────────

# Define the base directory for Python virtual environments (from pip)
export PYTHON_VENV_DIR="$HOME/MainPython_Virtual_Environment"
# You can change this path, It's bad, but I'm stuck with it.
# It was for when i only had one


pip_create() {
    if [[ -z "$1" ]]; then
        echo "❌ Usage: pip_create <venv_name>"
        return 1
    fi
    VENV_PATH="$PYTHON_VENV_DIR/$1"
    if [[ -d "$VENV_PATH" ]]; then
        echo "⚠️ Virtual environment '$1' already exists at $VENV_PATH"
    else
        python -m venv "$VENV_PATH"
        echo "✅ Virtual environment '$1' created at $VENV_PATH"
    fi
}

pip_activate() {
    if [[ -z "$1" ]]; then
        echo "❌ Usage: pip_activate <venv_name>"
        return 1
    fi
    VENV_PATH="$PYTHON_VENV_DIR/$1"
    if [[ -d "$VENV_PATH" ]]; then
        source "$VENV_PATH/bin/activate"
        echo "✅ Activated virtual environment: $1"
    else
        echo "❌ Virtual environment '$1' does not exist in $PYTHON_VENV_DIR"
    fi
}

# Use a venv's Python without activating it
alias pythonvenv="$PYTHON_VENV_DIR/pip_venv/bin/python"
alias pv="pythonvenv"

# Activate common virtual environments
alias govenv="pip_activate pip_venv"
alias projvenv="pip_activate project_venv"

# Deactivate the current virtual environment
alias lvenv="deactivate"

```

# Shell Setup for automake java cli easy calling

Add this to your shell rc so you can run it manually:

```bash
# Define paths
AutoMakeJava_Path="${HOME}/Documents/University (Real)/Semester 10/Comp 303/AutomakeJava"
PYTHON_VENV_DIR="$HOME/MainPython_Virtual_Environment"

# Path to Python executable inside the virtual environment
pythonFor_AutoMakeJava="$PYTHON_VENV_DIR/javaAM/bin/python"


# Unset alias if it exists (to avoid conflicts)
unalias automakeJava 2>/dev/null

# Function to run automake.py using the correct Python environment
automakeJava() {
	"$pythonFor_AutoMakeJava" "${AutoMakeJava_Path}/mysrc/automake.py" "$@"
}


# Alias to call the function
alias java_run="automakeJava"
# You can then do automakeJava java_file.java
# java_run java_file.java

```

# Neovim example for calling it on current file with <F4>

lua example for neovim:

```lua

-- keymaps.lua, sourced from init.lua
function RunCurrentFile()
	local filepath = vim.api.nvim_buf_get_name(0) -- Get the full file path
	local file_ext = vim.fn.fnamemodify(filepath, ":e") -- Get the file extension

	if file_ext == "sh" then
		-- Run Bash script
		vim.cmd("!bash " .. vim.fn.shellescape(filepath))
	elseif file_ext == "c" then
		-- Compile and run C file
		local executable = vim.fn.shellescape(filepath:gsub("%.c$", ""))
		vim.cmd("!gcc " .. vim.fn.shellescape(filepath) .. " -o " .. executable .. " && " .. executable)
	elseif file_ext == "cpp" then
		-- Compile and run C file
		local executable = vim.fn.shellescape(filepath:gsub("%.cpp$", ""))
		vim.cmd("!g++ " .. vim.fn.shellescape(filepath) .. " -o " .. executable .. " && " .. executable)
	elseif file_ext == "py" then
		-- Run Python script
		vim.cmd("!python3 " .. vim.fn.shellescape(filepath))
    ------------------------------------ THIS ------------------------------------------------------------
	elseif file_ext == "java" then
		local home = vim.fn.expand("$HOME")
		local AutoMakeJava_location = "/Documents/University (Real)/Semester 10/Comp 303/AutomakeJava"
		local autoMakeScript = home .. AutoMakeJava_location .. "/src/automake.py"
        -- For /home/me/Documents/... Change the automakejava location for
        -- where you downloaded my shit
		vim.cmd("!python3 " .. vim.fn.shellescape(autoMakeScript) .. " " .. vim.fn.shellescape(filepath))
        -- Note that this will need you to have activated the venv with javalang and numpy
        -- before entering neovim. (And if its installed on your default python,
        -- such a thing wont be a problem)
    ------------------------------------ THIS ------------------------------------------------------------
	else
		print("File type not supported for running with F4")
	end
end

local keymap = vim.keymap -- too lazy to say vim.keymap every single time
-- makes keymap seting easier
local function opts(desc) return { noremap = true, silent = true, desc = desc } end

keymap.set("n", "<F4>", RunCurrentFile, opts("Run current file"))


```

# Usage

I think it works now, maybe some day, I'll add other stuff for it, like not compiling if the .class is not older then .java like for make command

then just

```bash
pip_create javaAM
pip_activate javaAM
pip install numpy javalang
nvim Javafile.java
<Press F4>

# For CLI, (Example, you want to read user input, which doesn't work inside neovim)
#  go to ./myrc/JavaSrc, and do
automakeJava MainFile.java

```
