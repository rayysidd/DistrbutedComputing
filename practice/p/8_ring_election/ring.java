import java.util.*;

class Node {
    int pid;
    boolean alive = true;
    int coordinator = -1;

    Node(int pid) {
        this.pid = pid;
    }
}

public class ring {

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("Enter number of nodes: ");
        int n = sc.nextInt();

        // Initialize nodes with PIDs 1..n
        List<Node> nodes = new ArrayList<>();
        for (int i = 1; i <= n; i++) {
            nodes.add(new Node(i));
        }

        // Simulate election loop
        while (true) {
            System.out.println("\nEnter command: 1=fail node, 2=start election, 3=print coordinator, 0=exit");
            int cmd = sc.nextInt();

            switch (cmd) {
                case 1: // Fail a node
                    System.out.print("Enter PID to fail: ");
                    int failPid = sc.nextInt();
                    for (Node node : nodes) {
                        if (node.pid == failPid) {
                            node.alive = false;
                            System.out.println("Node " + failPid + " failed.");
                        }
                    }
                    break;

                case 2: // Start election from a node
                    System.out.print("Enter PID to start election: ");
                    int startPid = sc.nextInt();
                    startElection(nodes, startPid);
                    break;

                case 3: // Print current coordinator
                    int coord = -1;
                    for (Node node : nodes) {
                        if (node.alive) {
                            coord = node.coordinator;
                            break;
                        }
                    }
                    if (coord == -1)
                        System.out.println("No coordinator yet.");
                    else
                        System.out.println("Current Coordinator: Node " + coord);
                    break;

                case 0: // Exit
                    System.out.println("Exiting...");
                    return;

                default:
                    System.out.println("Invalid command");
            }
        }
    }

    // Ring Election Logic
    static void startElection(List<Node> nodes, int startPid) {
        System.out.println("Starting election from Node " + startPid);

        // Create token and add alive nodes in order starting from startPid
        List<Integer> ids = new ArrayList<>();
        int n = nodes.size();
        int index = -1;
        for (int i = 0; i < n; i++) {
            if (nodes.get(i).pid == startPid) {
                index = i;
                break;
            }
        }

        // Move around the ring and collect alive node IDs
        for (int i = 0; i < n; i++) {
            Node node = nodes.get((index + i) % n);
            if (node.alive)
                ids.add(node.pid);
        }

        // Highest PID becomes coordinator
        int newLeader = Collections.max(ids);
        System.out.println("Election complete. New Coordinator: Node " + newLeader);

        // Update all alive nodes with coordinator
        for (Node node : nodes) {
            if (node.alive)
                node.coordinator = newLeader;
        }
    }
}
