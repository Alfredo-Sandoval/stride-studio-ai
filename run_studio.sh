#!/bin/bash
# ---------------------------------------------------------------------------
#  run_studio.sh – launch Stride Studio on Linux/macOS
# ---------------------------------------------------------------------------

# 1. Activate Conda environment (edit name if needed)
echo "Attempting to activate Conda environment \"Stride_Studio\"..."
# Source conda.sh if conda command is not found directly
if ! command -v conda &> /dev/null; then
    echo "Conda command not found directly. Trying to source conda.sh..."
    # Try standard Miniconda/Anaconda paths - adjust if your install differs
    CONDA_BASE=$(conda info --base 2>/dev/null) || CONDA_BASE="$HOME/miniconda3" || CONDA_BASE="$HOME/anaconda3"
    if [ -f "$CONDA_BASE/etc/profile.d/conda.sh" ]; then
        source "$CONDA_BASE/etc/profile.d/conda.sh"
        echo "Sourced conda.sh from $CONDA_BASE"
    else
        echo "ERROR: Could not find conda.sh to initialize Conda. Please ensure Conda is initialized in your shell."
        exit 1
    fi
fi

conda activate Stride_Studio
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate environment \"Stride_Studio\"."
    echo "Please ensure the environment exists and Conda is configured correctly."
    exit 1
fi

# 2. Start the GUI (package entry-point)
#    Change directory to the script's location first
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR" || exit 1 # Exit if cd fails

echo "Starting Stride Studio from $SCRIPT_DIR..."
python -m stride_studio "$@" # Pass all script arguments to python

# 3. Done
echo ""
echo "Application finished."

exit 0
