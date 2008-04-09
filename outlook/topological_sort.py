# Original topological sort code written by Ofer Faigon (www.bitformation.com) and used with permission
def sort (items, partial_order):
  """Perform topological sort.
     items is a list of items to be sorted.
     partial_order is a list of pairs. If pair (a,b) is in it, it means
     that item a should appear before item b.
     Returns a list of the items in one of the possible orders, or None
     if partial_order contains a loop.
  """
  graph = dict ((node, [0]) for node in items)
  for a, b in partial_order:
    graph[a].append (b)
    graph[b][0] += 1

  roots = [node for (node, nodeinfo) in graph.items () if nodeinfo[0] == 0]

  while roots:
    root = roots.pop ()
    yield root
    for child in graph[root][1:]:
      graph[child][0] -= 1
      if graph[child][0] == 0:
        roots.append (child)
    del graph[root]
  
  if graph:
    raise RuntimeError, "Unable to find solution"
