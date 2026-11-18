
import math, heapq
from collections import deque

FLOORS = 5
SECTIONS = ["Computer Science", "Science", "Literature", "History", "Business"]
AISLES = 3
SHELVES = 4

def node_id(f,s,a,h):
    return f"F{f}-S{s}-A{a}-H{h}"

def build_graph(closed_sections=None, restricted_nodes=None, crowded_aisles=None):
    closed_sections=set(closed_sections or [])
    restricted_nodes=set(restricted_nodes or [])
    crowded_aisles=set(crowded_aisles or [])
    graph={}
    coords={}
    meta={}
    for f in range(1,FLOORS+1):
        for s, sec in enumerate(SECTIONS,1):
            for a in range(1,AISLES+1):
                for h in range(1,SHELVES+1):
                    n=node_id(f,s,a,h)
                    coords[n]=(f,s,a,h)
                    meta[n]={"floor":f,"section":sec,"section_no":s,"aisle":a,"shelf":h}
                    graph[n]=[]
    def add(u,v,cost,action):
        if u in graph and v in graph and u not in restricted_nodes and v not in restricted_nodes:
            graph[u].append((v,cost,action))
    for n,(f,s,a,h) in coords.items():
        if SECTIONS[s-1] in closed_sections or n in restricted_nodes: continue
        for df,ds,da,dh,act in [(0,0,0,1,"Walk along shelf"),(0,0,0,-1,"Walk along shelf"),
                               (0,0,1,0,"Move to next aisle"),(0,0,-1,0,"Move to previous aisle"),(0,1,0,0,"Move to adjacent section"),
                               (0,-1,0,0,"Move to adjacent section"),(1,0,0,0,"Use stairs to next floor"),(-1,0,0,0,"Use stairs to previous floor")]:
            nf,ns,na,nh=f+df,s+ds,a+da,h+dh
            if not (1<=nf<=FLOORS and 1<=ns<=len(SECTIONS) and 1<=na<=AISLES and 1<=nh<=SHELVES): continue
            v=node_id(nf,ns,na,nh)
            if SECTIONS[ns-1] in closed_sections or v in restricted_nodes: continue
            cost=2.0 if ds else 1.0
            if (f,s,a) in crowded_aisles or (nf,ns,na) in crowded_aisles:
                cost += 4.0
            if df: cost=3.0
            add(n,v,cost,act)
    return graph,coords,meta

def heuristic(u,v,coords):
    x,y=coords[u],coords[v]
    return abs(x[0]-y[0])*3 + abs(x[1]-y[1])*2 + abs(x[2]-y[2]) + abs(x[3]-y[3])

def search(graph,start,goal,algorithm,coords):
    if start not in graph or goal not in graph: return None, [], [], math.inf
    if start==goal: return [start],[start],[],0
    if algorithm=="BFS":
        q=deque([start]); parent={start:None}; opened=[start]; closed=[]
        while q:
            u=q.popleft()
            if u in closed: continue
            closed.append(u)
            if u==goal: break
            for v,_,_ in graph[u]:
                if v not in parent:
                    parent[v]=u; q.append(v); opened.append(v)
        cost=0
    elif algorithm=="DFS":
        stack=[start]; parent={start:None}; opened=[start]; closed=[]
        while stack:
            u=stack.pop()
            if u in closed: continue
            closed.append(u)
            if u==goal: break
            for v,_,_ in reversed(graph[u]):
                if v not in parent:
                    parent[v]=u; stack.append(v); opened.append(v)
        cost=0
    else:
        pq=[(heuristic(start,goal,coords),0,start)]
        parent={start:None}; g={start:0}; opened=[start]; closed=[]
        while pq:
            _,gu,u=heapq.heappop(pq)
            if u in closed: continue
            closed.append(u)
            if u==goal: break
            for v,w,_ in graph[u]:
                ng=gu+w
                if ng<g.get(v,math.inf):
                    g[v]=ng; parent[v]=u
                    heapq.heappush(pq,(ng+heuristic(v,goal,coords),ng,v))
                    opened.append(v)
        cost=g.get(goal,math.inf)
    if goal not in parent: return None,opened,closed,math.inf
    path=[]; cur=goal
    while cur is not None: path.append(cur); cur=parent[cur]
    path.reverse()
    if algorithm!="A*":
        cost=sum(next(w for v2,w,_ in graph[u] if v2==v) for u,v in zip(path,path[1:]))
    return path,opened,closed,cost

def path_actions(graph,path):
    result=[]
    for u,v in zip(path,path[1:]):
        edge=next((e for e in graph[u] if e[0]==v),None)
        if edge: result.append(edge[2])
    return result

def plan_multiple(graph,start,targets,algorithm,coords):
    current=start; full=[start]; legs=[]; total=0; all_open=[]; all_closed=[]
    remaining=list(targets)
    while remaining:
        if algorithm=="A*":
            target=min(remaining,key=lambda n: heuristic(current,n,coords))
        else:
            target=remaining[0]
        path,op,cl,cost=search(graph,current,target,algorithm,coords)
        if not path: legs.append((target,None,math.inf)); return full,legs,math.inf,all_open,all_closed
        full.extend(path[1:]); legs.append((target,path,cost)); total+=cost
        all_open.extend(op); all_closed.extend(cl)
        current=target; remaining.remove(target)
    return full,legs,total,all_open,all_closed
