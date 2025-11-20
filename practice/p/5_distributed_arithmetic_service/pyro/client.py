import Pyro5.api

# Replace with the URI printed by the server
uri = "PYRO:obj_XXXXXXXXXXXXXXXX@localhost:XXXX"  # copy from server output

proxy = Pyro5.api.Proxy(uri)

# Remote calls
print("Addition 15 + 7 =", proxy.addition(15, 7))
print("Subtraction 30 - 12 =", proxy.subtraction(30, 12))
print("Multiplication 6 * 8 =", proxy.multiplication(6, 8))
