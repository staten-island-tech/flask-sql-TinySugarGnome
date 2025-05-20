import java.util.Timer;
import java.util.TimerTask;
import java.util.Random;

public class MultiplierManager {

    private static final Random random = new Random();
    private static int multiplier = 1;
    private static long multiplierExpires = 0;

    public static void main(String[] args) {
        // Create a timer to run every second
        Timer timer = new Timer();
        timer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                checkForMultiplier();
            }
        }, 0, 1000);  // Run every 1000ms (1 second)
    }

    public static void checkForMultiplier() {
        // Check if multiplier is expired
        if (System.currentTimeMillis() > multiplierExpires) {
            multiplier = 1; // Reset multiplier when expired
        }

        // Random chance for x2 multiplier (1/100 chance)
        if (random.nextInt(100) == 0 && multiplier == 1) {
            // Activate x2 multiplier for 30 seconds
            multiplier = 2;
            multiplierExpires = System.currentTimeMillis() + 30000;  // 30 seconds from now
            System.out.println("2");  // Output multiplier to be used by Flask
            System.out.println(multiplierExpires);  // Output expiration time
        }

        // Random chance for x10 multiplier (1/500 chance)
        if (random.nextInt(500) == 0 && multiplier == 1) {
            // Activate x10 multiplier for 20 seconds
            multiplier = 10;
            multiplierExpires = System.currentTimeMillis() + 20000;  // 20 seconds from now
            System.out.println("10");  // Output multiplier to be used by Flask
            System.out.println(multiplierExpires);  // Output expiration time
        }
    }

    public static int getMultiplier() {
        return multiplier;
    }

    public static long getMultiplierExpires() {
        return multiplierExpires;
    }
}
