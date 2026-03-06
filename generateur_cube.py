from collections import deque


# --- Définition des pièces et de l'état résolu --

CORNERS = { # Numérotation et nommage des coins
    0 : "ULB", 1 : "URB", 2 : "URF", 3 : "ULF", 
    4 : "DLF", 5 : "DRB", 6 : "DRF", 7 : "DLB",
}     
# Signification des lettres : U=Up, D=Down, L=Left, R=Right, F=Front, B=Behind

EDGES = { # Numérotation et nommage des arêtes
    0 : "UB", 1 : "UR", 2 : "UF", 3 : "UL",   
    4 : "FR", 5 : "FL", 6 : "BL", 7 : "BR",   
    8 : "DF", 9 : "DR", 10 : "DB", 11 : "DL", 
}

corner_positions = (0, 1, 2, 3, 4, 5, 6, 7) # À l'emplacement i se trouve le coin j

corner_orientations = (0, 0, 0, 0, 0, 0, 0, 0) # Orientation de chaque coin
# corner_orientations[i] indique l'orientation de coin présent à l'emplacement i
# Un coin ayant trois ouleurs, il y a trois possibilités : 
#    - corner_orientations[i] = 0 : le coin est bien orienté
#    - corner_orientations[i] = 1 : le coin est tourné de 120° dans le sens des aiguilles d'une montre
#    - corner_orientations[i] = 2 : le coin est tourné de 120° dans le sens inverse des aiguilles d'une montre

edge_positions = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11) # À l'emplacement i se trouve l'arête j

edge_orientations = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
# edge_orientations[i] indique si l'arête à l'emplacement i est bien orientée ou si elle est retournée
#    - edge_orientations[i] = 0 : l'arête est bien orientée
#    - edge_orientations[i] = 1 : l'arête est retournée


SOLVED_STATE = (corner_positions, corner_orientations, edge_positions, edge_orientations)


# -- Implémentation des rotations --

def apply_U(state) :
    # Rotation horaire de la face du Haut (Up)
    cp, co, ep, eo = state
    
    # Coins
    new_cp = list(cp)
    new_cp[1] = cp[0]  # URB reçoit ULB
    new_cp[2] = cp[1]  # URF reçoit URB
    new_cp[3] = cp[2]  # ULF reçoit URF
    new_cp[0] = cp[3]  # ULB reçoit ULF
    
    # Arêtes
    new_ep = list(ep)
    new_ep[1] = ep[0]  # UR reçoit UB
    new_ep[2] = ep[1]  # UF reçoit UR
    new_ep[3] = ep[2]  # UL reçoit UF
    new_ep[0] = ep[3]  # UB reçoit UL
    
    # Pas de changement d'orientation pour le mouvement U
    return (tuple(new_cp), tuple(co), tuple(new_ep), tuple(eo))

def apply_D(state) :
    # Rotation horaire de la face du Bas (Down)
    cp, co, ep, eo = state
    
    # Coins
    new_cp = list(cp)
    new_cp[4] = cp[7]  # DLF reçoit DLB
    new_cp[5] = cp[4]  # DRB reçoit DLF
    new_cp[6] = cp[5]  # DRF reçoit DRB
    new_cp[7] = cp[6]  # DLB reçoit DRF
    
    # Arêtes
    new_ep = list(ep)
    new_ep[8] = ep[11]   # DF reçoit DL
    new_ep[9] = ep[8]    # DR reçoit DF
    new_ep[10] = ep[9]   # DB reçoit DR
    new_ep[11] = ep[10]  # DL reçoit DB
    
    # Pas de changement d'orientation pour le mouvement D
    return (tuple(new_cp), tuple(co), tuple(new_ep), tuple(eo))

def apply_R(state) :
    # Rotation horaire de la face Droite (Right)
    cp, co, ep, eo = state
    
    # Coins
    new_cp = list(cp)
    new_cp[2] = cp[1]  # URF reçoit URB
    new_cp[5] = cp[2]  # DRB reçoit URF
    new_cp[6] = cp[5]  # DRF reçoit DRB
    new_cp[1] = cp[6]  # URB reçoit DRF
    
    # L'orientation des coins change : modulo 3 (+1 ou +2 selon le sens du basculement)
    new_co = list(co)
    new_co[2] = (co[1] + 2) % 3  # URF
    new_co[5] = (co[2] + 1) % 3  # DRF
    new_co[6] = (co[5] + 2) % 3  # DRB
    new_co[1] = (co[6] + 1) % 3  # URB
    
    # Arêtes
    new_ep = list(ep)
    new_ep[4] = ep[1]  # FR reçoit UR
    new_ep[9] = ep[4]  # DR reçoit FR
    new_ep[7] = ep[9]  # BR reçoit DR
    new_ep[1] = ep[7]  # UR reçoit BR
    
    # R ne retourne pas les arêtes
    return (tuple(new_cp), tuple(new_co), tuple(new_ep), tuple(eo))

def apply_L(state) :
    # Rotation horaire de la face Gauche (Left)
    cp, co, ep, eo = state
    
    # Coins
    new_cp = list(cp)
    new_cp[4] = cp[3]  # DLF reçoit ULF
    new_cp[7] = cp[4]  # DLB reçoit DLF
    new_cp[0] = cp[7]  # ULB reçoit DLB
    new_cp[3] = cp[0]  # ULF reçoit ULB
    
    # Orientation des coins
    new_co = list(co)
    new_co[4] = (co[3] + 1) % 3  # DLF
    new_co[7] = (co[4] + 2) % 3  # DLB
    new_co[0] = (co[7] + 2) % 3  # ULB
    new_co[3] = (co[0] + 1) % 3  # ULF
    
    # Arêtes
    new_ep = list(ep)
    new_ep[11] = ep[5]  # DL reçoit FL
    new_ep[6] = ep[11]  # BL reçoit DL
    new_ep[3] = ep[6]   # UL reçoit BL
    new_ep[5] = ep[3]   # FL reçoit UL
    
    # L ne retourne pas les arêtes
    return (tuple(new_cp), tuple(new_co), tuple(new_ep), tuple(eo))

def apply_F(state) :
    # Rotation horaire de la face Avant (Front)
    cp, co, ep, eo = state
    
    # Coins
    new_cp = list(cp)
    new_cp[6] = cp[2]  # DRF reçoit URF
    new_cp[4] = cp[6]  # DLF reçoit DRF
    new_cp[3] = cp[4]  # ULF reçoit DLF
    new_cp[2] = cp[3]  # URF reçoit ULF
    
    # Orientation des coins
    new_co = list(co)
    new_co[6] = (co[2] + 2) % 3  # DRF
    new_co[4] = (co[6] + 1) % 3  # DLF
    new_co[3] = (co[4] + 1) % 3  # ULF
    new_co[2] = (co[3] + 2) % 3  # URF
    
    # Arêtes
    new_ep = list(ep)
    new_ep[4] = ep[2]  # FR reçoit UF
    new_ep[8] = ep[4]  # DF reçoit FR
    new_ep[5] = ep[8]  # FL reçoit DF
    new_ep[2] = ep[5]  # UF reçoit FL
    
    # Orientation des arêtes (Flip)
    new_eo = list(eo)
    # 1 - eo[i] inverse le bit d'orientation
    new_eo[4] = 1 - eo[2]  # FR
    new_eo[8] = 1 - eo[4]  # DF
    new_eo[5] = 1 - eo[8]  # FL
    new_eo[2] = 1 - eo[5]  # UF

    return (tuple(new_cp), tuple(new_co), tuple(new_ep), tuple(new_eo))

def apply_B(state) :
    # Rotation horaire de la face Arrière (Behind)
    cp, co, ep, eo = state
    
    # Coins
    new_cp = list(cp)
    new_cp[0] = cp[1]  # ULB reçoit URB
    new_cp[7] = cp[0]  # DLB reçoit ULB
    new_cp[5] = cp[7]  # DRB reçoit DLB
    new_cp[1] = cp[5]  # URB reçoit DRB
    
    # Orientation des coins
    new_co = list(co)
    new_co[0] = (co[1] + 1) % 3  # ULB
    new_co[7] = (co[0] + 2) % 3  # DLB
    new_co[5] = (co[7] + 2) % 3  # DRB
    new_co[1] = (co[5] + 1) % 3  # URB
    
    # Arêtes
    new_ep = list(ep)
    new_ep[6] = ep[0]   # BL reçoit UB
    new_ep[10] = ep[6]  # DB reçoit BL
    new_ep[7] = ep[10]  # BR reçoit DB
    new_ep[0] = ep[7]   # UB reçoit BR
    
    # B retourne les 4 arêtes de la face arrière
    new_eo = list(eo)
    new_eo[6] = 1 - eo[0]   # BL
    new_eo[10] = 1 - eo[6]  # DB
    new_eo[7] = 1 - eo[10]  # BR
    new_eo[0] = 1 - eo[7]   # UB

    return (tuple(new_cp), tuple(new_co), tuple(new_ep), tuple(new_eo))




# -- Gestion des mouvements --

# Liste des 18 mouvements du Rubik's Cube
MOVES = ["U", "U'", "U2", "D", "D'", "D2",
         "F", "F'", "F2", "B", "B'", "B2",
         "L", "L'", "L2", "R", "R'", "R2"]

def apply_move(state, move) :
    # Applique un mouvement complet au cube
    # Pour éviter de coder 18 fonction différentes :
    #    - les demi-tours (X2) sont obtenus en appliquant le mouvement de base 2 fois
    #    - les rotations anti-horaires (X') sont obtenues en l'appliquant 3 fois
    move_letter = move[0]
    MOVES_DICT = {"U" : apply_U, "D" : apply_D, "R" : apply_R, 
                  "L" : apply_L, "F" : apply_F, "B" : apply_B}
    apply_func = MOVES_DICT[move_letter]

    if move.endswith("2") :
        return apply_func(apply_func(state))
    elif move.endswith("'") :
        return apply_func(apply_func(apply_func(state)))
    else : 
        return apply_func(state)


# -- Recherche des plus courts chemins (BFS) --

def bfs(depth) :
    # BFS pour trouver tous les états du cube possibles jusqu'à une profondeur donnée
    queue = deque()
    visited_states = {SOLVED_STATE}
    queue.append((SOLVED_STATE, 0)) # La file d'attente stocke des paires : (état_du_cube, profondeur_actuelle)
    results = []

    while queue :
        state, state_depth = queue.popleft()
        
        # Si on atteint la profondeur cible, on stocke l'état et on arrête cette branche
        if state_depth == depth : 
            results.append(state)
            continue
            
        # Sinon, on génère les 18 états "enfants" possibles
        for move in MOVES : 
            new_state = apply_move(state, move)
            
            # Si l'état est nouveau on l'ajoute à la queue et à l'ensemble des états visités
            if new_state not in visited_states :
                visited_states.add(new_state)
                queue.append((new_state, state_depth + 1))
    
    return results


# -- Encodage binaire --

def state_to_binary(state) :
    # Conversion d'un état du cube en une liste de 244 bits
    cp, co, ep, eo = state
    binary_state = []

    for pos in cp : # 8 coins * 8 positions possibles, soit 64 bits
        bits = [0] * 8
        bits[pos] = 1 # Le bit 1 indique la position du coin
        binary_state.extend(bits)

    for ori in co : # 8 coins * 3 orientations (0, 1, 2), soit 24 bits
        bits = [0] * 3
        bits[ori] = 1 # Le bit 1 indique l'orientation du coin 
        binary_state.extend(bits)
        
    for pos in ep : # 12 arêtes * 12 positions possibles, soit 124 bits
        bits = [0] * 12
        bits[pos] = 1
        binary_state.extend(bits)

    # L'orientation des arête est déjà binaire (0 ou 1), donc on peut les ajouter directement
    binary_state.extend(eo) # Ce qui nous fait 12 bits

    return binary_state 


# -- Tests sur le programme --

# Nombre d'états atteints avec le BFS en fonction de la profondeur souhaitée
for i in range(5) :
    results = bfs(i)
    print(f"Nombre d'états uniques atteints pour la profondeur {i} : {len(results)}.")

# Test de l'encodage binaire pour la profondeur 1 (soit 18 états)
states_depth_1 = bfs(1)
first_state = states_depth_1[0]
binary_first_state = state_to_binary(first_state)
print(f"Taille de la liste binaire : {len(binary_first_state)}")