import java.util.*;

class Node {
    int pid;
    int coordinator = -1;
    boolean alive = true;

    Node(int pid) {
        this.pid = pid;
    }
}

public class bully {

    public static void main(String[] args) {
        int numNodes = 5;
        List<Node> nodes = new ArrayList<>();
        for (int i = 1; i <= numNodes; i++)
            nodes.add(new Node(i));

        // simulate election
        System.out.println("Starting Bully Algorithm simulation...\n");

        for (Node node : nodes) {
            if (!node.alive)
                continue;

            boolean gotOK = false;

            // send election to higher PID nodes
            for (Node higher : nodes) {
                if (higher.pid > node.pid && higher.alive) {
                    System.out.println("Node " + node.pid + " -> Node " + higher.pid + ": ELECTION");
                    gotOK = true; // if higher node exists, it will respond
                }
            }

            // decide coordinator
            if (!gotOK) {
                node.coordinator = node.pid;
                System.out.println("Node " + node.pid + " becomes COORDINATOR");
                // inform all lower nodes
                for (Node n : nodes) {
                    if (n.pid != node.pid && n.alive) {
                        n.coordinator = node.pid;
                        System.out.println("Node " + node.pid + " -> Node " + n.pid + ": COORDINATOR " + node.pid);
                    }
                }
            } else {
                System.out.println("Node " + node.pid + " waits for higher node to elect coordinator");
            }
            System.out.println();
        }

        // final coordinators
        System.out.println("Final coordinator status:");
        for (Node n : nodes) {
            System.out.println("Node " + n.pid + " sees coordinator: " + n.coordinator);
        }
    }
}
