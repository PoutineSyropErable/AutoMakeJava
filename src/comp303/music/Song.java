package comp303.music;

/**
 * Represents an audio file and its meta-data.
 */
public class Song
{
	@SuppressWarnings("unused")
	private String aName;
	@SuppressWarnings("unused")
	private AudioFormat aFormat;
	@SuppressWarnings("unused")
	private int aBpm;
	@SuppressWarnings("unused")
	private Genre aGenre;

	public Song()
	{

		aName = "Thunderstruck";
		aFormat = AudioFormat.MP3;
		aBpm = 1000;
		aGenre = Genre.ROCK;

	}

	public static void main(String[] args)
	{

		Song mySong = new Song();
		System.out.println("\nIT works!\n");
		System.out.println(mySong);
		System.out.println("\n");

	}
}
