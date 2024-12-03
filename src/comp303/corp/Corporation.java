package comp303.corp;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

/**
 * Represents a company that owns and operates one or more grocery stores, each with its own inventory.
 */
public class Corporation implements Iterable<Inventory>
{
	private Map<String, Inventory> aInventories = new HashMap<String, Inventory>();

	/**
	 * @param pInventory
	 *            An inventory to add to the corporation.
	 */
	public void addInventory(Inventory pInventory)
	{
		aInventories.put(pInventory.getName(), pInventory);
	}

	@Override
	public Iterator<Inventory> iterator()
	{
		return aInventories.values().iterator();
	}

	@Override
	public String toString()
	{
		StringBuilder sb = new StringBuilder();
		sb.append("Corporation with Inventories:\n");
		for (Inventory inventory : aInventories.values())
		{
			sb.append(" - ").append(inventory.getName()).append(":\n");
			for (Item item : inventory)
			{ // Assuming Inventory implements Iterable<Item>
				sb.append("   - ").append(item.getName()).append(" (ID: ").append(item.getId()).append(", Price: ")
						.append(item.getPrice()).append(" cents)\n");
			}
		}
		return sb.toString();
	}

}
