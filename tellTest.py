f = open("demofile.txt", "r")
print(f.tell())
print(f.readline())
print(f.tell())

try:
    open("NE.txt", "r")
except Exception as e:
    print("Exception issue: {e}")