#!/usr/bin/bash

# Set JAVA_HOME and add Java to PATH
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
export PATH_TO_FX="/usr/lib/jvm/javafx-sdk-17.0.13/lib"
export PATH="$JAVA_HOME/bin:$PATH"

# Set paths for JUnit 5 and JUnit 4
export JUNIT5_PATH="/usr/lib/jvm/junit5"
export JUNIT4_PATH="/usr/lib/jvm/junit4"

# Add JUnit paths to CLASSPATH
export CLASSPATH="$JUNIT5_PATH/junit-jupiter-api-5.11.3.jar:\
$JUNIT5_PATH/junit-jupiter-engine-5.11.3.jar:\
$JUNIT5_PATH/junit-jupiter-params-5.11.3.jar:\
$JUNIT4_PATH/junit-4.13.2.jar"

cd ..

RootModule="practice"

javac --module-path $PATH_TO_FX:$JUNIT4_PATH \
	--add-modules javafx.base,javafx.controls,javafx.graphics \
	-d out $(find src -name "*.java")

java --module-path $PATH_TO_FX:out \
	--add-modules javafx.base,javafx.controls,javafx.graphics \
	-cp $JUNIT4_PATH \
	-m $RootModule/comp303.music.Song
