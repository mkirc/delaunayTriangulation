from quadEdge.primitives import *


def merge(mesh, ldo, ldi, rdi, rdo):

    m = mesh

    print(m.org(ldi), m.dest(ldi), ldi)
    print(m.org(rdi), m.dest(rdi), rdi)
    # 'Compute the lower common tangent of L and R'
    while True:
        while ccw(m.org(rdi), m.org(ldi), m.dest(ldi)):
            ldi = m.lnext(ldi)
        if ccw(m.org(ldi), m.dest(rdi), m.org(rdi)):
            rdi = m.rprev(rdi)
        else:
            break

    # 'Create a first cross edge basel from rdi.Org to ldi.Org'
    basel = m.connect(sym(rdi), ldi, True)
    print(m.org(ldi), m.dest(ldi), ldi)
    print(m.org(rdi), m.dest(rdi), rdi)
    print(m.org(basel), m.dest(basel), basel)

    if m.dest(ldi) == m.org(ldo):
        ldo = sym(basel)
    if m.org(rdo) == m.org(rdi):
        rdo = basel
    
    lcand = m.rprev(basel)
    rcand = m.oprev(basel)

    print(m.org(basel), m.dest(basel), 'b')
    print(m.org(lcand), m.dest(lcand), 'l')
    print(m.org(rcand), m.dest(rcand), 'r')

    def valid(e):
        """
        Since valid() contains a comparison with basel,
        it is defined inside merge()
        """
        return ccw(m.dest(e), m.dest(basel), m.org(basel))
    
    while True:
        """
        'Locate the first L point (lcand.Dest) to be encountered by the rising bubble
         and delete L edges out of basel.Dest that fail the circle test.'
        """

        if valid(lcand):
            print('while lcand valid')
            while inCircle(m.dest(basel), m.org(basel), m.dest(lcand), m.dest(m.edges[lcand])):
                t = m.edges[lcand]
                m.deleteEdge(lcand)
                lcand = t

        """
        'Symmetrically, locate the first R point to be hit, and delete R edges'
        """
        if valid(rcand):
            print('while rcand valid')
            while inCircle(m.dest(basel), m.org(basel), m.dest(rcand), m.dest(m.edges[rcand])):
                t = m.oprev(rcand)
                m.deleteEdge(rcand)
                rcand = t
        
        """
        'If both lcand and rcand are invalid, then basel is the upper common tangent'
        """
        lvalid = valid(lcand)
        rvalid = valid(rcand)

        if not lvalid and not rvalid:
            print('Nothing of validity here')
            break

        """
        'The next cross edge is to be connected to either lcand.Dest or rcand.Dest.
        If both are valid, then choose the appropriate one using the InCircle test:'
        """
        if (not lvalid or 
                (rvalid and 
                    inCircle(m.dest(lcand), m.org(lcand), m.org(rcand), m.dest(rcand)))):

            # 'Add cross edge basel from rcand.Dest to basel.Dest'
            basel = m.connect(rcand, sym(basel)) 
        else:

            # 'Add cross edge basel from basel.Org to lcand.Dest'
            basel = m.connect(sym(basel), sym(lcand))

    return

def delaunay(mesh, start, end, leftEdge=None, rightEdge=None, rows=None):

    """
    This is an implentation of the divide-and-conquer alorithm proposed
    by guibas & stolfi.
    """

    m = mesh
    verts = m.vertices
    if start < (end - 2): # four or more points

        xMin = verts[start]
        xMax = verts[end]

        # divide points in two halves
        split = (end - start) // 2

        # recurse down the halves 
        ldo, ldi = delaunay(m, start, split)
        rdi, rdo = delaunay(m, (split + 1), end)

        # recursively merge the obtained halves
        merge(m, ldo, ldi, rdi, rdo) 


        # while m.org(ldo) != xMin:
        #     ldo = m.rprev(ldo)

        # while m.org(rdo) != xMax:
        #     rdo = m.lprev(rdo)

        # leftEdge = ldo
        # rightEdge = rdo
        
        return [leftEdge, rightEdge]

    elif start >= (end - 1): # two or one points
        """
        Original Comment:
         'Let s1, s2 be the two sites, in sorted order. 
          Create an edge a from s1 to s2'
        """

        a = m.makeEdge(verts[start], verts[end])
        leftEdge = a
        rightEdge = sym(a)

        if start == end:
            print('Lonely Point.')
        
        return [leftEdge, rightEdge]

    else: # Three points
        """
        Original Comment:
         'Let sl, s2, s 3 be the three sites, in sorted order.
          Create edges a connecting s 1 to s2 and b connecting a2 to s3'
        """

        v1 = verts[start]
        v2 = verts[start + 1]
        v3 = verts[end]
        a = m.makeEdge(v1, v2)
        b = m.makeEdge(v2, v3)
        m.splice(sym(a), b)

        """'Now close the triangle'"""
        
        c = m.connect(b, a)

        if ccw(v1, v3, v2):

            leftEdge = sym(a)
            rightEdge = c

        else:

            leftEdge = a
            rightEdge = sym(b)

        if not ccw(v1, v2, v3):
            m.deleteEdge(c)

        return [leftEdge, rightEdge]
