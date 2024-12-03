#!/usr/bin/bash

# Set JAVA_HOME and add Java to PATH
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
export PATH_TO_FX="/usr/lib/jvm/javafx-sdk-17.0.13/lib"
export PATH="$JAVA_HOME/bin:$PATH"

# Set paths for JUnit 4
export JUNIT4_PATH="/usr/lib/jvm/junit4"
export JUNIT4_JAR="$JUNIT4_PATH/junit-4.13.2.jar"
export HAMCREST_JAR="$JUNIT4_PATH/hamcrest-core-1.3.jar"

# Add JUnit and Hamcrest to CLASSPATH
export CLASSPATH="$JUNIT4_JAR:$HAMCREST_JAR"

# Display paths
printf "\nJavaFX:\n"
ls "$PATH_TO_FX"
printf "\n\nJUnit:\n"
ls "$JUNIT4_PATH"
printf "\n\nJava Home:\n"
ls "$JAVA_HOME"
printf "\n\n"

# Navigate to project root if executed from a subdirectory
cd "$(dirname "$(realpath "$0")")/.." || exit 1

# Check if the first argument ($1) is provided
if [[ -n "$1" ]]; then
	# Get absolute path, remove "src/" prefix, and derive package/class notation
	ABSOLUTE_PATH=$(realpath "$1")
	printf "Input path: %s\n" "$1"
	echo "Absolute path: $ABSOLUTE_PATH"

	# Extract `src` directory to start the package path correctly
	PACKAGE_PATH=$(echo "$ABSOLUTE_PATH" | sed -e 's/.*\/src\///' -e 's/\.java$//')
	TEST_CLASS=$(echo "$PACKAGE_PATH" | tr '/' '.') # Convert path to package.className notation
	printf "Testing class: %s\n\n" "$TEST_CLASS"
else
	echo "No file specified. Please provide the path to the Java file to be tested."
	exit 1
fi

# Compile all Java files
javac --module-path "$PATH_TO_FX:$JUNIT4_PATH" \
	--add-modules javafx.base,javafx.controls,javafx.graphics \
	-d out $(find src -name "*.java")

# Run the JUnit test using the full package.class notation
printf -- "\n\n-------------------------START OF TEST-----------------------------\n\n"
java -cp "out:$CLASSPATH" org.junit.runner.JUnitCore "$TEST_CLASS"
