from pyheapfile.heap import HeapFile

hpf = HeapFile("my-heap.hpf").create()

print("heap file", hpf)

testv = [(10, "hello"), (10, None), (20, "world"), (20, None), (50, "!")]

for i, t in testv:
    node = hpf.alloc_append(i, t.encode() if t != None else None)

n = hpf.read_next(None)

n = hpf.realloc(n, 20)

print("after realloc", n)

print("--- heap node dump")

n = hpf.read_node(0)
while n != None:
    cont = hpf.read_node_content(n) if n.used > 0 else None
    print(n.id, n, cont)
    n = hpf.read_next(n)

hpf.close()
