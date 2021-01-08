import os
import shutil

import unittest

from pyheapfile.heap import HeapFile, Node

fnam = "test_heap.hpf"
pr = None  # or True


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


class HeapReallocTestCase(unittest.TestCase):
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

    def test_realloc_find_block(self):
        create_heap()

        hpf = HeapFile(fnam).open()

        sumbytes = 0
        for i, t in [(10, "hello"), (10, None), (20, "world"), (200, None), (50, "!")]:
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

        n = hpf.realloc(nodes[0], 200, merge_free=False)
        self.assertEqual(nodes[3].id, n.id)

        nodes = []

        n = hpf.read_node(0)
        numbytes = 0
        numnodes = 0
        while n != None:
            nodes.append(n)
            numnodes += 1
            numbytes += n.used
            if pr:
                print(n)
                print("node-content:", hpf.read_node_content(n))
            n = hpf.read_next(n)

        self.assertEqual(sumbytes, numbytes)
        self.assertEqual(numnodes, len(nodes))

        node = None
        tval = [
            (10, None),
            (10, None),
            (20, "world"),
            (200, "hello"),
            (50, "!"),
        ]

        for sz, tx in tval:
            node = hpf.read_next(node)
            self.assertEqual(node.aloc, sz)
            if tx:
                cont = hpf.read_node_content(node)
                self.assertEqual(cont, tx.encode())

        hpf.close()

    def test_realloc_append(self):

        print("name", self._testMethodName)

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

        n = hpf.realloc(nodes[0], 200, merge_free=False)
        hpf.flush()

        l = nodes[-1]
        self.assertEqual(l.id + l.aloc + Node.node_size(), n.id)

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
        self.assertEqual(numnodes, len(nodes) + 1)

        hpf.close()
