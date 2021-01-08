import os

import unittest

from pyheapfile.heap import HeapFile, Node

fnam = "test_heap.hpf"
pr = None


def rm_heap_file():
    try:
        os.remove(fnam)
    except:
        pass


def create_heap():
    # create empty
    rm_heap_file()
    hpf = HeapFile(fnam).create()
    hpf.close()


class HeapFuncTestCase(unittest.TestCase):
    def setUp(self):
        # rm_heap_file()
        pass

    def tearDown(self):
        try:
            fs = os.stat(fnam)
            if pr:
                print(fnam, fs)
        except:
            pass
        if pr:
            shutil.copy(fnam, self._testMethodName + ".hpf")
        rm_heap_file()

    def test_alloc_filled(self):
        create_heap()

        hpf = HeapFile(fnam).open()

        node = hpf.alloc_append(15, "hello".encode())
        node2 = hpf.alloc_append(32, "world!".encode())

        hpf.flush()

        n = hpf.read_node(0)
        while n != None:
            if pr:
                print(n)
                print("node-content:", hpf.read_node_content(n))
            n = hpf.read_next(n)

        fs = os.stat(fnam)
        self.assertEqual(fs.st_size, 15 + 32 + 2 * Node.node_size())

        node = None
        tval = [
            (15, "hello"),
            (32, "world!"),
        ]

        for sz, tx in tval:
            node = hpf.read_next(node)
            cont = hpf.read_node_content(node)
            self.assertEqual(node.aloc, sz)
            self.assertEqual(cont, tx.encode())

        hpf.close()

    def test_alloc_filled(self):
        create_heap()

        hpf = HeapFile(fnam).open()

        node = hpf.alloc_append(15, "hello".encode())
        node2 = hpf.alloc_append(32, "world!".encode())

        hpf.flush()

        n = hpf.read_node(0)
        while n != None:
            if pr:
                print(n)
                print("node-content:", hpf.read_node_content(n))
            n = hpf.read_next(n)

        fs = os.stat(fnam)
        self.assertEqual(fs.st_size, 15 + 32 + 2 * Node.node_size())

        node = None
        tval = [
            (15, "hello"),
            (32, "world!"),
        ]

        for sz, tx in tval:
            node = hpf.read_next(node)
            cont = hpf.read_node_content(node)
            self.assertEqual(node.aloc, sz)
            self.assertEqual(cont, tx.encode())

        hpf.close()

    def test_free(self):
        create_heap()

        hpf = HeapFile(fnam).open()

        sumbytes = 0
        for i, t in [(10, "hello"), (20, "world"), (50, "!")]:
            node = hpf.alloc_append(i, t.encode() if t != None else None)
            sumbytes += len(t)

        hpf.flush()

        nodes = []
        n = hpf.read_node(0)
        while n != None:
            hpf.free(n, merge_free=False)
            nodes.append(n)
            n = hpf.read_next(n)

        node = None
        tval = [
            (10, None),
            (20, None),
            (50, None),
        ]

        for sz, tx in tval:
            node = hpf.read_next(node)
            self.assertEqual(node.aloc, sz)
            if tx:
                cont = hpf.read_node_content(node)
                self.assertEqual(cont, tx.encode())

        hpf.close()

    def test_free_merge(self):
        create_heap()

        hpf = HeapFile(fnam).open()

        sumbytes = 0
        for i, t in [(10, None), (20, "world"), (50, None)]:
            node = hpf.alloc_append(i, t.encode() if t != None else None)
            if t:
                sumbytes += len(t)

        hpf.flush()

        nodes = []
        n = hpf.read_node(0)
        while n != None:
            nodes.append(n)
            n = hpf.read_next(n)

        hpf.free(nodes[1])

        n = hpf.read_node(0)
        numnodes = 0
        while n != None:
            numnodes += 1
            n = hpf.read_next(n)

        self.assertEqual(numnodes, 1)

        node = None
        tval = [
            (10 + 20 + 50 + Node.node_size() * 2, None),
        ]

        for sz, tx in tval:
            node = hpf.read_next(node)
            self.assertEqual(node.aloc, sz)
            if tx:
                cont = hpf.read_node_content(node)
                self.assertEqual(cont, tx.encode())

        hpf.close()

    def test_merge(self):
        create_heap()

        hpf = HeapFile(fnam).open()

        sumbytes = 0
        for i, t in [(10, "hello"), (10, None), (20, "world"), (20, None), (50, "!")]:
            node = hpf.alloc_append(i, t.encode() if t != None else None)
            if t:
                sumbytes += len(t)

        hpf.flush()

        nodes = []

        n = hpf.read_node(0)
        numbytes = 0
        while n != None:
            nodes.append(n)
            numbytes += n.used
            n = hpf.read_next(n)

        hpf.merge_next(nodes[0])
        hpf.merge_next(nodes[2])

        n = hpf.read_node(0)
        numbytes = 0
        numnodes = 0
        while n != None:
            numnodes += 1
            numbytes += n.used
            if pr:
                print(n)
                print("node-content:", hpf.read_node_content(n))
            n = hpf.read_next(n)

        self.assertEqual(sumbytes, numbytes)
        self.assertEqual(numnodes, len(nodes) - 2)

        node = None
        tval = [
            (10 + 10 + Node.node_size(), "hello"),
            (20 + 20 + Node.node_size(), "world"),
            (50, "!"),
        ]

        for sz, tx in tval:
            node = hpf.read_next(node)
            cont = hpf.read_node_content(node)
            self.assertEqual(node.aloc, sz)
            self.assertEqual(cont, tx.encode())

        hpf.close()

    def test_realloc_merge(self):
        create_heap()

        hpf = HeapFile(fnam).open()

        sumbytes = 0
        for i, t in [(10, "hello"), (10, None), (20, "world"), (20, None), (50, "!")]:
            node = hpf.alloc_append(i, t.encode() if t != None else None)
            if t:
                sumbytes += len(t)

        hpf.flush()

        nodes = []

        n = hpf.read_node(0)
        numbytes = 0
        while n != None:
            nodes.append(n)
            numbytes += n.used
            n = hpf.read_next(n)

        n = hpf.realloc(nodes[0], 15)
        self.assertEqual(nodes[0], n)

        n = hpf.read_node(0)
        numbytes = 0
        numnodes = 0
        while n != None:
            numnodes += 1
            numbytes += n.used
            if pr:
                print(n)
                print("node-content:", hpf.read_node_content(n))
            n = hpf.read_next(n)

        self.assertEqual(sumbytes, numbytes)
        self.assertEqual(numnodes, len(nodes) - 1)

        node = None
        tval = [
            (10 + 10 + Node.node_size(), "hello"),
            (20, "world"),
            (20, None),
            (50, "!"),
        ]

        for sz, tx in tval:
            node = hpf.read_next(node)
            self.assertEqual(node.aloc, sz)
            if tx:
                cont = hpf.read_node_content(node)
                self.assertEqual(cont, tx.encode())

        hpf.close()
