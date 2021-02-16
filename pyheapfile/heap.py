import os


def to_bytes(buf, blen=1):
    # return buf.to_bytes(blen, byteorder=Node.BYTEORD)
    rc = []
    for i in range(0, blen):
        b = buf & 0xFF
        rc.append(b)
        buf >>= 8
    return bytes(reversed(rc))


def from_bytes(buf):
    # return int.from_bytes(buf, byteorder=Node.BYTEORD)
    rc = 0
    for i in range(0, len(buf)):
        rc <<= 8
        rc |= buf[i]
    return rc


class Node(object):

    MAGKNUM = 4
    BYTENUM = 6

    MAGIK_BEG = 0x_2_BAD_DEAD
    # MAGIK_END = 0xBADC0FEE
    # MAGIK_BEF = 0xDEADBEEF

    @staticmethod
    def the_byte_num():
        return Node.BYTENUM

    @staticmethod
    def node_size():
        return Node.MAGKNUM + Node.the_byte_num() * 2

    def __init__(self):

        # not persisted values
        self.id = None
        self.prev = None
        self.succ = None

        # persisted values
        self.mark_beg = Node.MAGIK_BEG
        self.aloc = 0
        self.used = 0

    def valid(self):
        return self.mark_beg == Node.MAGIK_BEG

    def to_bytes(self):
        rby = []
        rby.extend(to_bytes(self.mark_beg, self.MAGKNUM))
        rby.extend(to_bytes(self.aloc, self.the_byte_num()))
        rby.extend(to_bytes(self.used, self.the_byte_num()))
        return bytes(rby)

    @staticmethod
    def _split(buf, blen):
        return buf[:blen], buf[blen:]

    def from_bytes(self, buf):
        b, buf = self._split(buf, self.MAGKNUM)
        self.mark_beg = from_bytes(b)
        b, buf = self._split(buf, self.the_byte_num())
        self.aloc = from_bytes(b)
        b, buf = self._split(buf, self.the_byte_num())
        self.used = from_bytes(b)
        return self

    def __repr__(self):
        return (
            "id:"
            + str(self.id)
            + ":"
            + str(self.prev)
            + ":"
            + str(self.succ)
            + ":"
            + str(["{:02X}".format(x) for x in self.to_bytes()])
        )


class HeapFile(object):
    def __init__(self, fnam):
        self.fnam = fnam
        self.fd = None

    def __repr__(self):
        return self.__class__.__name__ + "(" + self.fnam + ", " + str(self.fd) + ")"

    def _assert_fd(self):
        if self.fd != None:
            raise Exception("file already open")

    # low level api
    #
    # dont use directly

    def read(self, rlen=-1):
        return self.fd.read(rlen)

    def write(self, data):
        return self.fd.write(data)

    def truncate(self, flen):
        return self.fd.truncate(flen)

    def seek(self, offset, whence=os.SEEK_SET):
        return self.fd.seek(offset, whence)

    # high level api

    def create(self):
        self._assert_fd()
        self.fd = open(self.fnam, "w+b")
        return self

    def open(self):
        self._assert_fd()
        self.fd = open(self.fnam, "r+b")
        return self

    def close(self):
        if self.fd != None:
            self.fd.close()
            self.fd = None

    def flush(self):
        self.fd.flush()

    def read_node(self, nodeid):
        flen = self.seek(0, os.SEEK_END)
        if nodeid >= flen:
            return None
        self.seek(nodeid)
        buf = self.read(Node.node_size())
        n = Node().from_bytes(buf)
        n.id = nodeid
        if n.valid() is False:
            raise Exception("no node", n)
        return n

    def read_next(self, node):
        if node == None:
            return self.read_node(0)
        nodeid = node.id + Node.node_size() + node.aloc
        node.succ = nodeid
        n = self.read_node(nodeid)
        if n != None:
            n.prev = node.id
        return n

    def read_node_content(self, node, offs=0, datalen=None):
        if datalen == None:
            datalen = node.used
        if offs < 0 or offs + datalen > node.used:
            raise Exception("boundery violation")
        self.seek(node.id + Node.node_size() + offs)
        if node.used > 0:
            data = self.read(datalen)
            return data

    def write_node(self, node, data=None, validate=True):
        if validate and node.valid() is False:
            raise Exception("no node")
        self.seek(node.id)
        if data != None:
            node.used = len(data)
            if node.used > node.aloc:
                raise Exception("no free memory")
        self.write(node.to_bytes())
        if data != None:
            self.write_node_content(node, data)
        return node

    def write_node_content(self, node, data, offs=0):
        # this doesnt write the node itself
        if offs + len(data) > node.used:
            raise Exception("boundery violation")
        self.seek(node.id + offs + Node.node_size())
        self.write(data)
        return node

    def find_free(self, datalen, equal_size_match=False):
        n = self.read_node(0)
        while n != None:
            if equal_size_match is False:
                if n.used == 0 and n.aloc >= datalen:
                    break
            elif n.used == 0 and n.aloc == datalen:
                break

            n = self.read_next(n)
        return n

    def alloc(self, datalen, data=None, equal_size_match=False):
        n = self.find_free(datalen, equal_size_match)
        if n == None:
            return self.alloc_append(datalen, data)
        if n.used != 0:
            raise Exception("internal error")
        n.used = datalen
        return self.write_node(n, data)

    def alloc_append(self, datalen, data=None):
        flen = self.seek(0, os.SEEK_END)
        n = Node()
        n.id = flen
        n.aloc = datalen
        self.write_node(n, data)
        if n.used != n.aloc:
            # adjust block and file length
            self.seek(n.id + Node.node_size() + n.aloc - 1)
            self.write(bytes([0x55]))
        return n

    def free(self, node, merge_free=True):
        node.used = 0
        self.write_node(node)
        if merge_free is True:
            # try to merge next node
            self.merge_next(node)
            if node.prev != None:
                # try to merge previous node
                node = self.read_node(node.prev)
                self.merge_next(node)

    def merge_next(self, node):
        """merge if next node if it is empty"""
        nx = self.read_next(node)
        if nx != None and nx.used == 0:
            node.aloc = node.aloc + nx.aloc + Node.node_size()
            nx.mark_beg = 0xAAAAAAAA
            self.write_node(nx, validate=False)
            self.write_node(node)
            return True

    def realloc(self, node, newlen, merge_free=True, blk_size=4096):
        nx = self.read_next(node)
        if nx != None and nx.used == 0:
            if nx.aloc + Node.node_size() + node.aloc >= newlen:
                self.merge_next(node)
                return node
        n = self.find_free(newlen)
        if n == None:
            n = self.alloc_append(newlen)
        remain = node.used
        pos = 0
        while remain > 0:
            self.seek(node.id + Node.node_size() + pos)
            datalen = min(remain, blk_size)
            data = self.read(datalen)
            self.seek(n.id + Node.node_size() + pos)
            self.write(data)
            remain -= datalen
            pos += datalen
        n.used = node.used
        self.write_node(n)
        self.free(node, merge_free=merge_free)
        return n

    def split(self, node, datalen, minsize=16):
        if node.used >= datalen:
            raise Exception("node data overflow", node.used, datalen)
        splitnodesize = node.aloc - datalen - Node.node_size()
        if splitnodesize > minsize:
            node.aloc = datalen
            self.write_node(node)
            n = Node()
            n.id = node.id + Node.node_size() + node.aloc
            n.aloc = splitnodesize
            self.write_node(n)
            node.succ = n.id
        return node

    def trunc(self, node):
        if node.valid() is False:
            raise Exception("no node")
        return self.truncate(node.id)
