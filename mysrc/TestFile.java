// TestFile.java
public class TestFile {
	public static void main(String[] args) {
		greet();
		int result = add(5, 3);
		System.out.println("Result: " + result);
	}

	public static void greet() {
		System.out.println("Hello, World!");
	}

	public static int add(int a, int b) {
		return a + b;
	}
}
