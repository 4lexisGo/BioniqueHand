import cv2
import time
import os

import HandTrackingModule as htm
from EmetteurCommandeServoPython import ArduinoController

carte = ArduinoController(port='COM4', baudrate=9600)
moteurs = carte.control_servos

carte2 = ArduinoController(port='COM3', baudrate=9600)
moteurs2 = carte2.control_servos2

cap = cv2.VideoCapture(1)

wCam = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 640
hCam = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # 480

#print("Largeur :", wCam)
#print("Hauteur :",hCam)

pTime = 0
cTime = 0

detector = htm.handDetector()

# Sélection affichage
ligne_droite = False # Trace une ligne sur la main droite
rect_droite = True  # Trace un rectangle autour de la main droite
ligne_gauche = False # Trace une ligne sur la main gauche
rect_gauche = False  # Trace un rectangle autour de la main gauche
ligne_both = False   # Trace une ligne entre les 2 mains
emote = True         # Affiche les images correspondantes aux signes de la main
count = False         # Compte le nombre de doigts levés sur les 2 mains

track_droite = True

# Point pour la distance sur main droite
a1 = 4
b1 = 8

# Point pour la distance entre gauche et droite
a2 = 20
b2 = 20

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

# Pour affichage nombre de doigts
folderPath = "Images/Fingers"
dirList = os.listdir(folderPath)
overlayListFingerRight = []
overlayListFingerLeft = []
for imgPath in dirList:
    image = cv2.imread(f'{folderPath}/{imgPath}')
    image_resized = cv2.resize(image, (50, 100))
    overlayListFingerRight.append(image_resized)
    image_flip = cv2.flip(image_resized, 1)
    overlayListFingerLeft.append(image_flip)
# Inversion d'image pour le poing fermé
image_a_inverser = 6 - 1 # -1 pour la liste
overlayListFingerLeft[image_a_inverser], overlayListFingerRight[image_a_inverser] = overlayListFingerRight[image_a_inverser], overlayListFingerLeft[image_a_inverser]

# Pour affichage emote pouce
folderPath = "Images/Thumbs"
dirList = os.listdir(folderPath)
overlayListThumbLeft = []
overlayListThumbRight = []
for imgPath in dirList:
    image = cv2.imread(f'{folderPath}/{imgPath}')
    image_resized = cv2.resize(image, (100, 100))
    overlayListThumbLeft.append(image_resized)
    image_flip = cv2.flip(image_resized, 1)
    overlayListThumbRight.append(image_flip)


totalFingers, totalFingers_L, totalFingers_R = 0, 0, 0

# Boucle principale
while True:
    success, img = cap.read()
    if not success:
        print("Erreur de capture vidéo")
        break

    img = cv2.flip(img, 1) # Flip horizontal de la vidéo

    hands, img = detector.findHands(img)

    if hands:
        lmList1, label1 = detector.findPosition(img, draw=False, handNo=0)
    else:
        lmList1, label1 = [], ""
        
    if len(hands) == 2:
        lmList2, label2 = detector.findPosition(img, draw=False, handNo=1)
    else:
        lmList2, label2 = [], ""
        if label1:
            if label1 == "Right":
                label1 = "Left"
            elif label1 == "Left":
                label1 = "Right"
    # Simplifier les manipulations de label
    # Premiere inversion dans findPosition
    # Puis le reste ici, pas satisfait
    if label1 == "Right":
        lmListDroite = lmList1
        lmListGauche = lmList2
    elif label1 == "Left":
        lmListDroite = lmList2
        lmListGauche = lmList1
    else:
        lmListDroite = []
        lmListGauche = []


    # Début script main gauche
    if lmListGauche:
        mainGauche = htm.hand(lmListGauche, "Gauche")
        pt_sup_gauche, pt_inf_droite = mainGauche.boite(img, rect_gauche)
        mainGauche.handedness_printing(img, pt_sup_gauche, pt_inf_droite)

        if emote:
            if mainGauche.is_emote_thumb_up():
                #cv2.putText(img, "Pouce en haut", (10,hCam-10), police, 1, noir, 1)
                img[0:100, 100:200] = overlayListThumbLeft[1]

                totalFingers_L = 1
            elif mainGauche.is_emote_thumb_down():
                #cv2.putText(img, "Pouce en bas", (10,hCam-10), police, 1, noir, 1)
                img[0:100, 100:200] = overlayListThumbLeft[0]

                totalFingers_L = 0
            else:
                totalFingers_L = mainGauche.doigts_up().count(1)
                if mainGauche.doigts_up():
                    img[0:100, 100:150] = overlayListFingerLeft[totalFingers_L - 1]
    else:
        totalFingers_L = 0
    
        
    # Début script main droite
    if lmListDroite:
        mainDroite = htm.hand(lmListDroite, "Droite")

        if ligne_droite:
            coord_a, coord_b, coord_ab = htm.ligne(img, lmListDroite, a1, lmListDroite, b1, ligne_droite)

        pt_sup_gauche, pt_inf_droite = mainDroite.boite(img, rect_droite)
        mainDroite.handedness_printing(img, pt_sup_gauche, pt_inf_droite)

        if track_droite:
            contour1 = 0.3
            contour2 = 0.2
            coeff1 = 70
            coeff2 = 30
            m1, i1, m2, i2 = 0, 0, 0, 0
            if pt_sup_gauche[0] < contour1*wCam:
                m1 = 1
                i1 = int((contour1 - pt_sup_gauche[0]/wCam) * coeff1)
            if pt_inf_droite[0] > (1-contour1)*wCam:
                m1 = 2
                i1 = int((pt_inf_droite[0]/wCam - (1 - contour1)) * coeff1)
            if pt_sup_gauche[1] < contour2*hCam:
                m2 = 1
                i2 = int((contour2 - pt_sup_gauche[1]/hCam) * coeff2)
            if pt_inf_droite[1] > (1-contour2)*hCam:
                m2 = 2
                i2 = int((pt_inf_droite[1]/hCam - (1 - contour2)) * coeff2)
            #if m1 != 0 or m2 != 0:
            #    print(m1, i1, m2, i2)
            moteurs(m1, i1, m2, i2)

            # Bornes en pixels
            x_g = int(contour1 * wCam)              # marge gauche
            x_d = int((1 - contour1) * wCam)        # marge droite
            y_h = int(contour2 * hCam)              # marge haute
            y_b = int((1 - contour2) * hCam)        # marge basse

            # Rectangle "zone autorisée" (entre les marges)
            cv2.rectangle(img, (x_g, y_h), (x_d, y_b), (0, 200, 0), 2)

            # (Optionnel) étiquette
            cv2.putText(img, "Zone", (x_g + 10, y_h - 10), police, 2, (0, 200, 0), 2)

        if emote:
            if mainDroite.is_emote_thumb_up():
                #text_size = cv2.getTextSize("Pouce en haut", police, 1, 1)[0]
                #cv2.putText(img, "Pouce en haut", (wCam-text_size[0]-10,hCam-10), police, 1, noir, 1)
                img[0:100, 540:640] = overlayListThumbRight[1]

                totalFingers_R = 1

                moteurs2(2, 20, 0, 0, 0, 0)

            elif mainDroite.is_emote_thumb_down():
                #text_size = cv2.getTextSize("Pouce en bas", police, 1, 1)[0]
                #cv2.putText(img, "Pouce en bas", (wCam-text_size[0]-10,hCam-10), police, 1, noir, 1)
                img[0:100, 540:640] = overlayListThumbRight[0]

                totalFingers_R = 0

                moteurs2(1, 20, 0, 0, 0, 0)
            else:
                totalFingers_R = mainDroite.doigts_up().count(1)
                if mainDroite.doigts_up():
                    img[0:100, 590:640] = overlayListFingerRight[totalFingers_R - 1]
                moteurs2(0, 0, 0, 0, 0, 0)
        else:
            moteurs2(0, 0, 0, 0, 0, 0)
    else:
        totalFingers_R = 0
        m1, i1, m2, i2 = 0, 0, 0, 0
        moteurs(m1, i1, m2, i2)

    # Début script double main
    if lmListGauche and lmListDroite:
        if ligne_both:
            coord_a, coord_b, coord_ab = htm.ligne(img, lmListGauche, a2, lmListDroite, b2, ligne_both)
    if count:
        totalFingers = totalFingers_L + totalFingers_R
        cv2.putText(img, str(totalFingers), (300, 19+15), police, 2, noir, 2)
    # Calcul des fps
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    # Ecriture des fps
    police_taille_fps = 2
    police_epaisseur_fps = 2
    #text_size = cv2.getTextSize(str(int(fps)), police, police_taille_fps, police_epaisseur_fps)[0]
    #print(text_size) # 19
    cv2.putText(img, str(int(fps)), (10, 19+15), police, police_taille_fps, noir, police_epaisseur_fps)

    # Affichage de l'image
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
carte.close