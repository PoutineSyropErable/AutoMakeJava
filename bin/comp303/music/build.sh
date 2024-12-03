#!/bin/bash
printf "\n"
# notify-send "being called"


# Set JAVA_HOME and add Java to PATH
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
export PATH_TO_FX="/usr/lib/jvm/javafx-sdk-17.0.13/lib"
export PATH="$JAVA_HOME/bin:$PATH"

# Set paths for JUnit 5 and JUnit 4
export JUNIT4_PATH="/usr/lib/jvm/junit4"
export JUNIT4_JAR="$JUNIT4_PATH/junit-4.13.2.jar"
export HAMCREST_JAR="$JUNIT4_PATH/hamcrest-core-1.3.jar"
export CLASSPATH="$JUNIT4_JAR:$HAMCREST_JAR"

export JUNIT5_PATH="/usr/lib/jvm/junit5"

# Add JUnit paths to CLASSPATH // WE DO NOT USE JUNIT5 FOR NOW BUT IT IS THERE
export CLASSPATH_5="$JUNIT5_PATH/junit-jupiter-api-5.11.3.jar:\
$JUNIT5_PATH/junit-jupiter-engine-5.11.3.jar:\
$JUNIT5_PATH/junit-jupiter-params-5.11.3.jar:\
$JUNIT4_PATH/junit-4.13.2.jar"

#--------------------------------------------GO TO CORRECT DIRECTORY---------------------------
SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
# SCRIPT_DIR=$(realpath $SCRIPT_DIR)
printf "script path: $SCRIPT_PATH\n"
printf "script dir: $SCRIPT_DIR\n"

cd "$SCRIPT_DIR" || {
	echo "Can't CD to Script Dir"
	exit 66
}

printf "Currently in $(pwd)\n"

# If executed the one in ./build_script, it cd back to the project root
if [[ ! -d "src" ]]; then
	echo "cd-ing backward"
	cd ..
	printf "Currently in $(pwd)\n"
fi
printf "\n"

#--------------------------------------GETTING THE FILE----------------------------------------------

#^ The file we wish to compile (if given no argument) dirname.filename (Since we are only 2 directory deep)
DEFAULT_MODULE_TO_EXECUTE="demo.Welcome"

# Check if argument $1 is provided
if [[ -n "$1" ]]; then
	# Extract directory and filename components
	ABSOLUTE_PATH=$(realpath "$1")
	printf "input path: $1\n"
	echo "Absolute path: $ABSOLUTE_PATH"

	DIRNAME_PATH=$(dirname "$ABSOLUTE_PATH") # Remove "src/" prefix
	DIRNAME=$(basename "$DIRNAME_PATH")
	FILENAME=$(basename "$1" .java) # Strip .java extension
	echo "dirname_path: $DIRNAME_PATH"
	echo "dirname: $DIRNAME"
	printf "filename: $FILENAME\n\n"

	MODULE_TO_EXECUTE="$DIRNAME.$FILENAME" # Convert path to module notation
	printf "using $MODULE_TO_EXECUTE\n\n"

else
	# Use default module if no file is specified
	MODULE_TO_EXECUTE="$DEFAULT_MODULE_TO_EXECUTE"
	printf "No file specified. Using default module: $DEFAULT_MODULE_TO_EXECUTE\n\n"
fi
#-------------------------------------------------------------------------------------

#-------------------------------------COMPILING & OPTIONS----------------------------
# Variables for paths and modules
OUTPUT_DIR="out" # The output directory for compiled files
SRC_DIR="src"    # The source directory
ROOT_MODULE="practice"
ALL_JAVA_FILES=$(find "$SRC_DIR" -name "*.java")       # All .java files in the source directory
ALL_OUTPUT_FILES=$(find "$OUTPUT_DIR" -name "*.class") # All .java files in the source directory
MAIN_MODULE="$ROOT_MODULE/comp303.$MODULE_TO_EXECUTE"  # Main module to run

removeOutputFiles() {
	echo "Removing specific output files in $OUTPUT_DIR..."
	echo "Here is the list of files to remove"
	echo "$ALL_OUTPUT_FILES"

	# Ensure $OUTPUT_DIR exists to avoid errors
	if [[ -d "$OUTPUT_DIR" ]]; then
		# Specify patterns for files to delete
		find "$OUTPUT_DIR" -type f -name "*.class" -exec rm {} +
		find "$OUTPUT_DIR" -type f -name "*.jar" -exec rm {} +
		# Add additional file patterns as needed
	else
		echo "Output directory $OUTPUT_DIR does not exist."
	fi

	echo "Cleanup complete."
}

#You can comment this line, it's not needed
removeOutputFiles

# Recompile all Java files (Overkill, but let's not recreate a makefile from scratch for java)
javac --module-path "$PATH_TO_FX:$JUNIT4_PATH" \
	--add-modules "javafx.base,javafx.controls,javafx.graphics" \
	-d "$OUTPUT_DIR" $ALL_JAVA_FILES

#-----------------------------------EXECUTING THE FILE--------------------------------
printf -- "\nMAIN_MODULE:($MAIN_MODULE) \n\n"
printf -- "\n\n-------------------------START OF PROGRAM-----------------------------\n\n"

java --module-path "$PATH_TO_FX:$OUTPUT_DIR" \
	--add-modules "javafx.base,javafx.controls,javafx.graphics" \
	-cp "$CLASSPATH" \
	-m "$MAIN_MODULE"
