import cv2
import mediapipe as mp
import time
import numpy as np
import math

# Couleur en BGR
bleu = (255, 0, 0)      # Bleu
vert = (0, 255, 0)      # Vert
rouge = (0, 0, 255)     # Rouge

cyan = (255, 255, 0)    # Cyan
magenta = (255, 0, 255) # Magenta
jaune = (0, 255, 255)   # Jaune

noir = (0, 0, 0)        # Noir
blanc = (255, 255, 255) # Blanc

orange = (0, 165, 255)  # Orange
violet = (128, 0, 128)  # Violet
gris = (128, 128, 128)  # Gris
marron = (42, 42, 165)   # Marron
turquoise = (255, 215, 0) # Turquoise
rose = (203, 192, 255)   # Rose
argent = (192, 192, 192)  # Argent
beige = (255, 228, 196)  # Beige
olive = (0, 128, 128)    # Olive

police = cv2.FONT_HERSHEY_PLAIN

class handDetector():

    '''
    Class pour detecter les mains
    '''

    def __init__(self, mode=False, maxHands=2, modelComp=1, detectionCon=0.7, trackCon=0.6):
        self.mode = mode
        self.maxHands = maxHands
        self.modelComp = modelComp
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.modelComp, self.detectionCon, self.trackCon)

        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        hands = []
        if self.results.multi_hand_landmarks:
            hands = self.results.multi_hand_landmarks
            for handsLms in hands:
                if draw:
                    self.mpDraw.draw_landmarks(img, handsLms, self.mpHands.HAND_CONNECTIONS)
        return hands, img

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, bleu, cv2.FILLED)
        
        label = None
        if self.results.multi_handedness:
            for hand_handedness in self.results.multi_handedness:
                label = hand_handedness.classification[0].label
                # Inverser le label
            if label == "Right":
                label = "Left"
            elif label == "Left":
                label = "Right"

        return lmList, label
    
    
class hand:

    '''
    Class pour les mains
    '''

    def __init__(self, lmList, label):
        self.lmList = lmList
        self.label = label
        self.min_x, self.max_x, self.min_y, self.max_y = self.maxima()
        '''
        if self.lmList:
            self.lm_coord()
        '''


    def maxima(self):
        lmList_np = np.array(self.lmList)
        # Extraire x et y
        x_coords = lmList_np[:, 1]  # 2e colonne
        y_coords = lmList_np[:, 2]  # 3e colonne

        # Trouver les min et max pour x et y
        min_x = np.min(x_coords)
        max_x = np.max(x_coords)
        min_y = np.min(y_coords)
        max_y = np.max(y_coords)

        return min_x, max_x, min_y, max_y

    def boite(self, img, draw=True):
        #min_x, max_x, min_y, max_y = self.maxima()

        # Coordonnées supérieur gauche
        pt_sup_gauche = (self.min_x, self.min_y)

        # Coordonnées inférieur droit
        pt_inf_droite = (self.max_x, self.max_y)

        if draw:
            offset = (10, 10)
            ptsg_offset = (pt_sup_gauche[0]-offset[0], pt_sup_gauche[1]-offset[1])
            ptid_offset = (pt_inf_droite[0]+offset[0], pt_inf_droite[1]+offset[1])
            cv2.rectangle(img, ptid_offset, ptsg_offset, vert, 2) # Rectangle
            cv2.circle(img, ptsg_offset, 5, rouge, -1)            # Point supérieur       
            cv2.circle(img, ptid_offset, 5, bleu, -1)             # Point inférieur

        return pt_sup_gauche, pt_inf_droite

    # Affiche centré au dessus de la main le label Gauche ou Droite
    def handedness_printing(self, img, pt_sup_gauche, pt_inf_droite):
        text_x = (pt_sup_gauche[0] + pt_inf_droite[0]) // 2
        text_y = pt_sup_gauche[1] - 5

        # Spécifier la police et la taille
        police_taille = 1
        police_epaisseur = 1

        # Obtenir la taille du texte
        text_size = cv2.getTextSize(self.label, police, police_taille, police_epaisseur)[0]

        # Calculer les coordonnées du coin inférieur gauche du texte pour centrer le texte sur (text_x, text_y), on ajuste
        text_x_start = text_x - text_size[0] // 2  # Ajustement pour centrer horizontalement
        text_y_start = text_y - text_size[1] // 2  # Ajustement pour centrer verticalement

        cv2.putText(img, self.label, (text_x_start, text_y_start), police, police_taille, noir, police_epaisseur, cv2.LINE_AA)

        return

    # Pour emote thumb up
    def is_pouce_up(self):
        #min_x, max_x, min_y, max_y = self.maxima()

        # Pouce aligner vers le haut
        alignement_pouce_up_y = self.lmList[0][2] > self.lmList[1][2] > self.lmList[2][2] > self.lmList[3][2] > self.lmList[4][2]

        # Bout du pouce le plus haut
        pouce_up = self.lmList[4][2] == self.min_y

        if alignement_pouce_up_y and self.ecart_pouce_x() and pouce_up:
            return True
        else:
            return False
        
    # Pour emote thumb down 
    def is_pouce_down(self):
        #min_x, max_x, min_y, max_y = self.maxima()

        # Pouce aligner vers le haut
        alignement_pouce_down_y = self.lmList[0][2] < self.lmList[1][2] < self.lmList[2][2] < self.lmList[3][2] < self.lmList[4][2]         

        # Bout du pouce le plus bas
        pouce_down = self.lmList[4][2] == self.max_y

        if alignement_pouce_down_y and self.ecart_pouce_x() and pouce_down:
            return True
        else:
            return False
        
    # Bout du pouce entre poignet et début d'index par rapport à x
    def ecart_pouce_x(self):
        poignet_left = self.lmList[0][1] == self.min_x or self.lmList[1][1] == self.min_x
        poignet_right = self.lmList[0][1] == self.max_x or self.lmList[1][1] == self.max_x

        if poignet_left:
            ecart_x = self.lmList[0][1] < self.lmList[4][1] < self.lmList[5][1]
        elif poignet_right:
            ecart_x = self.lmList[0][1] > self.lmList[4][1] > self.lmList[5][1]
        else:
            ecart_x = False

        return ecart_x


    # Pour emoji pouce vers le haut ou vers le bas
    # Doigts pliés horizontalement
    def is_four_fingers_folded(self):
        #min_x, max_x, _, _ = self.maxima()

        poignet_left = self.lmList[0][1] == self.min_x or self.lmList[1][1] == self.min_x
        poignet_right = self.lmList[0][1] == self.max_x or self.lmList[1][1] == self.max_x

        fingerList = [8, 12, 16, 20]
        finger_unfold = False
        for n in fingerList:
            if poignet_left:
                if self.lmList[n][1] > self.lmList[n-2][1]:
                    finger_unfold = True
                    break
            elif poignet_right:
                if self.lmList[n][1] < self.lmList[n-2][1]:
                    finger_unfold = True
                    break

        if not finger_unfold:
            return True
        else:
            return False

    # Emoji pouce vers le haut  
    def is_emote_thumb_up(self):
        if self.is_pouce_up() and self.is_four_fingers_folded():
            return True
        else:
            return False

    # Emoji pouce vers le bas
    def is_emote_thumb_down(self):
        if self.is_pouce_down() and self.is_four_fingers_folded():
            return True
        else:
            return False
        
    # Liste des doigts levés de l'index au petit
    def four_fingerList_up(self):
        fingerList = [8, 12, 16, 20]
        finger_up = []
        for n in fingerList:
            if self.lmList[n][2] < self.lmList[n-2][2] and self.lmList[0][2] == self.max_y:
                finger_up.append(1)
            else:
                finger_up.append(0)

        return finger_up
    
    # Pouce plié pour le nombre de doigt vers le haut
    def is_thumb_unfolded(self):
        distance0 = distance_calcul(self.lmList, 4, self.lmList, 3)
        distance1 = distance_calcul(self.lmList, 4, self.lmList, 0)
        distance2 = distance_calcul(self.lmList, 3, self.lmList, 0)

        if distance1 > (distance2 + distance0 * 0.3):
            return 1
        else:
            return 0
    
    # Nombre de doigts levés
    def doigts_up(self):
        if self.lmList[0][2] == self.max_y:
            return [self.is_thumb_unfolded()] + self.four_fingerList_up()
        else:
            return []

    # A tester si pratique pour coder ou pas
    # Traduction des coordonées dans la liste en mot
    def lm_coord(self):
        # Pour le poignet (wrist)
        self.wrist_x = self.lmList[0][1]
        self.wrist_y = self.lmList[0][2]

        # Pour le pouce (thumb)
        self.thumb_cmc_x = self.lmList[1][1]
        self.thumb_cmc_y = self.lmList[1][2]

        self.thumb_mcp_x = self.lmList[2][1]
        self.thumb_mcp_y = self.lmList[2][2]

        self.thumb_ip_x = self.lmList[3][1]
        self.thumb_ip_y = self.lmList[3][2]

        self.thumb_tip_x = self.lmList[4][1]
        self.thumb_tip_y = self.lmList[4][2]

        # Pour l'index (index finger)
        self.index_mcp_x = self.lmList[5][1]
        self.index_mcp_y = self.lmList[5][2]

        self.index_pip_x = self.lmList[6][1]
        self.index_pip_y = self.lmList[6][2]

        self.index_dip_x = self.lmList[7][1]
        self.index_dip_y = self.lmList[7][2]

        self.index_tip_x = self.lmList[8][1]
        self.index_tip_y = self.lmList[8][2]

        # Pour le majeur (middle finger)
        self.middle_mcp_x = self.lmList[9][1]
        self.middle_mcp_y = self.lmList[9][2]

        self.middle_pip_x = self.lmList[10][1]
        self.middle_pip_y = self.lmList[10][2]

        self.middle_dip_x = self.lmList[11][1]
        self.middle_dip_y = self.lmList[11][2]

        self.middle_tip_x = self.lmList[12][1]
        self.middle_tip_y = self.lmList[12][2]

        # Pour l'annulaire (ring finger)
        self.ring_mcp_x = self.lmList[13][1]
        self.ring_mcp_y = self.lmList[13][2]

        self.ring_pip_x = self.lmList[14][1]
        self.ring_pip_y = self.lmList[14][2]

        self.ring_dip_x = self.lmList[15][1]
        self.ring_dip_y = self.lmList[15][2]

        self.ring_tip_x = self.lmList[16][1]
        self.ring_tip_y = self.lmList[16][2]

        # Pour l'auriculaire (pinky finger)
        self.pinky_mcp_x = self.lmList[17][1]
        self.pinky_mcp_y = self.lmList[17][2]

        self.pinky_pip_x = self.lmList[18][1]
        self.pinky_pip_y = self.lmList[18][2]

        self.pinky_dip_x = self.lmList[19][1]
        self.pinky_dip_y = self.lmList[19][2]

        self.pinky_tip_x = self.lmList[20][1]
        self.pinky_tip_y = self.lmList[20][2]

        return

# pas une méthode d'instance (statique ou pas dans une class)
def ligne(img, lmList1, a, lmList2, b, draw=True):
        # Point a et b
        coord_a = (lmList1[a][1], lmList1[a][2])
        coord_b = (lmList2[b][1], lmList2[b][2])

        # Milieu entre a et b
        coord_ab = milieu(coord_a, coord_b)

        if draw:
            cv2.line(img, coord_a, coord_b, vert, 2)  # Ligne entre a et b
            cv2.circle(img, coord_a, 6, rouge, -1)    # Point a
            cv2.circle(img, coord_b, 6, bleu, -1)     # Point b
            cv2.circle(img, coord_ab, 5, magenta, -1) # Point entre a et b

        return coord_a, coord_b

# Trouve le milieu entre 2 points
def milieu(coord_a, coord_b):
    return (coord_a[0] + coord_b[0])//2, (coord_a[1] + coord_b[1])//2

# Valeur abs car distance
def distance_calcul(lmList1, a, lmList2, b):
    distance = math.sqrt((lmList1[a][1]-lmList2[b][1])**2+(lmList1[a][2]-lmList2[b][2])**2)
    return abs(distance)
    
def main():
    url = 'https://nexus.avermedia.com/CamEngine/index.html'
    cap = cv2.VideoCapture(url)

    pTime = 0
    cTime = 0

    detector = handDetector()

    while True:
        success, img = cap.read()
        if not success:
            print("Erreur de capture vidéo")
            break

        img = cv2.flip(img, 1) # Flip horizontal de la vidéo

        #############################
        # DEBUT DE ZONE DE TEST

        hands, img = detector.findHands(img)
        lmList, label = detector.findPosition(img=img, handNo=0)

        # Test
        if lmList:
            Main = hand(lmList, label)
            if Main.is_thumb_unfolded(lmList):
                print("pouce déplié")
            else:
                print("pouce plié")

        # FIN DE ZONE DE TEST
        #############################

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10,50), police, 3, noir, 3, cv2.LINE_AA)

        cv2.imshow("Image", img)

        # Attendre 1 ms pour vérifier si une touche a été pressée
        key = cv2.waitKey(1) & 0xFF

        # Si la touche ESC (code 27) ou la touche 'q' est pressée, quitter la boucle
        if key == 27 or key == ord('q'):
            break

        # Vérifier si la fenêtre a été fermée
        if cv2.getWindowProperty('Image', cv2.WND_PROP_VISIBLE) < 1:
            break

        cv2.waitKey(1)

    # Libérer les ressources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()