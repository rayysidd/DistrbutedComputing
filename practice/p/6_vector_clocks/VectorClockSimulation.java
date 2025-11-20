import java.util.*;

class Process {
    int pid; // Process ID
    int n; // Total number of processes
    int[] vector; // Vector clock

    Process(int pid, int n) {
        this.pid = pid;
        this.n = n;
        this.vector = new int[n];
    }

    // Internal event: increment own clock
    void internalEvent() {
        vector[pid]++;
        System.out.println("[P" + pid + "] internal -> " + Arrays.toString(vector));
    }

    // Send event: merges with receiver and simulates receive
    void sendEvent(Process receiver) {
        vector[pid]++; // increment before send
        System.out.println("[P" + pid + "] sending -> " + Arrays.toString(vector));

        // Receiver processes message
        receiver.receive(vector, pid);

        // Optionally, merge receiver vector back to sender to simulate reply
        for (int i = 0; i < n; i++) {
            vector[i] = Math.max(vector[i], receiver.vector[i]);
        }
        vector[pid]++; // increment for receive event (reply)
        System.out.println(
                "[P" + pid + "] updated after merging with P" + receiver.pid + " -> " + Arrays.toString(vector));
    }

    // Receive a message from another process
    void receive(int[] senderVector, int senderPid) {
        for (int i = 0; i < n; i++) {
            vector[i] = Math.max(vector[i], senderVector[i]);
        }
        vector[pid]++; // increment own clock for receive event
        System.out.println("[P" + pid + "] received from P" + senderPid + " -> " + Arrays.toString(vector));
    }
}

public class VectorClockSimulation {

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.print("Enter number of processes: ");
        int n = sc.nextInt();

        Process[] processes = new Process[n];
        for (int i = 0; i < n; i++) {
            processes[i] = new Process(i, n);
        }

        System.out.print("Enter number of steps to simulate: ");
        int steps = sc.nextInt();

        Random rand = new Random();

        // Simulation loop
        for (int step = 0; step < steps; step++) {
            int pid = rand.nextInt(n); // random process
            Process p = processes[pid];

            // Random action: more chance for internal event
            String action = rand.nextInt(3) < 2 ? "internal" : "send";

            if (action.equals("internal")) {
                p.internalEvent();
            } else {
                // Random receiver different from sender
                int receiverPid;
                do {
                    receiverPid = rand.nextInt(n);
                } while (receiverPid == pid);
                Process receiver = processes[receiverPid];
                p.sendEvent(receiver);
            }

            // Small delay for readability
            try {
                Thread.sleep(300);
            } catch (InterruptedException e) {
            }
        }

        System.out.println("\n--- Final Vector Clocks ---");
        for (Process p : processes) {
            System.out.println("P" + p.pid + " -> " + Arrays.toString(p.vector));
        }
    }
}
