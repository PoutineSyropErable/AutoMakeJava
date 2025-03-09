// utils/Helper.java
package utils;

import pack.Cat;

public class Helper {
	public static void sayHello() {
		System.out.println("Hello from Helper!");

		Cat cat = new Cat("Kitty");
		cat.sayName();
	}

	public static int multiply(int a, int b) {
		return a * b;
	}
}
