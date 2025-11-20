import java.util.Scanner;

public class consistency {

    // 3 replicas each with variable x
    static class Replica {
        int x = 0;
    }

    static Replica[] replicas = { new Replica(), new Replica(), new Replica() };

    static void show(String title) {
        System.out.println("\n" + title);
        for (int i = 0; i < replicas.length; i++) {
            System.out.println("  Replica " + i + ": x = " + replicas[i].x);
        }
        System.out.println("-------------------------------");
    }

    // Eventual consistency: write locally, propagate after delay
    static void eventual(int value, int delayMs) {
        replicas[0].x = value;
        show("After local write on replica 0 (others stale)");

        System.out.println("Simulating delay: sleeping " + delayMs + " ms...");
        try {
            Thread.sleep(delayMs);
        } catch (Exception e) {
        }

        for (int i = 1; i < replicas.length; i++) {
            replicas[i].x = replicas[0].x;
        }
        show("After propagation (eventual consistency)");
    }

    // Strong consistency: update all replicas immediately
    static void strong(int value) {
        for (Replica r : replicas) {
            r.x = value;
        }
        show("After synchronous update (strong consistency)");
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        show("Initial state (all replicas identical)");

        System.out.print("Mode (eventual/strong): ");
        String mode = sc.next().trim().toLowerCase();

        System.out.print("Value to write (integer): ");
        int value = sc.nextInt();

        if (mode.equals("eventual")) {
            System.out.print("Propagation delay in ms: ");
            int delay = sc.nextInt();
            eventual(value, delay);
        } else if (mode.equals("strong")) {
            strong(value);
        } else {
            System.out.println("Unknown mode.");
        }

        sc.close();
    }
}
