import java.util.Timer;
import java.util.TimerTask;
import java.util.Random;
import java.util.HashMap;
import java.util.Map;

public class MultiplierManager {

    private static final Random random = new Random();
    private static final Map<Integer, Integer> userMultipliers = new HashMap<>();
    private static final Map<Integer, Long> multiplierExpires = new HashMap<>();

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

    // Check multipliers for all users and reset if expired
    public static void checkForMultiplier() {
        long currentTime = System.currentTimeMillis();
        // For each user, check if their multiplier should expire and/or be updated
        for (Integer userId : userMultipliers.keySet()) {
            // Check if multiplier is expired for the user
            if (multiplierExpires.get(userId) < currentTime) {
                // Reset multiplier to 1 if expired
                userMultipliers.put(userId, 1);  // Reset multiplier to 1
                multiplierExpires.put(userId, 0L);  // Clear expiration time
                System.out.println("User " + userId + "'s multiplier expired and was reset.");
            }
        }

        // Random chance for multipliers (per user)
        // Example: 1% chance to give a random multiplier for a user every second
        for (Integer userId : userMultipliers.keySet()) {
            if (random.nextInt(1) == 0) {
                // Give user a x2 multiplier for 30 seconds
                userMultipliers.put(userId, 2);
                multiplierExpires.put(userId, currentTime + 30000);  // Expire in 30 seconds
                System.out.println("User " + userId + " gets x2 multiplier for 30 seconds!");
            }

            if (random.nextInt(5) == 0) {
                // Give user a x10 multiplier for 20 seconds
                userMultipliers.put(userId, 10);
                multiplierExpires.put(userId, currentTime + 20000);  // Expire in 20 seconds
                System.out.println("User " + userId + " gets x10 multiplier for 20 seconds!");
            }
        }
    }

    // Function to add a new user with default multiplier
    public static void addUser(int userId) {
        // Initialize user with a multiplier of 1
        userMultipliers.put(userId, 1);
        multiplierExpires.put(userId, 0L);  // No expiration initially
        System.out.println("User " + userId + " added with default x1 multiplier.");
    }

    // Function to get multiplier for a specific user
    public static int getUserMultiplier(int userId) {
        return userMultipliers.getOrDefault(userId, 1);  // Default to x1 if no multiplier
    }

    // Function to get expiration time for a specific user's multiplier
    public static long getUserMultiplierExpires(int userId) {
        return multiplierExpires.getOrDefault(userId, 0L);
    }
    
    // Function to remove a user
    public static void removeUser(int userId) {
        userMultipliers.remove(userId);
        multiplierExpires.remove(userId);
        System.out.println("User " + userId + " has been removed.");
    }
}
