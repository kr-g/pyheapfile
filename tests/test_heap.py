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


class HeapTestCase(unittest.TestCase):
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

    def test_heap_open_not_found(self):
        rm_heap_file()
        self.assertRaises(FileNotFoundError, HeapFile(fnam).open)

    def test_heap_create(self):
        rm_heap_file()
        hpf = HeapFile(fnam).create()
        hpf.close()
        fs = os.stat(fnam)
        self.assertEqual(fs.st_size, 0)

    def test_heap_open(self):
        # create empty
        hpf = HeapFile(fnam).create()
        hpf.close()
        hpf = HeapFile(fnam).open()
        hpf.close()

    def test_append(self):
        create_heap()

        hpf = HeapFile(fnam).open()

        node = hpf.alloc_append(15)

        self.assertEqual(node.id, 0)
        self.assertEqual(node.aloc, 15)
        self.assertEqual(node.used, 0)

        hpf.close()

        if pr:
            print(node)

        fs = os.stat(fnam)
        self.assertEqual(fs.st_size, 15 + Node.node_size())

    def test_append_2(self):
        create_heap()

        hpf = HeapFile(fnam).open()

        node = hpf.alloc_append(15)
        node2 = hpf.alloc_append(32)

        n = hpf.read_node(0)
        while n != None:
            if pr:
                print(n)
            n = hpf.read_next(n)

        fs = os.stat(fnam)
        self.assertEqual(fs.st_size, 15 + 32 + 2 * Node.node_size())

        hpf.close()

    def test_trunc(self):
        create_heap()

        hpf = HeapFile(fnam).open()

        node = hpf.alloc_append(15)
        node2 = hpf.alloc_append(32)

        hpf.trunc(node2)

        n = hpf.read_node(0)
        while n != None:
            if pr:
                print(n)
            n = hpf.read_next(n)

        fs = os.stat(fnam)
        self.assertEqual(fs.st_size, 15 + Node.node_size())

        hpf.close()
