#!/usr/bin/bash

# Set JAVA_HOME and add Java to PATH
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
export PATH_TO_FX="/usr/lib/jvm/javafx-sdk-17.0.13/lib"
export PATH="$JAVA_HOME/bin:$PATH"

# Set paths for JUnit 4
export JUNIT4_PATH="/usr/lib/jvm/junit4"
export JUNIT4_JAR="$JUNIT4_PATH/junit-4.13.2.jar"
export HAMCREST_JAR="$JUNIT4_PATH/hamcrest-core-1.3.jar"

# Add JUnit paths to CLASSPATH
# Add Hamcrest to CLASSPATH
export CLASSPATH="$JUNIT4_JAR:$HAMCREST_JAR"

printf "\nJavaFX:\n"
ls $PATH_TO_FX
printf "\n\nJUnit:\n"
ls $JUNIT4_PATH
printf "\n\nJava Home:\n"
ls $JAVA_HOME
printf "\n\n"

cd ..

# Compile all Java files
javac --module-path "$PATH_TO_FX:$JUNIT4_PATH" \
	--add-modules javafx.base,javafx.controls,javafx.graphics \
	-d out $(find src -name "*.java")

# Run the JUnit test
java -cp "out:$CLASSPATH" org.junit.runner.JUnitCore comp303.demo.TestAlternatingLabelProvider
