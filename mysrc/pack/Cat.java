// utils/Helper.java
package pack;

public class Cat {
	private String aName;

	public void sayName() {
		System.out.printf("I'm a Cat (%s), Meaow", aName);
	}

	public Cat(String pName) {
		aName = pName;
	}

}
