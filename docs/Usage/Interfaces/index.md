# Interfaces 

`monarch-py` provides a collection of interfaces that abstractify implementation details,  
and provide a coherent set of graph operations.  

Developers can code according to the interface, mostly ignoring whether the implementation  
is a relational database, a local file, etc.  
    <!-- <sub>(The one exception is the [OAK implementation](../Implementations/OAK.md), which is used primarily for functionality related to semantic similarity.)</sub> -->

### Interface

- [Entity](./Entity.md)
- [Association](./Association.md)
- [Query](./Query.md)
- [Search](./Search.md)


