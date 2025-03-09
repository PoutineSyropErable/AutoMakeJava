
// MainFile.java
import utils.Helper;
import pack.*;

public class MainFile {
	public static void main(String[] args) {
		Helper.sayHello();
		int result = Helper.multiply(4, 5);
		System.out.println("Result: " + result);

		Dog.bark();

	}

}
