import java.util.*;

class Server {
    int id;
    boolean isLeader = false;
    boolean alive = true;
    int clock = 0;
    int balance = 1000;

    Server(int id) {
        this.id = id;
    }

    void incrementClock() {
        clock++;
    }

    void receiveMessage(int ts) {
        clock = Math.max(clock, ts) + 1;
    }

    void crash() {
        alive = false;
        isLeader = false;
    }

    void recover() {
        alive = true;
    }
}

public class BankSystem {

    static Server electLeader(List<Server> servers) {
        Server leader = null;
        for (Server s : servers) {
            if (s.alive) {
                if (leader == null || s.id > leader.id)
                    leader = s;
            }
        }
        leader.isLeader = true;
        System.out.println("Leader Elected → Server " + leader.id);
        return leader;
    }

    static void performTransaction(List<Server> servers, int amount) {
        Server leader = null;
        for (Server s : servers) {
            if (s.alive) {
                if (leader == null || s.id > leader.id)
                    leader = s;
            }
        }
        if (leader == null || !leader.alive) {
            System.out.println("No leader available! Elect a leader first.");
            return;
        }

        leader.incrementClock();
        int ts = leader.clock;

        leader.balance += amount;
        System.out.println("Transaction: " + (amount >= 0 ? "Deposit " : "Withdraw ")
                + Math.abs(amount) + " | TS = " + ts);

        for (Server s : servers) {
            if (s != leader && s.alive) {
                s.receiveMessage(ts);
                s.balance = leader.balance;
            }
        }
    }

    static void showStatus(List<Server> servers) {
        System.out.println("\n--- Server Status ---");
        for (Server s : servers) {
            System.out.println("Server " + s.id +
                    " | Alive=" + s.alive +
                    " | Leader=" + s.isLeader +
                    " | Balance=" + s.balance +
                    " | Clock=" + s.clock);
        }
        System.out.println("---------------------\n");
    }

    public static void main(String[] args) {

        Scanner sc = new Scanner(System.in);

        List<Server> servers = Arrays.asList(
                new Server(1),
                new Server(2),
                new Server(3),
                new Server(4),
                new Server(5));

        Server leader = electLeader(servers);

        int choice;

        while (true) {

            System.out.println("==== Distributed Banking System ====");
            System.out.println("1. Perform Deposit");
            System.out.println("2. Perform Withdraw");
            System.out.println("3. Crash Leader");
            System.out.println("4. Recover a Server");
            System.out.println("5. Elect New Leader");
            System.out.println("6. Show Server Status");
            System.out.println("7. Exit");
            System.out.print("Enter choice: ");

            choice = sc.nextInt();

            switch (choice) {

                case 1:
                    System.out.print("Enter amount to deposit: ");
                    int d = sc.nextInt();
                    performTransaction(servers, d);
                    break;

                case 2:
                    System.out.print("Enter amount to withdraw: ");
                    int w = sc.nextInt();
                    performTransaction(servers, -w);
                    break;

                case 3:
                    if (leader != null) {
                        System.out.println("Leader Crashed → Server " + leader.id);
                        leader.crash();
                    }
                    break;

                case 4:
                    System.out.print("Enter server ID to recover: ");
                    int rid = sc.nextInt();
                    if (rid >= 1 && rid <= 5) {
                        servers.get(rid - 1).recover();
                        System.out.println("Server " + rid + " recovered.");
                    }
                    break;

                case 5:
                    leader = electLeader(servers);
                    break;

                case 6:
                    showStatus(servers);
                    break;

                case 7:
                    System.out.println("Exiting...");
                    return;

                default:
                    System.out.println("Invalid choice.");
            }
        }
    }
}
