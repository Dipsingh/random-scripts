import struct,logging
import socket,argparse,netaddr
from subprocess import call
from networkx_viewer import Viewer

def ip2int(addr):
    return struct.unpack_from("!I", socket.inet_aton(addr))[0]
def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I",addr))

class Node:
    def __init__(self):
        self.right = None
        self.left = None
        self.flag = None
        self.prefix= None
        self.bit = None


class Trie:
    def __init__(self):
        self.root = Node()

    def _longest_prefix_value(self, node, key, values,prefix_match,bit_trace):
        '''
        Recursive function on the binary tree which runs DFS to return the longest prefix match.
        '''
        n = len(key)
        if node.flag != None:
            values.append(node.flag)
        if node.prefix != None:
            prefix_match.append(node.prefix)
        if node.bit != None:
            bit_trace.append(node.bit)
        if n == 0:
            return values,prefix_match,bit_trace

        for i in range(n):
            x = key[i]
            if x == "1":
                if node.right != None:
                    return self._longest_prefix_value(node.right, key[i + 1:], values,prefix_match,bit_trace)
                else:
                    return values,prefix_match,bit_trace
            if x == "0":
                if node.left != None:
                    return self._longest_prefix_value(node.left,key[i + 1:], values,prefix_match,bit_trace)
                else:
                    return values,prefix_match,bit_trace

    def longest_prefix_value(self, key):
        values = []
        prefix_match = []
        bit_trace = []
        values,prefix_match,bit_trace = self._longest_prefix_value(self.root, key, values,prefix_match,bit_trace)
        if len(values) == 0:
            return None,None
        return values[-1],prefix_match,bit_trace

    def lookup(self, ip):
        '''
        Convert the IP address into binary format and calls the longest prefix value function
        '''
        x = ip.split(".")
        for i in range(4):
            x[i] = format(int(x[i]), "08b")
        binary = "".join(x)
        return self.longest_prefix_value(binary)

    def add_bin(self, key, value,prefix):
        '''
        Add the IP address in the tree in binary format
        '''
        n = len(key)
        node = self.root
        for i in range(n):
            x = key[i]
            if x == "1":
                if node.right == None:
                    node.right = Node()
                    node.right.bit= "1"
                node = node.right
            elif x == "0":
                if node.left == None:
                    node.left = Node()
                    node.left.bit= "0"
                node = node.left
        node.flag = value
        node.prefix = prefix

    def add_ip_prefix(self, prefix, value):
        '''
        Splits the Network and Mask and converts the Network field in the binary format
        '''
        x = prefix.split(".")
        n = int(x[3].split("/")[1])  # getting the length of prefix
        x[3] = x[3].split("/")[0]
        for i in range(4):
            x[i] = format(int(x[i]), "08b")
        binary = "".join(x)
        binary = binary[:n]
        self.add_bin(binary,value,prefix)

    def draw_graph(self):
        fname= "tree.dot"
        with open(fname, "w") as f:
            f.write("digraph G { ranksep=3; ratio=auto; \n")
            node = self.root
            l = []
            count = 0
            c = "yellow"
            shape = "circle"
            while (node is not None):
                count += 1
                #print(node2net4(node.ID), node.p)
                f.write('"{ip}" [ label="{ip}",shape="{shape}",style="filled",color="{color}" ];\n'.format(ip = node.prefix, color = c, shape = shape))
                if node.right:
                    #print("rigth p: ", node.right.p)
                    f.write('"{r}" -> "{c}" [ label=" ",color="blue",arrowhead="dot" ];\n'.format(r = node.prefix, c = c))
                    l.append(node.right)
                if node.left:
                    #print("left p: ", node.left.p)
                    f.write('"{r}" -> "{c}" [ label=" ",color="blue",arrowhead="dot" ];\n'.format(r = node.prefix, c = node.left.prefix))
                    node = node.left
                else:
                    try:
                        node = l.pop()
                        #print("pop, ", node.p)
                    except:
                        node = None
                    #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Pop: ", node2net4(node.ID))
                '''
                try:
                    if node.p == "F":
                        c = "green"
                    elif node.p == "V":
                        c = "grey"
                    elif node.p == "B":
                        c = "cyan"
                    elif node.p == "A":
                        c = "blue"
                except:
                    # only fails if node is None
                    pass
                '''
            f.write("\n}\n")
        logging.debug("Draw count: {}".format(count))
        sname = fname.rstrip(".dot") + ".svg"
        #call(["twopi", "-Tsvg", "-o" , sname, fname])


def main():
    troot = Trie()
    flag_value = 'T'
    with open("route_table.txt", "r") as f:
        for line in f:
            troot.add_ip_prefix(line, flag_value)

    '''
    troot.draw_graph()
    app=Viewer("tree.dot")
    app.mainloop()
    '''

    print ("Parsed the Routing Table")
    parser = argparse.ArgumentParser(description='Cmd line options for LPM')
    parser.add_argument('-r',action='store',dest='route')
    results = parser.parse_args()
    if results.route:
        flag_value,prefix_match,bit_trace = troot.lookup(results.route)
        if (flag_value!= None) and (prefix_match != None):
            print ("Route matched prefix",prefix_match.pop(),"".join(bit_trace))
        else:
            print ("Given Route didn't Matched.It will take Default if present")


if __name__ == '__main__':
    main()
