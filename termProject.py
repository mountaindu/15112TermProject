import pygame
import random
import math
import copy
import pygame.gfxdraw
import pickle
import os

# Manual box spawn off
# Add Quit 


class ArenaGame(object):

    def __init__(self):
        # Initializing values
        self.width = 700
        self.height = 600

        self.initLevels()
        
        self.screen = pygame.display.set_mode([self.width, self.height])
        self.background = pygame.Surface(self.screen.get_size())
        self.done = False
        self.platform_list = pygame.sprite.Group()
        self.all_sprite_list = pygame.sprite.Group()
        self.clock = pygame.time.Clock()

        (self.x, self.y) = (0, 0)

        
        # Set the current level
        self.copyLevelList = copy.deepcopy(self.levelList)
        self.currentLevelNum = 0
        self.currentLevel = self.levelList[self.currentLevelNum]
        self.levelPlatforms = self.currentLevel.platformList
        self.xDiff = 0

        # Creating weapons and crates
        self.boxList = pygame.sprite.Group()
        self.bulletList1 = pygame.sprite.Group()
        self.bulletList2 = pygame.sprite.Group()
        self.player1Weapon = pygame.sprite.Group()
        self.player2Weapon = pygame.sprite.Group()

        # Start on starting screen
        self.startMenu = True
        self.gamePlay = False
        self.levelEditor = False
        self.preGameMenu = False
        self.instructionsMenu = False
        self.colorMenu = False
        self.paused = False

        # Initializing Weapons
        self.initWeapons()

        self.p1Weapon = Weapon(self.gunSS.image_at((238, 178, 38, 28)), 
                               "ASP", 12, 10, 20)
        self.p2Weapon = Weapon(self.gunSS.image_at((238, 178, 38, 28)), 
                               "ASP", 12, 10, 20)

        # Creating players
        self.p1Color = (255, 255, 255)
        self.p2Color = (255, 255, 255)
        self.playerList = pygame.sprite.Group()
        self.player1 = Blob(self.width, self.height, self.currentLevel, 
                            self.boxList, self.p1Weapon, self.p1Color)
        self.player2 = Blob(self.width, self.height, self.currentLevel, 
                            self.boxList, self.p2Weapon, self.p2Color)
        self.playerList.add(self.player1, self.player2)

        self.player1Weapon.add(self.player1.weapon)
        self.player2Weapon.add(self.player2.weapon)

        # Initializing Game Setup
        self.initGame()
        

        # Map Creator
        self.newMap = []
        self.mapName = "Untitled"
        (self.LM_startX, self.LM_startY) = (None, None)

        

    def initGame(self):
        
        # Game Setup
        self.killLimit = "10"
        self.gameOver = False
        self.paused = False

        


    def initLevels(self):
        # StartX, StartY, Width, Height
        if os.path.isfile("levels.pkl"):
            self.levelList = []
            with open("levels.pkl", "rb") as f:
                tempList = pickle.load(f)
            for level in tempList:
                self.levelList.append(GameLevel(level.level, level.name))



        
        else:
            # Creates level file with basic levels if the file does not exist
            self.levelList = []
            level1 = GameLevel([[200, 200, 200, 60], [50, 400, 700, 60], 
                                [500, 100, 60, 200]], "Arena")
            level2 = GameLevel([[400, 500, 210, 70],
                     [100, 400, 210, 70],
                     [400, 200, 70, 210],
                     ], "Agility")
            level3 = GameLevel([[50, 600, 700, 60], [70, 400, 600, 60], 
                               [300, 250, 60, 210], [70, 150, 240, 60], 
                               [450, 180, 250, 40], [850, 250, 70, 250], 
                               [800, 200, 160, 70]], "Battlefield")
            level4 = GameLevel([[111, 197, 17, 245], [156, 196, 159, 14], 
                                [155, 197, 16, 112], [155, 296, 161, 17], 
                                [303, 297, 15, 151], [155, 431, 161, 17], 
                                [342, 314, 41, 18], [400, 195, 17, 253], 
                                [481, 195, 16, 254], [550, 196, 162, 13], 
                                [704, 197, 11, 128], [551, 311, 154, 14], 
                                [551, 324, 14, 128], [552, 435, 163, 17], 
                                [100, 519, 646, 13]], "15112")


            self.levelList = [level1, level2, level3, level4]

            with open("levels.pkl", "wb") as f:
                pickle.dump(self.levelList, f, -1)


        

    def run(self):
        # Initializing Menus
        pygame.init()
        pygame.display.set_caption('SMO Arena')
        self.all_sprite_list.add(self.player1, self.player2)
        self.SM = StartMenu(self.screen, self.width, self.height)
        self.GM = GameMenu(self.screen, self.width, self.height, self.p1Weapon, 
                           self.p2Weapon, self.killLimit)
        self.PG = PreGameMenu(self.screen, self.width, self.height, 
                              self.levelList, (200,200,200), (200, 200, 200), 
                              self.killLimit)
        self.LM = LevelEditorMenu(self.screen, self.width, self.height, 
                                  self.mapName)
        self.IM = InstructionMenu(self.screen, self.width, self.height)
        self.CM = ColorMenu(self.screen, self.width, self.height)

        # Counts amount of actions
        self.timeCounter = 0

        while not self.done:
            self.timeCounter += 1

            self.randNum = (randomNum(self.currentLevel.platformXCoordinates())+
                           self.currentLevel.XLevelShift)
            self.lowestPlat = self.currentLevel.lowestPlatX()
            
            # Finds mouse position, mouse pressed, and key pressed 
            (self.x, self.y) = pygame.mouse.get_pos()
            (self.p1, self.p2, self.p3) = pygame.mouse.get_pressed()
            self.pressedKeys = pygame.key.get_pressed()

            # Changes Game Stage based on state
            if self.gamePlay == True:
                self.GP_Wrapper()

            elif self.preGameMenu == True:
                self.PG_Wrapper()
                
            elif self.startMenu == True:
                self.SM_Wrapper()

            elif self.levelEditor == True:
                self.LM_Wrapper()

            elif self.instructionsMenu == True:
                self.IM_Wrapper()

            elif self.colorMenu == True:
                self.CM_Wrapper()

            # Setting FPS Limit 
            self.clock.tick(40)
            self.drawFPS()

            pygame.display.update()

            

        pygame.quit()

    def GP_Wrapper(self):
        # Main gameplay function

        # Sets player shooting once to false
        self.p1SingleShot = False
        self.p2SingleShot = False
        
        # Game being played 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.GM_changeGameState()
                
            self.GP_OnKeyPressed(event)

        # Controls for players
        self.player1.decreaseCooldown()
        self.player2.decreaseCooldown()
        self.GP_player1Controls()
        self.GP_player2Controls()

        # Stops playing if game is paused or game is over
        if (self.paused == False) and (self.gameOver == False):
            # Updates all sprite sheets
            self.all_sprite_list.update()
            self.currentLevel.update()
            self.player1Weapon.update()
            self.player2Weapon.update()
            self.bulletList1.update()
            self.bulletList2.update()
            self.boxList.update()

        
        self.GM_enlargeText()
        self.GP_randomBoxSpawn()
        self.GP_checkHitBox()
        self.GP_bulletHitPlat()
        self.GP_bulletHitPlayer()
        self.GP_checkWeapon()

        self.player1.giveWeapon(self.p1Weapon)
        self.player2.giveWeapon(self.p2Weapon)
            
            
        # Drawing everything on screen
        self.currentLevel.draw(self.screen)
        self.boxList.draw(self.screen)
        self.all_sprite_list.draw(self.screen)
        self.GP_drawPointers()
        self.player1Weapon.draw(self.screen)
        self.player2Weapon.draw(self.screen)
        self.bulletList1.draw(self.screen)
        self.bulletList2.draw(self.screen)
        self.GP_playerLabels()

        self.GP_middleCoordinates()
        self.GP_offset()

        self.GMStatus()
        self.GM.update()

    def PG_Wrapper(self):
        # preGame Menu status
        self.PG.lColor = (200, 200, 200)
        self.PG.rColor = (200, 200, 200)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.PG_changeGameState()
            self.PG_changeMap(event)
        
            self.PG_OnKeyPressed(event)
            self.PG_killLimitInput(event)

        self.PG_enlargeText()
        self.PG.update()

    def SM_Wrapper(self):
        # Starting menu status

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True

            self.SM_enlargeText()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.SM.buttonList:
                    if button.rect.collidepoint(self.x, self.y):
                        self.SM_changeGameState(button)

        self.SM.update()

    def LM_Wrapper(self):
        # Menu for editing levels

        if (self.pressedKeys[pygame.K_LSHIFT] or 
            self.pressedKeys[pygame.K_RSHIFT]):
            # Deletes platform when Shift is held down
            self.deleting = True

            if self.p1 == 1:
                delX, delY = pygame.mouse.get_pos()
                self.LM.removePlat(delX, delY)
        else:
            self.deleting = False



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
                
            if not self.deleting:
                # Creates platforms when shift is not pressed 
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.LM_startX, self.LM_startY = pygame.mouse.get_pos()
                    self.LM_changeGameState()


                elif event.type == pygame.MOUSEBUTTONUP:
                    endX, endY = pygame.mouse.get_pos()
                    if (self.LM_startX != None) and (self.LM_startY != None):
                    # Checking for when first starting level editor menu
                        plat = self.LM_createPlat(self.LM_startX,self.LM_startY, 
                                                  endX, endY)
                        if plat != None:
                            self.LM.rectList.append(plat)


            self.LM_mapNameInput(event)

        self.LM_enlargeText()
        self.LM_scroll()

        self.LM.update()

        if not self.deleting:
            # Draws platform based on mouse position
            if self.p1 == 1:
                currentX, currentY = pygame.mouse.get_pos()
                if (self.LM_startX != None) and (self.LM_startY != None):
                    # Checking for when first starting level editor menu
                    self.LM_drawPlatform(self.LM_startX, self.LM_startY, 
                                         currentX, currentY)


    def IM_Wrapper(self):
        # Menu for instructions

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.IM_changeGameState()

        self.IM_enlargeText()
        self.IM.update()


    def CM_Wrapper(self):
        # Menu for instructions

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                #(x, y) = pygame.mouse.get_pos()
                self.CM_changeGameState()
                self.CM_changeSliderPosition()

            

        self.CM_getPlayerColor()


        self.CM_enlargeText()
        self.CM.update()




    def GP_offset(self):
        # Moves the screen based on players locations
        # Checks if rect is past a certain point, if it is, move all platforms
        # and sprites for every distance the rect moves past that point
        self.hOffset = 250


        # Horizontal offset
        if self.middleX >= self.width - self.hOffset:
            self.xDiff = -(self.middleX - (self.width - self.hOffset))
            self.player1.rect.right += self.xDiff
            self.player2.rect.right += self.xDiff
            self.currentLevel.xShift(self.xDiff)
            for box in self.boxList:
                box.rect.x += self.xDiff
            for bullet in self.bulletList1:
                bullet.rect.x += self.xDiff
            for bullet in self.bulletList2:
                bullet.rect.x += self.xDiff

            
        if self.middleX <= self.hOffset + 50:
            self.xDiff = self.hOffset + 50 - self.middleX
            self.player1.rect.right += self.xDiff
            self.player2.rect.right += self.xDiff
            self.currentLevel.xShift(self.xDiff)

            for box in self.boxList:
                box.rect.x += self.xDiff
            for bullet in self.bulletList1:
                bullet.rect.x += self.xDiff
            for bullet in self.bulletList2:
                bullet.rect.x += self.xDiff


        # Vertical offset
        if self.middleY >= self.height/2 + 50:

            self.yDiff = -(self.middleY - (self.height/2 + 50))
            self.player1.rect.bottom += self.yDiff
            self.player2.rect.bottom += self.yDiff
            self.currentLevel.yShift(self.yDiff)

            for box in self.boxList:
                box.rect.y += self.yDiff
            for bullet in self.bulletList1:
                bullet.rect.y += self.yDiff
            for bullet in self.bulletList2:
                bullet.rect.y += self.yDiff


        if self.middleY <= 150:

            self.yDiff = 150 - self.middleY
            self.player1.rect.bottom += self.yDiff
            self.player2.rect.bottom += self.yDiff
            self.currentLevel.yShift(self.yDiff)

            for box in self.boxList:
                box.rect.y += self.yDiff
            for bullet in self.bulletList1:
                bullet.rect.y += self.yDiff
            for bullet in self.bulletList2:
                bullet.rect.y += self.yDiff


    
    def GP_playerDying(self):
        # Checks if a player (or both) is below the level
        topLimit = self.currentLevel.highestPlatX() - 250

        if (self.player1.rect.bottom >= self.lowestPlat) or (
            self.player1.rect.bottom <= topLimit) and(
            self.player2.rect.bottom >= self.lowestPlat) or (
            self.player2.rect.bottom <= topLimit):
            return 0

        elif (self.player1.rect.bottom >= self.lowestPlat) or (
              self.player1.rect.bottom <= self.currentLevel.highestPlatX()-250):
            return 1

        elif (self.player2.rect.bottom >= self.lowestPlat) or (
              self.player2.rect.bottom <= self.currentLevel.highestPlatX()-250):
            return 2

    def GP_playerLabels(self):
        # Draws the player label text
        textSize = 18
        labelFont = pygame.font.SysFont("arial bold", textSize) 
        label1 = labelFont.render("Player 1" , 1, (255,255,255))
        label2 = labelFont.render("Player 2" , 1, (255,255,255))

        self.screen.blit(label1, (self.player1.rect.x, self.player1.rect.y-20))
        self.screen.blit(label2, (self.player2.rect.x, self.player2.rect.y-20))

    def GP_middleCoordinates(self):
        # Determines coordinates to act as middle for map offset
        self.middleX = (self.player1.rect.right + self.player2.rect.right)/2
        self.middleY = (self.player1.rect.bottom + self.player2.rect.bottom)/2

        if self.GP_playerDying() == 0:

            levelMidX = (self.currentLevel.rightestPlat() + 
                         self.currentLevel.leftestPlat())/2
            levelMidY = (self.currentLevel.highestPlatX() + 
                         self.currentLevel.lowestPlatX())/2

            self.middleX = levelMidX
            self.middleY = levelMidY


        elif self.GP_playerDying() == 1:
            self.middleX = self.player2.rect.right
            self.middleY = self.player2.rect.bottom

        elif self.GP_playerDying() == 2:
            self.middleX = self.player1.rect.right
            self.middleY = self.player1.rect.bottom

        else:
            self.middleX = (self.player1.rect.right+self.player2.rect.right)/2
            self.middleY = (self.player1.rect.bottom+self.player2.rect.bottom)/2

        
                



    def GP_OnKeyPressed(self, event):
        # Responds to key pressed or release
        

        if event.type == pygame.KEYDOWN:
            
            # Pausing game
            if not self.gameOver:
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                    self.GM.paused = self.paused

        self.GP_singleShot(event)


    def GP_singleShot(self, event):
        # When firing a single shot
        if event.type == pygame.KEYUP:

            # Player 1 shooting
            if (event.key==pygame.K_BACKSLASH) and (self.player1.cooldown==0):
                self.player1.resetCooldown()
                self.p1SingleShot = True

                (x, y) = self.player1.weaponCoordinates()
                self.bulletList1.add(Bullet(x, y, self.player1.direction))
                self.player1.shoot()

            # Player 2 shooting
            if (event.key == pygame.K_SPACE) and (self.player2.cooldown == 0):
                self.player2.resetCooldown()
                self.p2SingleShot = True

                (x, y) = self.player2.weaponCoordinates()
                self.bulletList2.add(Bullet(x, y, self.player2.direction))
                self.player2.shoot()



    def GP_player1Controls(self):
        # Controls for player 1
        
        # Moves based on what direction pressed
        
        if self.pressedKeys[pygame.K_LEFT]:
            self.player1.moveLeft()
        
        elif self.pressedKeys[pygame.K_RIGHT]:
            self.player1.moveRight()

        if self.pressedKeys[pygame.K_UP]:
            self.player1.jump()

        elif self.pressedKeys[pygame.K_DOWN]:
            self.player1.moveDown()

        if self.p1SingleShot == False:
            if self.pressedKeys[pygame.K_BACKSLASH]:
                if self.timeCounter % self.player1.weapon.fireRate == 0:
                    (x, y) = self.player1.weaponCoordinates()
                    self.bulletList1.add(Bullet(x, y, self.player1.direction))
                    self.player1.shoot()



        # Checks when key is not bring pressed
        if not self.pressedKeys[pygame.K_LEFT] and self.player1.dX < 0:
            self.player1.stop()
        elif not self.pressedKeys[pygame.K_RIGHT] and self.player1.dX > 0:
            self.player1.stop()

    def GP_player2Controls(self):
        # Controls for player 2


        # Moves based on what direction pressed
        if self.pressedKeys[pygame.K_a]:
            self.player2.moveLeft()

        elif self.pressedKeys[pygame.K_d]:
            self.player2.moveRight()

        if self.pressedKeys[pygame.K_w]:
            self.player2.jump()

        elif self.pressedKeys[pygame.K_s]:
            self.player2.moveDown()

        if self.p2SingleShot == False:
            if self.pressedKeys[pygame.K_SPACE]:
                if self.timeCounter % self.player2.weapon.fireRate == 0:
                    (x, y) = self.player2.weaponCoordinates()
                    self.bulletList2.add(Bullet(x, y, self.player2.direction))
                    self.player2.shoot()



        if not self.pressedKeys[pygame.K_a] and self.player2.dX < 0:
            self.player2.stop()

        elif not self.pressedKeys[pygame.K_d] and self.player2.dX > 0:
            self.player2.stop()

    def GP_checkWeapon(self):
        # Check is weapon has anymore ammo, give pistol if not
        if self.player1.weapon.ammo == 0:
            self.player1.weapon.resetAmmo()
            self.player1Weapon.empty()
            self.p1Weapon = Weapon(self.gunSS.image_at((238, 178, 38, 28)), 
                                   "ASP", 12, 10, 20)
            self.player1Weapon.add(self.p1Weapon)

        if self.player2.weapon.ammo == 0:
            self.player2.weapon.resetAmmo()
            self.player2Weapon.empty()
            self.p2Weapon = Weapon(self.gunSS.image_at((238, 178, 38, 28)), 
                                   "ASP", 12, 10, 20)
            self.player2Weapon.add(self.p2Weapon)

    def drawFPS(self):
        # Draws FPS Counter
        myFont = pygame.font.SysFont(None, 20)

        speed = myFont.render("FPS %d" % self.clock.get_fps(), 1, (255,255,255))
        self.screen.blit(speed, (0, self.height - 30))


    def GP_checkHitBox(self):
        # Deletes box if a player hits it and gives player a weapon

        if len(pygame.sprite.spritecollide(self.player1,self.boxList,True))==1:
            # Resets gun ammo
            self.player1.weapon.resetAmmo()
            # No flash when gun reset
            self.player1.weapon.rect.x = -10000

            # Gives player random weapon 
            self.player1Weapon.empty()
            self.p1Weapon = random.choice(self.weaponList1)
            self.player1Weapon.add(self.p1Weapon)


        elif len(pygame.sprite.spritecollide(self.player2, 
                                             self.boxList, True)) == 1:

            self.player2.weapon.resetAmmo()
            self.player2.weapon.rect.x = -10000

            self.player2Weapon.empty()
            self.p2Weapon = random.choice(self.weaponList2)
            self.player2Weapon.add(self.p2Weapon)


    def GP_bulletHitPlat(self):
        # Removes bullet if it hits a platform
        pygame.sprite.groupcollide(self.bulletList1, 
                                  self.levelPlatforms, True, False)
        pygame.sprite.groupcollide(self.bulletList2, 
                                   self.levelPlatforms, True, False)

        # Kills bullets if they go off the edge of the map
        for bullet in self.bulletList1:
            if bullet.rect.x <= 0 or bullet.rect.x >= self.width:
                bullet.remove()
                bullet.kill()

        for bullet in self.bulletList2:
            if bullet.rect.x <= 0 or bullet.rect.x >= self.width:
                bullet.remove()
                bullet.kill()

    def GP_randomBoxSpawn(self):
        # Spawns box randomly 
        randNum = random.randint(250, 300)

        # Spawns box when time is divisible by the random number
        if self.timeCounter % randNum == 0:
            newBox = Box(self.width, self.height,self.currentLevel,self.randNum)
            self.boxList.add(newBox)
             


    def GP_bulletHitPlayer(self):
        # Checks if a player is hit by a bullet

        player1Hit = len(pygame.sprite.spritecollide(self.player1, 
                                                     self.bulletList2, True))
        player2Hit = len(pygame.sprite.spritecollide(self.player2, 
                                                     self.bulletList1, True))

        # Changes the rect of the player based on weapon power
        if player1Hit > 0:
            p2WeaponPower = self.player2.weapon.power

            if self.player2.direction == "RIGHT":
                self.player1.dX += p2WeaponPower
            else:
                self.player1.dX -= p2WeaponPower

        if player2Hit > 0:
            p1WeaponPower = self.player1.weapon.power

            if self.player1.direction == "RIGHT":
                self.player2.dX += p1WeaponPower
            else:
                self.player2.dX -= p1WeaponPower

    def GP_drawPointers(self):
        # Draws pointers to blob location when off map vertically
        textSize = 14
        pointerFont = pygame.font.SysFont("arial bold", textSize) 

        # Determines x position of pointer based on blobs position
        # Draws triangle at top or bottom of screen, depending on position
        if self.player1.rect.bottom <= 0:
            x1 = self.player1.rect.x 
            distance1 = self.player1.rect.bottom
            # Makes sure pointer is on screen
            if x1 <= 50: x1 = 50
            elif x1 >= self.width - 50: x1 = self.width - 50

            # Draws the triangle
            pygame.gfxdraw.aatrigon(self.screen, x1, 50, x1 + 40, 50, 
                                    x1 + 20, 10, (self.player1.color))
            pygame.gfxdraw.filled_trigon(self.screen, x1, 50, x1 + 40, 50, 
                                    x1 + 20, 10, (self.player1.color))
            # Draws the distance text
            pointer1 = pointerFont.render("%d" % distance1, 1, (0,0,0))
            self.screen.blit(pointer1, (x1 + 10, 30))

        elif self.player1.rect.top >= self.height:
            x1 = self.player1.rect.x 
            distance1 = self.player1.rect.bottom
            if x1 <= 50: x1 = 50
            elif x1 >= self.width - 50: x1 = self.width - 50

            pygame.gfxdraw.aatrigon(self.screen, x1, self.height - 50, 
                                    x1 + 40, self.height - 50, x1 + 20, 
                                    self.height - 10, (self.player1.color))
            pygame.gfxdraw.filled_trigon(self.screen, x1, self.height - 50, 
                                    x1 + 40, self.height - 50, x1 + 20, 
                                    self.height - 10, (self.player1.color))
            pointer1 = pointerFont.render("%d" % distance1, 1, (0,0,0))
            self.screen.blit(pointer1, (x1 + 10, self.height - 40))


        if self.player2.rect.bottom <= 0:
            x2 = self.player2.rect.x
            distance2 = self.player2.rect.bottom
            if x2 <= 50: x2 = 50
            elif x2 >= self.width - 50: x2 = self.width - 50

            pygame.gfxdraw.aatrigon(self.screen, x2, 50, x2 + 40, 50, 
                                    x2 + 20, 10, (self.player2.color))
            pygame.gfxdraw.filled_trigon(self.screen, x2, 50, x2 + 40, 50, 
                                    x2 + 20, 10, (self.player2.color))
            pointer2 = pointerFont.render("%d" % distance2, 1, (0,0,0))
            self.screen.blit(pointer2, (x2 + 10, 30))


        elif self.player2.rect.top >= self.height:
            x2 = self.player2.rect.x 
            distance2 = self.player2.rect.bottom
            if x2 <= 50: x2 = 50
            elif x2 >= self.width - 50: x2 = self.width - 50

            pygame.gfxdraw.aatrigon(self.screen, x2, self.height - 50, 
                                    x2 + 40, self.height - 50, x2 + 20, 
                                    self.height - 10, (self.player2.color))
            pygame.gfxdraw.filled_trigon(self.screen, x2, self.height - 50, 
                                    x2 + 40, self.height - 50, x2 + 20, 
                                    self.height - 10, (self.player2.color))
            pointer2 = pointerFont.render("%d" % distance2, 1, (0,0,0))
            self.screen.blit(pointer2, (x2 + 10, self.height - 40))



    def GMStatus(self):
        # Checks if game is over
        self.gameOver = self.GM.checkGameOver()
        # Changes Status of in-game menu
        if self.gameOver:
            self.GM.gameOverText()

        if self.paused:
            self.GM.pause()

        # Adds score and gives user pistol when respawn
        if self.player1.respawn() == True:
            self.GM.addScore(2)
            self.p1Weapon = Weapon(self.gunSS.image_at((238, 178, 38, 28)), 
                                   "ASP", 12, 10, 20)
            self.player1Weapon.add(self.p1Weapon)

        elif self.player2.respawn() == True:
            self.GM.addScore(1)
            self.p2Weapon = Weapon(self.gunSS.image_at((238, 178, 38, 28)), 
                                   "ASP", 12, 10, 20)
            self.player2Weapon.add(self.p2Weapon)

        
        self.GM.changeP1Weapon(self.p1Weapon)
        self.GM.changeP2Weapon(self.p2Weapon)

    def GM_changeGameState(self):
        # Changes game state based on what button pressed
        if self.paused or self.gameOver:
            for button in self.GM.buttonList:
                if button.rect.collidepoint(self.x, self.y):
                    if button.buttonType() == "MAIN MENU":

                        self.gamePlay = False
                        self.startMenu = True

    def resetGame(self):
        # Resets game 
        self.initGame()
        self.GM.paused = self.paused
        self.GM.p1Score = 0
        self.GM.p2Score = 0

        
        self.boxList.empty()
        self.bulletList1.empty()
        self.bulletList2.empty()
        self.player1.weapon.rect.x = -10000
        self.player2.weapon.rect.x = -10000
        self.player1Weapon.empty()
        self.player2Weapon.empty()

        self.p1Weapon = Weapon(self.gunSS.image_at((238, 178, 38, 28)), 
                               "ASP", 12, 10, 20)
        self.p2Weapon = Weapon(self.gunSS.image_at((238, 178, 38, 28)), 
                               "ASP", 12, 10, 20)

        self.player1.giveWeapon(self.p1Weapon)
        self.player2.giveWeapon(self.p2Weapon)

        self.player1Weapon.add(self.p1Weapon)
        self.player2Weapon.add(self.p2Weapon)

        self.player1.dX = 0
        self.player1.dY = 0
        self.player2.dX = 0
        self.player2.dY = 0

    def GM_enlargeText(self):
        # Enlarges button text when hovering over
        textSize = 20

        for button in self.GM.buttonList:
            if button.rect.collidepoint(self.x, self.y) == True:
                button.changeTextSize(textSize + 2)  
            else:
                button.changeTextSize(textSize)


    def SM_enlargeText(self):
        # Enlarges button text when hovering over
        textSize = 25

        for button in self.SM.buttonList:
            if button.rect.collidepoint(self.x, self.y) == True:
                button.changeTextSize(textSize + 2)  
            else:
                button.changeTextSize(textSize)



    def SM_changeGameState(self, button):
        # Changes game state based on what button pressed
        
        if button.buttonType() == "NEW GAME":
            # Resets shift of the previous level
            self.currentLevel.resetShift()
            self.resetGame()
            self.startMenu = False
            self.preGameMenu = True

        elif button.buttonType() == "INSTRUCTIONS":
            self.startMenu = False
            self.instructionsMenu = True

        elif button.buttonType() == "LEVEL EDITOR":
            self.startMenu = False
            self.levelEditor = True

        elif button.buttonType() == "EDIT PROFILE":
            self.startMenu = False
            self.colorMenu = True

    def LM_drawPlatform(self, startX, startY, endX, endY):
        # Draws platform based on user input
        platformGray = (150, 150, 150)
        if (abs(endX - startX) * abs(endY - startY)) >= 100:
            pygame.draw.rect(self.screen, platformGray, 
                            [startX, startY, endX - startX, endY - startY], 0)


    def LM_createPlat(self, x1, y1, x2, y2):
        # Creates a platform with the given coordinates

        startX = min(x1, x2)
        startY = min(y1, y2)
        endX = max(x1, x2)
        endY = max(y1, y2)

        width = endX - startX
        height = endY - startY
        if (width * height) >= 100:
            return [startX, startY, width, height]
        else: return None

    def LM_mapNameInput(self, event):
        # Returns map name based on what user types

        if event.type == pygame.KEYDOWN:

            if len(self.LM.mapName) <= 12: 
                # Makes sure input is letter or number
                if event.unicode.isalpha():
                    self.LM.mapName += event.unicode
                elif event.unicode.isdigit():
                    self.LM.mapName += event.unicode

            if event.key == pygame.K_BACKSPACE:
                self.LM.mapName = self.LM.mapName[:-1]



    def LM_enlargeText(self):
        # Enlarges button text when hovering over
        textSize = 20

        for button in self.LM.buttonList:
            if button.rect.collidepoint(self.x, self.y) == True:
                button.changeTextSize(textSize + 2)  
            else:
                button.changeTextSize(textSize)

    def LM_changeGameState(self):
        # Changes game state based on what button pressed


        for button in self.LM.buttonList:
            if button.rect.collidepoint(self.x, self.y):
    
                if button.buttonType() == "MAIN MENU":
                    self.LM.rectList = []
                    self.LM.mapName = "Untitled"
                    self.levelEditor = False
                    self.startMenu = True

                elif button.buttonType() == "SAVE":
                    if len(self.LM.mapName) == 0:
                        self.LM.mapName = "Untitled" 

                    self.LM_addNewLevel()
                    self.levelEditor = False
                    self.startMenu = True
                        

    def LM_addNewLevel(self):
        # Adds new level to the file
        self.LM_adjustPlatforms()
        newLevel = GameLevel(self.LM.rectList, self.LM.mapName)

        # Adds to list
        self.levelList.append(newLevel)

        # Adds to file
        with open("levels.pkl", "wb") as f:
            pickle.dump(self.levelList, f, -1)


        # Resets screen and name
        self.LM.rectList = []
        self.LM.mapName = "Untitled"

    def LM_adjustPlatforms(self):
        # Adjusts platforms after drawing them so it is centered
        adjustedX = 200
        adjustedY = 200


        for platform in self.LM.rectList:
            startX = platform[0]
            startY = platform[1]
            minX = min(startX, adjustedX)
            minY = min(startY, adjustedY)
        
        if len(self.LM.rectList) > 0:
            scaleX = adjustedX - minX
            scaleY = adjustedY - minY

        for platform in self.LM.rectList:
            platform[0] += scaleX
            platform[1] += scaleY
         

    def LM_scroll(self):
        # Scrolls platforms based on direction pressed
        if self.pressedKeys[pygame.K_LEFT]:
            self.LM_horizontalScroll(5)
        
        elif self.pressedKeys[pygame.K_RIGHT]:
            self.LM_horizontalScroll(-5)

        if self.pressedKeys[pygame.K_UP]:
            self.LM_verticalScroll(5)

        elif self.pressedKeys[pygame.K_DOWN]:
            self.LM_verticalScroll(-5)

    def LM_horizontalScroll(self, num):
        # Scrolls platforms horizontally
        if len(self.LM.rectList) > 0:
            for platform in self.LM.rectList:
                platform[0] += num

    def LM_verticalScroll(self, num):
        # Scrolls platforms vertically
        if len(self.LM.rectList) > 0:
            for platform in self.LM.rectList:
                platform[1] += num


    def PG_enlargeText(self):
        # Enlarges button text when hovering over
        textSize = 20

        for button in self.PG.buttonList:
            if button.rect.collidepoint(self.x, self.y) == True:
                button.changeTextSize(textSize + 2)  
            else:
                button.changeTextSize(textSize)

    def PG_changeGameState(self):
        # Changes game state based on what button pressed

        for button in self.PG.buttonList:
            if button.rect.collidepoint(self.x, self.y):
                
                if button.buttonType() == "MAIN MENU":
                    self.preGameMenu = False
                    self.startMenu = True

                elif button.buttonType() == "START":
                    index = self.PG.index
                    self.currentLevel = self.levelList[index]

                    self.player1.level = self.currentLevel
                    self.player2.level = self.currentLevel

                    self.player1.adjustStart()
                    self.player2.adjustStart()

                
                    self.levelPlatforms = self.currentLevel.platformList
                    self.GM.killLimit = self.killLimit

                    self.preGameMenu = False
                    self.gamePlay = True


    def PG_killLimitInput(self, event):
        # Changes kill limit based on user input

        if event.type == pygame.KEYDOWN:

            if len(self.killLimit) <= 2: 
                # Makes sure user input is a digit
                if event.unicode.isdigit():
                    self.killLimit += event.unicode

            # Deletes when backspace is pressed
            if event.key == pygame.K_BACKSPACE:
                self.killLimit = self.killLimit[:-1]

        self.PG.kills = self.killLimit




    def PG_OnKeyPressed(self, event):
        # Events when key is pressed on preGame menu
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_LEFT:
                # Shifts level and changes button color
                self.PG.levelIndex += 1
                self.PG.lButton.changeColor((1,1,1))

            elif event.key == pygame.K_RIGHT:
                # Shifts level and changes button color
                self.PG.levelIndex -= 1
                self.PG.rButton.changeColor((1,1,1))

        elif event.type == pygame.KEYUP:
            # Changes button color when let go 
            for button in self.PG.tButtonList:
                button.changeColor((200,200,200))

    def PG_changeMap(self, event):
        # Changes map based on mouse press
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.PG.tButtonList:
                if button.rect.collidepoint(self.x, self.y) == True:
                    # Changes button color to black
                    button.changeColor((1,1,1))

                    if button.direction == "LEFT": self.PG.levelIndex += 1
                    elif button.direction == "RIGHT": self.PG.levelIndex -= 1

        elif event.type == pygame.MOUSEBUTTONUP:
            for button in self.PG.tButtonList:
                # Changes button color when let go 
                button.changeColor((200,200,200))

                
    def IM_enlargeText(self):
        # Enlarges button text when hovering over
        textSize = 20

        for button in self.IM.buttonList:
            if button.rect.collidepoint(self.x, self.y) == True:
                button.changeTextSize(textSize + 2)  
            else:
                button.changeTextSize(textSize)

    def IM_changeGameState(self):
        # Changes game state based on what button pressed

        for button in self.IM.buttonList:
            if button.rect.collidepoint(self.x, self.y):
                
                if button.buttonType() == "MAIN MENU":
                    self.instructionsMenu = False
                    self.startMenu = True



    def CM_enlargeText(self):
        # Enlarges button text when hovering over
        textSize = 20

        for button in self.CM.buttonList:
            if button.rect.collidepoint(self.x, self.y) == True:
                button.changeTextSize(textSize + 2)  
            else:
                button.changeTextSize(textSize)

    def CM_changeGameState(self):
        # Changes game state based on what button pressed

        for button in self.CM.buttonList:
            if button.rect.collidepoint(self.x, self.y):
                
                if button.buttonType() == "MAIN MENU":
                    self.instructionsMenu = False
                    self.startMenu = True

    def CM_getPlayerColor(self):
        # Changes Blob Color based on color change menu
        self.player1.color = self.CM.p1Color
        self.player2.color = self.CM.p2Color

    def CM_changeSliderPosition(self):
        # Changes slider position based on mouse position
        start1 = self.CM.s1
        start2 = self.CM.s2
        end1 = start1 + 255
        end2 = start2 + 255

        # First checks if the place clicked is on a bar 
        # Changes slider position to place clicked
        for slider in self.CM.sliderList1:
            if self.y >= slider.rect.y and self.y <= slider.rect.y + 20:
                if self.x >= start1 and self.x <= end1:
                    slider.rect.x = self.x - 5

                    if slider.rect.x < start1:
                        slider.rect.x = start1
                    elif slider.rect.x > end1:
                        slider.rect.x = end1

        for slider in self.CM.sliderList2:
            if self.y >= slider.rect.y and self.y <= slider.rect.y + 20:
                if self.x >= start2 and self.x <= end2:
                    slider.rect.x = self.x - 5

                    if slider.rect.x < start2:
                        slider.rect.x = start2
                    elif slider.rect.x > end2:
                        slider.rect.x = end2



    def initWeapons(self):
        # Initializing different guns and their images
        self.gunSS = gunSS = SpriteSheet('gunSpriteSheet.png')

        AUG = Weapon(gunSS.image_at((40, 8, 58, 28)), "AUG", 3, 30, 18)
        AUG_ = Weapon(gunSS.image_at((40, 8, 58, 28)), "AUG", 3, 30, 18)
        M61 = Weapon(gunSS.image_at((10, 52, 70, 35)), "M61", 2, 100, 15)
        M61_ = Weapon(gunSS.image_at((10, 52, 70, 35)), "M61", 2, 100, 15)
        FAMAS = Weapon(gunSS.image_at((100, 40, 66, 32)), "FAMAS", 3, 40, 17)
        FAMAS_ = Weapon(gunSS.image_at((100, 40, 66, 32)), "FAMAS", 3, 40, 17)
        SCAR = Weapon(gunSS.image_at((73, 95, 65, 23)), "SCAR", 4, 30, 25)
        SCAR_ = Weapon(gunSS.image_at((73, 95, 65, 23)), "SCAR", 4, 30, 25)
        LMG = Weapon(gunSS.image_at((158, 93, 77, 28)), "LMG", 4, 50, 20)
        LMG_ = Weapon(gunSS.image_at((158, 93, 77, 28)), "LMG", 4, 50, 20)
        MP5K = Weapon(gunSS.image_at ((300, 164, 62, 28)), "MP5K", 3, 30, 18)
        MP5K_ = Weapon(gunSS.image_at ((300, 164, 62, 28)), "MP5K", 3, 30, 18)
        AK47 = Weapon(gunSS.image_at((272, 215, 65, 30)), "AK47", 3, 35, 22)
        AK47_ = Weapon(gunSS.image_at((272, 215, 65, 30)), "AK47", 3, 35, 22)
        PSG = Weapon(gunSS.image_at((340, 249, 85, 28)), "PSG", 12, 5, 50)
        PSG_ = Weapon(gunSS.image_at((340, 249, 85, 28)), "PSG", 12, 5, 50)

        self.weaponList1 = [AUG, M61, FAMAS, SCAR, LMG, MP5K, AK47, PSG]
        self.weaponList2 = [AUG_, M61_, FAMAS_, SCAR_, LMG_, MP5K_, AK47_, PSG_]






class Blob(pygame.sprite.Sprite):
    

 
    def __init__(self, width, height, level, boxes, weapon, color):
        # Initializing the player blob
        pygame.sprite.Sprite.__init__(self)

        (self.width, self.height) = (width, height)
        self.radius = 25
        self.image = pygame.Surface((self.radius * 2, self.radius * 2))
        self.image.set_colorkey((0,0,0))
        

        self.dX = 0
        self.dY = 0
        self.rect = self.image.get_rect()
        
        self.level = level
        self.boxes = boxes
        self.moveThru = False
        self.direction = "RIGHT"

        self.rect.x = randomNum(self.level.platformXCoordinates())
        self.rect.y = self.level.highestPlatX() - 200


        self.weapon = weapon 
        self.cooldown = weapon.fireRate
        self.OGCooldown = self.cooldown
        self.color = color
        
    def adjustStart(self):
        # Adjusts start to be randomly over a platform
        self.rect.x = randomNum(self.level.platformXCoordinates())
        self.rect.y = self.level.highestPlatX() - 200


    def calcGravity(self):
        # Calculate effect of gravity
        # Loosely based on 
        # http://programarcadegames.com/python_examples
        # /show_file.php?file=platform_jumper.py

        if self.dY == 0:
            self.dY = 1
        else:
            self.dY += .50


    def moveLeft(self):
        # Called when the user hits the left arrow.
        self.direction = "LEFT"
        if self.dX > -8:
            self.dX -= 1.5
 
    def moveRight(self):
        # Called when the user hits the right arrow. 
        self.direction = "RIGHT"
        if self.dX < 8:
            self.dX += 1.5

    def moveDown(self):
        # Goes through platform
        if self.dY == 0:
            self.dY += 3
            self.moveThru = True
        
 
    def stop(self):
        # Called when the user lets off the keyboard.
        if self.dX > 0:
            self.dX -= .5
            if self.dX < 0:
                self.dX = 0

        elif self.dX < 0:
            self.dX += .5
            if self.dX > 0:
                self.dX = 0

        elif self.dX == 0:
            self.dX = 0

    def bulletStop(self):
        # Physics to stop player when hit by bullet, similar to stop, but stops
        # slower

        if self.dY != 0:
            if self.dX > 0:
                self.dX -= .1
                if self.dX < 0:
                    self.dX = 0

            elif self.dX < 0:
                self.dX += .1
                if self.dX > 0:
                    self.dX = 0

            elif self.dX == 0:
                self.dX = 0

        else:
            if self.dX > 0:
                self.dX -= .5
                if self.dX < 0:
                    self.dX = 0

            elif self.dX < 0:
                self.dX += .5
                if self.dX > 0:
                    self.dX = 0

            elif self.dX == 0:
                self.dX = 0



    def jump(self):
        # Called when user hits 'jump' button. 

        # Move down a bit and see if there is a platform below us.    
        self.rect.y += 2
        self.platformHitList = pygame.sprite.spritecollide(self, 
                               self.level.platformList, False)
        self.rect.y -= 2
 
        # Only jump if on platform and if Y speed is 0
        if self.dY == 0:
            if len(self.platformHitList) > 0 or self.rect.bottom >= self.height:
                self.dY = -15

    def respawn(self):
        # Respawns blob after falling off the platform
        if self.rect.y >= 3000:

            self.rect.y = -300
            self.rect.x = (randomNum(self.level.platformXCoordinates()) + 
                           self.level.XLevelShift)

            self.dY = 0

            return True



    def update(self):
        # Updates Blob
         
        self.calcGravity()
        self.bulletStop()
        self.respawn()
        self.findWeaponCoordinates()
        self.weaponDirection()
        self.drawBlob()


        # Move side to side
        self.rect.x += self.dX
        self.horizontalHit()
    
        # Move up/down
        self.rect.y += self.dY

        # Checks that down is not being pressed
        if self.dY > 0 and self.moveThru == False:
            self.verticalHit()
        
        self.moveThru = False


    def horizontalHit(self):
        # Check plats hit horizontally

        blockHitList = pygame.sprite.spritecollide(self, 
                                self.level.platformList, False)
        for block in blockHitList:
            (startX, startY, width, height) = block.coordinates()

            if self.rect.right <= startX + round(self.dX):
                # If we are moving right,
                # set our right side to the left side of the item we hit
                if self.dX > 0:
                    self.dX = -self.dX / 10
                    self.rect.right = block.rect.left

            if self.rect.left + 1 >= startX + width + round(self.dX):
                if self.dX < 0:
                    self.dX = 0
                    # Otherwise if we are moving left, do the opposite.
                    self.rect.left = block.rect.right + 1


    def verticalHit(self):
        # Checks plat hit vertically

        blockHitList = pygame.sprite.spritecollide(self, 
                                self.level.platformList, False)
        for block in blockHitList:
            (startX, startY, width, height) = block.coordinates()

            if self.rect.bottom <= startY + self.dY:
                # Reset position based on the top/bottom of the object.
                if self.dY > 0:
                    self.rect.bottom = block.rect.top
                elif self.dY < 0:
                    self.rect.top = block.rect.bottom

                # Stop our vertical movement
                self.dY = 0


    def giveWeapon(self, weapon):
        # Changes weapon of the player
        self.weapon = weapon

    def findWeaponCoordinates(self):
        # Draws the weapon relative to the blob

        if self.direction == "RIGHT":
            self.weapon.rect.x = (self.rect.x + (self.radius * 2)/2 - 5)
            self.weapon.rect.y = (self.rect.y + (self.radius * 2)/2 - 2)
        else:
            self.weapon.rect.x = (self.rect.x + (self.radius * 2)/2 - 
                                  self.weapon.gunWidth + 5)
            self.weapon.rect.y = (self.rect.y + (self.radius * 2)/2 - 2)

    def weaponCoordinates(self):
        # Finds the coordinates of the weapons
        if self.direction == "RIGHT":
            return (self.weapon.rect.x + self.weapon.gunWidth - 20, 
                    self.weapon.rect.y + 2)
        else:
            return (self.weapon.rect.x - 20, self.weapon.rect.y + 2)

    def weaponDirection(self):
        # Draws the weapon according to what direction facing
        if self.direction == "LEFT":
            self.weapon.image = self.weapon.flippedImage
    
        else:
            self.weapon.image = self.weapon.OGImage

    def decreaseCooldown(self):
        # Decreases cooldown on every action
        if self.cooldown > 0:
            self.cooldown -= 1

    def resetCooldown(self):
        # Resets to original cooldown of gun
        self.cooldown = self.OGCooldown
     
    def drawBlob(self):
        # Draws main blob
        pygame.gfxdraw.filled_circle(self.image, self.radius, self.radius, 
                                    self.radius-1, self.color)
        pygame.gfxdraw.aacircle(self.image, self.radius, self.radius, 
                                self.radius-1, self.color)


        # Changes eyes according to direction facing
        if self.direction == "RIGHT":
            pygame.gfxdraw.aaellipse(self.image, self.radius + 4, 
                   self.radius - 5, self.radius/7, self.radius/3, (1,1,1))
            pygame.gfxdraw.filled_ellipse(self.image, self.radius + 4, 
                   self.radius - 5, self.radius/7, self.radius/3, (1,1,1))
            pygame.gfxdraw.aaellipse(self.image, self.radius + 12, 
                   self.radius - 5, self.radius/7, self.radius/3, (1,1,1))
            pygame.gfxdraw.filled_ellipse(self.image, self.radius + 12, 
                   self.radius - 5, self.radius/7, self.radius/3, (1,1,1))

        else:
            pygame.gfxdraw.aaellipse(self.image, self.radius - 4, 
                   self.radius - 5, self.radius/7, self.radius/3, (1,1,1))
            pygame.gfxdraw.filled_ellipse(self.image, self.radius - 4, 
                   self.radius - 5, self.radius/7, self.radius/3, (1,1,1))
            pygame.gfxdraw.aaellipse(self.image, self.radius - 12,
                   self.radius - 5, self.radius/7, self.radius/3, (1,1,1))
            pygame.gfxdraw.filled_ellipse(self.image, self.radius - 12, 
                   self.radius - 5, self.radius/7, self.radius/3, (1,1,1))



    def shoot(self):
        # Decreases weapon ammo
        self.weapon.decreaseAmmo()

    
class Platform(pygame.sprite.Sprite):

    def __init__(self, startX, startY, width, height):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([width, height])

        self.platformGray = (150, 150, 150)
        self.image.fill(self.platformGray)
 
        self.rect = self.image.get_rect()

        self.rect.x = startX
        self.rect.y = startY
        self.width = width
        self.height = height

    def coordinates(self):
        # Returns coordinates of platform
        return (self.rect.x, self.rect.y, self.width, self.height)

class Level(object):
 
    def __init__(self):

        self.platformList = pygame.sprite.Group()
        self.BGGray = (110, 110, 110)
        self.radius = 25
        self.XLevelShift = 0 
        self.YLevelShift = 0
        

    def update(self):
        # Update everything in this level.
        self.platformList.update()

 
    def draw(self, screen):
        # Draw everything on this level. 
        screen.fill(self.BGGray)
        # Draw all the sprite lists that we have
        self.platformList.draw(screen)



    def platformXCoordinates(self):
        # Finds all of the x coordinates of the platform
        coordinateList = []

        
        for platform in self.level:
            xStart = platform[0]
            width = platform[2]

            # SUBTRACT HALF THE WIDTH OF THE PLAYER/BOX WIDTH
            coordinateList.append((xStart - self.radius, 
                                   xStart + width - self.radius))

        return coordinateList

    def xShift(self, shiftX):
 
        # Keep track of the shift amount
        self.XLevelShift += shiftX
 
        # Go through all the sprite lists and shift
        for platform in self.platformList:
            platform.rect.x += shiftX

    def yShift(self, shiftY):
        # Keep track of the shift amount
        self.YLevelShift += shiftY
 
        # Go through all the sprite lists and shift
        for platform in self.platformList:
            platform.rect.y += shiftY

    def resetShift(self):
        for platform in self.platformList:
            platform.rect.x -= self.XLevelShift
            platform.rect.y -= self.YLevelShift

        self.XLevelShift = 0
        self.YLevelShift = 0

    def lowestPlatX(self):
        # Finds the lowest coordinate of the level platforms
        lowPlat = None
        for platform in self.platformList:
            lowPlat = max(lowPlat, platform.rect.y + platform.height)
        return lowPlat

    def highestPlatX(self):
        # Finds the highest coordinate of the level platforms
        highPlat = self.lowestPlatX()
        for platform in self.platformList:
            highPlat = min(highPlat, platform.rect.y)
        return highPlat


    def rightestPlat(self):
        # Finds the most right platform coordinate
        rightPlat = None
        for platform in self.platformList:
            rightPlat = max(rightPlat, platform.rect.x + platform.width)
        return rightPlat

    def leftestPlat(self):
        # Finds the most left platform coordinate
        leftPlat = self.rightestPlat()
        for platform in self.platformList:
            leftPlat = min(leftPlat, platform.rect.x)
        return leftPlat

    
class GameLevel(Level):
    
    def __init__(self, coordinates, name):
        # Testing level creator, later put into file
 
        # Call the parent constructor
        Level.__init__(self)
 

        self.level = coordinates
        self.name = name

        
        # Go through the array above and add platforms
        for platform in self.level:
            block = Platform(platform[0], platform[1], platform[2], platform[3])
            self.platformList.add(block)
        

    
class Box(pygame.sprite.Sprite):

    def __init__(self, width, height, level, x):
        # Initializing values
        pygame.sprite.Sprite.__init__(self)
        self.width = width
        self.height = height
        self.level = level

        spriteSheet = SpriteSheet('gunSpriteSheet.png')
        self.image = spriteSheet.image_at((170, 213, 35, 31))
        self.boxWidth = pygame.Surface.get_width(self.image)
        self.boxHeight = pygame.Surface.get_height(self.image)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -100


        self.change_y = 10

    def calcGravity(self):
        # Calculate effect of gravity.
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .75

        
    def update(self):
        self.calcGravity()
        self.rect.y += self.change_y

        # Stop when box hits platform

        blockHitList = pygame.sprite.spritecollide(self, 
                            self.level.platformList, False)

        for block in blockHitList:
            (startX, startY, width, height) = block.coordinates()
            if self.rect.bottom <= startY + self.change_y:
                # Reset position based on the top/bottom of the object.
                self.rect.bottom = block.rect.top
                # Stop vertical movement
                self.change_y = 0

        
         
class Weapon(pygame.sprite.Sprite):
    def __init__(self, image, name, fireRate, startAmmo, power):
        # Initializing values
        pygame.sprite.Sprite.__init__(self)
        

        self.name = name
        self.image = image
        self.fireRate = fireRate
        self.ammo = startAmmo
        self.power = power

        self.image.set_colorkey((0,0,0))

        self.gunWidth = pygame.Surface.get_width(self.image)
        self.gunHeight = pygame.Surface.get_height(self.image)
        self.rect = self.image.get_rect()
        # Set rect out of screen
        self.rect.x = -1000
        self.rect.y = -1000
        self.flipped = False

        self.OGImage = self.image
        self.flippedImage = pygame.transform.flip(self.image, True, False)

        self.OGAmmo = self.ammo


    def __str__(self):
        # Returns name of the gun
        return self.name

    def resetAmmo(self):
        # Resets ammo so it has a full clip
        self.ammo = self.OGAmmo

    def decreaseAmmo(self):
        # Decreases ammo by 1
        if self.ammo > 0: 
            self.ammo -= 1

    
    


class StartMenu(pygame.sprite.Sprite):


    def __init__(self, screen, width, height):
        # Initializing values
        pygame.sprite.Sprite.__init__(self)

        self.screen = screen
        self.width = width
        self.height = height


        self.BGGray = (110, 110, 110)
        self.menuList = pygame.sprite.Group()
        
        self.buttonList = pygame.sprite.Group()
        self.menuLabels()

    def menuLabels(self):

        # Creating text labels
        gameButton = Button("NEW GAME", 25, self.width * 2/3, 200)
        settings = Button("INSTRUCTIONS", 25, self.width *2/3, 250)
        levelEditor = Button("LEVEL EDITOR", 25, self.width *2/3, 300)
        colorMenu = Button("EDIT PROFILE", 25, self.width *2/3, 350)

        self.buttonList.add(gameButton, settings, levelEditor, colorMenu)

            
    def drawText(self):
        # Draws title text
        titleSize = 70
        titleFont = pygame.font.SysFont("arial", titleSize) 
        title = titleFont.render("SMO ARENA", 1, (255, 255, 255))
        self.screen.blit(title, (30, 30))

    
    def update(self):
        # Updates screen and draws
        self.screen.fill(self.BGGray)
        
        self.buttonList.update()
        self.buttonList.draw(self.screen)
        self.drawText()


class GameMenu(pygame.sprite.Sprite):
    def __init__(self, screen, width, height, p1Weapon, p2Weapon, killLimit):
        # Initializing values

        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        (self.width, self.height) = (width, height)
        self.killLimit = killLimit
        self.textSize = 18
        self.p1Score = 0
        self.p2Score = 0
        self.winner = None
        self.buttonList = pygame.sprite.Group()
        self.paused = False

        self.p1Weapon = p1Weapon
        self.p2Weapon = p2Weapon
        
        self.mainMenuButton()


        

    def text(self):
        # Writing player status text
        self.textSize = 18
        
        self.score = self.myFont.render("Score: %d|%d" % (self.p1Score, 
                                        self.p2Score), 1, (255, 255, 255))

        self.p1 = self.myFont.render("Player 1", 1, (255, 255, 255))
        self.p1Bullets = self.myFont.render("%s: %d" % (self.p1Weapon, 
                                        self.p1BCount), 1, (255, 255, 255))

        self.p2 = self.myFont.render("Player 2", 1, (255, 255, 255))
        self.p2Bullets = self.myFont.render("%s: %d" % (self.p2Weapon, 
                                        self.p2BCount), 1, (255, 255, 255))

    def mainMenuButton(self):
        # Setting up buttons for in game
        mainMenu = Button("MAIN MENU", 20, self.width - 130, self.height - 30)
        self.buttonList.add(mainMenu)


    def drawText(self):
        # Draws the status text
        self.screen.blit(self.score, (self.width/2 - 50, 30))

        self.screen.blit(self.p1, (30, 30))
        self.screen.blit(self.p1Bullets, (30, 50))

        self.screen.blit(self.p2, (self.width - 140, 30))
        self.screen.blit(self.p2Bullets, (self.width - 140, 50))

        

    def addScore(self, player):
        # Adds score to the player
        if player == 1:
            self.p1Score += 1
        elif player == 2:
            self.p2Score += 1

    def pause(self):
        # Creates text when game is being paused
        textSize = 60
        pauseFont = pygame.font.SysFont("arial", textSize) 
        pause = pauseFont.render("PAUSED", 1, (255, 255, 255))
        self.screen.blit(pause, (self.width/2 - 100, self.height/2 - 50))

    def gameOverText(self):
        # Creates text when game is over
        textSize = 60
        goFont = pygame.font.SysFont("arial", textSize) 
        go = goFont.render("GAME OVER", 1, (255, 255, 255))
        winnerFont = pygame.font.SysFont("arial", textSize/3) 
        winner = winnerFont.render("%s wins" % self.winner, 1, (255, 255, 255))

        self.screen.blit(go, (self.width/2 - 150, self.height/2 - 100))
        self.screen.blit(winner, (self.width/2 - 40, self.height/2 - 20))

    def changeP1Weapon(self, weaponName):
        # Changes player 1 weapon name
        self.p1Weapon = weaponName

    def changeP2Weapon(self, weaponName):
        # Changes player 2 weapon name
        self.p2Weapon = weaponName

    def checkGameOver(self):
        # Checks if game is over
        # If kill limit set to 0 or no value, play infinitely
        if self.killLimit == "":
            return False

        limit = int(self.killLimit)

        # Checks if either players score has reached the kill limit
        if limit == 0:
            return False
        elif self.p1Score >= limit:
            self.winner = "Player 1"
            return True
        elif self.p2Score >= limit:
            self.winner = "Player 2"
            return True
        else: 
            return False

    def update(self):
        # Updates the game menu 
        self.p1BCount = self.p1Weapon.ammo
        self.p2BCount = self.p2Weapon.ammo

        self.myFont = pygame.font.SysFont("arial", self.textSize) 
        self.text()
        self.drawText()

        if self.paused or self.checkGameOver():
            self.buttonList.update()
            self.buttonList.draw(self.screen)


class LevelEditorMenu(pygame.sprite.Sprite):
    def __init__(self, screen, width, height, mapName):
        # Initializing values
        self.screen = screen
        self.width = width
        self.height = height
        self.mapName = mapName
        self.BGGray = (110, 110, 110)
        self.rectList = []
        self.buttonList = pygame.sprite.Group()
        self.menuButtons()

    def drawText(self):
        # Draws description text
        self.textSize = 18
        self.myFont = pygame.font.SysFont("arial", self.textSize) 
        d1 = self.myFont.render("Click and drag to create a platform", 1, 
                               (255, 255, 255))
        d2 = self.myFont.render("Use arrow keys to scroll", 1, (255, 255, 255))
        d3 = self.myFont.render('''Press "Shift" and click to delete \
a platform''', 1, (255, 255, 255))
        d4 = self.myFont.render('''Map Name:''', 1, (255, 255, 255))
        descriptionList = [d1, d2, d3, d4]

        # Scales so space is even between each description
        for index in xrange(len(descriptionList)):
            scale = index * 30
            self.screen.blit(descriptionList[index], (30, 30 + scale))

         
        # Draws map name based on user input
        mName = self.myFont.render(self.mapName, 1, (0, 0, 0))
        self.screen.blit(mName, (150, 120))


    def drawPlats(self):
        # Draws platforms in rect list

        platformGray = (150, 150, 150)

        for platform in self.rectList:
            startX = platform[0]
            startY = platform[1]
            width = platform[2]
            height = platform[3]
            pygame.draw.rect(self.screen, platformGray, 
                            [startX, startY, width, height], 0)


    def removePlat(self, x, y):
        # Removes platform where the x and y coordinate is
        for platform in self.rectList:

            startX = platform[0]
            startY = platform[1]
            width = platform[2]
            height = platform[3]

            if (x >= startX) and (x <= startX + width):
                if (y >= startY) and (y <= startY + height):
                    self.rectList.remove(platform)



    def menuButtons(self):
        # Buttons for level editor meu
        saveButton = Button("SAVE", 20, self.width - 210, self.height - 30)
        mainMenu = Button("MAIN MENU", 20, self.width - 130, self.height - 30)
        self.buttonList.add(saveButton, mainMenu)


    def nameSetup(self):
        # Draws blank white rect for name
        space = 30
        pygame.draw.rect(self.screen, (255, 255, 255), 
                         [space * 5, space * 4, space * 5, space], 0)

    
    def update(self):
        # Updates Level Creator Menu

        self.screen.fill(self.BGGray)

        self.drawPlats()
        
        self.nameSetup()
        self.drawText()
        self.buttonList.update()
        self.buttonList.draw(self.screen)


class PreGameMenu(pygame.sprite.Sprite):

    def __init__(self, screen, width, height, levelList, lColor, rColor, kills):
        # Initialiizing Values
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        (self.width, self.height) = (width, height)
        self.levels = levelList
        self.lColor = lColor
        self.rColor = rColor
        self.kills = kills

        self.BGGray = (110, 110, 110)
        self.buttonList = pygame.sprite.Group()
        self.levelIndex = 0
        self.index = self.levelIndex % len(self.levels)

        self.tButtonList = pygame.sprite.Group()
        self.rButton = TriangleButton(self.rColor, "RIGHT", width-70, height/2)
        self.lButton = TriangleButton(self.lColor, "LEFT", 10, height/2)
        self.tButtonList.add(self.rButton, self.lButton)


        self.menuButtons()



    def drawMap(self):
        # Drawing map

        level = self.levels[self.index]
        level.draw(self.screen)

    def drawMapName(self):
        # Drawing map name at top

        levelName = self.levels[self.index].name
        levelSize = 40
        levelFont = pygame.font.SysFont("arial", levelSize) 
        level = levelFont.render("%s" % levelName, 1, (255, 255, 255))

        self.screen.blit(level, (30, 30))

    def menuButtons(self):
        # Buttons for level editor meu
        mainMenu = Button("MAIN MENU", 20, self.width - 130, self.height - 30)
        start = Button("START", 40, self.width - 275, self.height - 30)
        self.buttonList.add(mainMenu, start)

    def killLimitSetup(self):
        # Draws Box for Kill Limit and the limit is based on user input
        space = 30
        self.textSize = 20
        self.myFont = pygame.font.SysFont("arial", self.textSize) 

        killLimit = self.myFont.render("Kill Limit:", 1, (255, 255, 255))
        kills = self.myFont.render("%s" % self.kills, 1, (1, 1, 1))

        pygame.draw.rect(self.screen, (255, 255, 255), [self.width - space * 4, 
                         space, space * 3, space], 0)

        self.screen.blit(killLimit, (self.width - (space * 7), space)) 
        self.screen.blit(kills, (self.width - (space * 4), space))

    def update(self):
        # Updates the level creator menu
        self.index = self.levelIndex % len(self.levels)

        self.buttonList.update()
        self.tButtonList.update()

        self.screen.fill(self.BGGray)
        self.drawMap()
        self.drawMapName()
        self.killLimitSetup()
        self.tButtonList.draw(self.screen)
        self.buttonList.draw(self.screen)

class InstructionMenu(pygame.sprite.Sprite):
    def __init__(self, screen, width, height):
        # Initializing values
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        (self.width, self.height) = (width, height)
        self.BGGray = (110, 110, 110)
        self.buttonList = pygame.sprite.Group()

        self.menuButtons()

    def menuButtons(self):
        # Buttons for instructions menu
        mainMenu = Button("MAIN MENU", 20, self.width - 130, self.height - 30)
        self.buttonList.add(mainMenu)

    def drawInstructions(self, screen):
        # Text for instructions on how to play the game
        self.textSize = 18
        self.myFont = pygame.font.SysFont("arial", self.textSize) 
        d1 = self.myFont.render("Controls(Player1/Player2)", 1, (255, 255, 255))
        d2 = self.myFont.render("Jump:    Up Arrow / W", 1, (255, 255, 255))
        d3 = self.myFont.render("Drop:    Down Arrow / S", 1, (255, 255, 255))
        d4 = self.myFont.render("Left:    Left Arrow / A", 1, (255, 255, 255))
        d5 = self.myFont.render("Right:   Right Arrow / D", 1, (255, 255, 255))
        d6 = self.myFont.render("Shoot:   ForwardSlash / Space",1,(255,255,255))
        d7 = self.myFont.render('''Press "P" to pause ''', 1, (255, 255, 255))
        d8 = self.myFont.render("Instructions:", 1, (255, 255, 255))
        d9 = self.myFont.render("Try to blast your opponent off the map! ", 
                                1, (255, 255, 255))
        d10 = self.myFont.render("Everytime they fall off, you get one point.", 
                                1, (255, 255, 255))

        descriptionList = [d1, d2, d3, d4, d5, d6, d7]
        d2List = [d8, d9, d10]

        for index in xrange(len(descriptionList)):
            scale = index * 30
            self.screen.blit(descriptionList[index], (30, 30 + scale))

        for index in xrange(len(d2List)):
            scale = index * 30
            self.screen.blit(d2List[index], (30, 300 + scale))


    
    def update(self):
        # Updating 
        self.screen.fill(self.BGGray)
        self.drawInstructions(self.screen)
        self.buttonList.update()
        self.buttonList.draw(self.screen)

class ColorMenu(pygame.sprite.Sprite):

    def __init__(self, screen, width, height):
        # Initializing values
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        (self.width, self.height) = (width, height)

        self.radius = 50
        self.BGGray = (110, 110, 110)
        self.buttonList = pygame.sprite.Group()

        self.sliderList1 = pygame.sprite.Group()
        self.sliderList2 = pygame.sprite.Group()

        self.menuButtons()
        self.sliders()
        self.colors()

    def menuButtons(self):
        # Buttons for instructions menu
        mainMenu = Button("MAIN MENU", 20, self.width - 130, self.height - 30)
        self.buttonList.add(mainMenu)

    def drawSliderBars(self):
        

        # Draws the gradient background behind slider bar

        for colorIndex in xrange(0, 256):
            # Draw rectangle of width 1 256 times, decreasing color each time

            pygame.draw.rect(self.screen, (255-colorIndex,0,0), 
                             [self.s1 + colorIndex, 305, 1, 10], 0)
            pygame.draw.rect(self.screen, (0,255-colorIndex,0), 
                             [self.s1 + colorIndex, 355, 1, 10], 0)
            pygame.draw.rect(self.screen, (0,0,255-colorIndex), 
                             [self.s1 + colorIndex, 405, 1, 10], 0)

            pygame.draw.rect(self.screen, (255-colorIndex,0,0), 
                             [self.s2 + colorIndex, 305, 1, 10], 0)
            pygame.draw.rect(self.screen, (0,255-colorIndex,0), 
                             [self.s2 + colorIndex, 355, 1, 10], 0)
            pygame.draw.rect(self.screen, (0,0,255-colorIndex), 
                             [self.s2 + colorIndex, 405, 1, 10], 0)


    def drawSampleBlob(self):
        # Draws blob to display color
        midX = 175
        midY = 200
        C1 = self.p1Color
        C2 = self.p2Color
        
        # Blob 1
        pygame.gfxdraw.filled_circle(self.screen, midX, midY, self.radius, C1)
        pygame.gfxdraw.aacircle(self.screen, midX, midY, self.radius, C1)

        pygame.gfxdraw.aaellipse(self.screen, midX+25, midY-10, 
                                 self.radius/7, self.radius/3, (0,0,0))
        pygame.gfxdraw.filled_ellipse(self.screen, midX+25, midY-10, 
                                 self.radius/7, self.radius/3, (0,0,0))
        pygame.gfxdraw.aaellipse(self.screen, midX+5, midY-10, 
                                 self.radius/7, self.radius/3, (0,0,0))
        pygame.gfxdraw.filled_ellipse(self.screen, midX+5, midY-10, 
                                 self.radius/7, self.radius/3, (0,0,0))

        # Blob 2
        midX = 525
        pygame.gfxdraw.filled_circle(self.screen, midX, midY, self.radius, C2)
        pygame.gfxdraw.aacircle(self.screen, midX, midY, self.radius, C2)
        pygame.gfxdraw.aaellipse(self.screen, midX+25, midY-10, 
                                 self.radius/7, self.radius/3, (0,0,0))
        pygame.gfxdraw.filled_ellipse(self.screen, midX+25, midY-10, 
                                 self.radius/7, self.radius/3, (0,0,0))
        pygame.gfxdraw.aaellipse(self.screen, midX+5, midY-10, 
                                 self.radius/7, self.radius/3, (0,0,0))
        pygame.gfxdraw.filled_ellipse(self.screen, midX+5, midY-10, 
                                 self.radius/7, self.radius/3, (0,0,0))



    def sliders(self):
        # Creates slider list
        self.red1 = Slider(50, 300)
        self.green1 = Slider(50, 350)
        self.blue1 = Slider(50, 400)

        self.red2 = Slider(400, 300)
        self.green2 = Slider(400, 350)
        self.blue2 = Slider(400, 400)

        self.sliderList1.add(self.red1, self.green1, self.blue1)
        self.sliderList2.add(self.red2, self.green2, self.blue2)

        self.s1 = self.red1.x
        self.s2 = self.red2.x
        
    def colors(self):
        # Retrieves RGB Color code based on slider position
        red = 255 - (self.red1.rect.x - 50)
        green = 255 - (self.green1.rect.x - 50)
        blue = 255 - (self.blue1.rect.x - 50)
        self.p1Color = (red, green, blue)

        red = 255 - (self.red2.rect.x - 400)
        green = 255 - (self.green2.rect.x - 400)
        blue = 255 - (self.blue2.rect.x - 400)
        self.p2Color = (red, green, blue)

    def drawDescriptionText(self):
        # Draws Description Text 

        titleSize = 40
        labelSize = 18
        titleFont = pygame.font.SysFont("arial", titleSize) 
        labelFont = pygame.font.SysFont("arial", labelSize) 

        title = titleFont.render("Profile Customizer", 1, (255, 255, 255))
        label1 = labelFont.render("Player 1", 1, (255, 255, 255))
        label2 = labelFont.render("Player 2", 1, (255, 255, 255))
        color1 = labelFont.render("RED", 1, (255, 255, 255))
        color2 = labelFont.render("GREEN", 1, (255, 255, 255))
        color3 = labelFont.render("BLUE", 1, (255, 255, 255))

        self.screen.blit(title, (30, 30))
        self.screen.blit(label1, (145, 120))
        self.screen.blit(label2, (500, 120))
        self.screen.blit(color1, (325, 300))
        self.screen.blit(color2, (325, 350))
        self.screen.blit(color3, (325, 400))

    def update(self):
        # Updating 
        self.screen.fill(self.BGGray)

        self.drawSliderBars()
        self.drawSampleBlob()
        self.drawDescriptionText()

        self.sliderList1.update()
        self.sliderList2.update()
        self.buttonList.update()

        self.colors()

        self.sliderList1.draw(self.screen)
        self.sliderList2.draw(self.screen)
        self.buttonList.draw(self.screen)

class Slider(pygame.sprite.Sprite):
    def __init__(self, x, y):
        # Making gray surface for slider
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((15, 20))
        self.image.fill((50, 50, 50))
        self.x = x 
        self.y = y
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Button(pygame.sprite.Sprite):
    # Creates button that responds when clicked on

    def __init__(self, text, textSize, x, y):
        # Initializing values

        pygame.sprite.Sprite.__init__(self)

        self.width = len(text) * textSize * .75
        self.height = textSize * 1.5

        self.image = pygame.Surface((self.width, self.height))

        self.image.set_colorkey((0,0,0))
        self.text = text
        self.textSize = textSize
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        
    def changeTextSize(self, num):
        # Changes textsize to input number
        self.textSize = num

    def buttonType(self):
        # Returns the buttontype as the string of the name
        return self.text

    def update(self):
        # Update button
        self.image.fill((0, 0, 0))
        self.myFont = pygame.font.SysFont("arial", self.textSize) 
        self.playText = self.myFont.render(self.text, 1, (255, 255, 255))
        self.image.blit(self.playText, (0, 0))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        # Initializing bullet values
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((40, 3))
        self.image.fill((0, 0, 0))

        # Draws red tip
        pygame.gfxdraw.rectangle(self.image, (0,0, 5, 3), (244, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x 
        self.rect.y = y
        self.direction = direction

        self.OGImage = self.image
        self.flippedImage = pygame.transform.flip(self.image, True, False)

    def update(self):
        # Moves bullet direction
        # Changes image direction based on which way player is looking
        if self.direction == "RIGHT":
            self.image = self.flippedImage
            self.rect.x += 25 

        elif self.direction == "LEFT":
            self.image = self.OGImage
            self.rect.x -= 25

class TriangleButton(pygame.sprite.Sprite):

    def __init__(self, color, direction, x, y):
        # Initializing values

        pygame.sprite.Sprite.__init__(self)

        self.color = color
        self.direction = direction

        self.image = pygame.Surface((60, 60))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def changeColor(self, color):
        # Changes button color
        self.color = color

    def drawTriangle(self):
        # Draws Triangle depending on direction
        if self.direction == "RIGHT":
            pygame.gfxdraw.aatrigon(self.image,0,0,0,60,60,30, self.color)
            pygame.gfxdraw.filled_trigon(self.image,0,0,0,60,60,30, self.color)
            

        elif self.direction == "LEFT":
            pygame.gfxdraw.aatrigon(self.image,0,30,60,60,60,0, self.color)
            pygame.gfxdraw.filled_trigon(self.image,0,30,60,60,60,0, self.color)

    def update(self):
        # Draws the triangle when called
        self.drawTriangle()

class SpriteSheet(object):
    # COPIED VERBATIM FROM: 
    # http://www.pygame.org/wiki/Spritesheet?parent=CookBook
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error, message:
            print 'Unable to load spritesheet image:', filename
            raise SystemExit, message
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)
        

def randomNum(rangeList):
    # Returns a randomNum between different ranges

    def rangeSize(l):
        # Finds the overall size of the combined ranges
        size = 0
        for interval in l:
            size += (interval[1] - interval[0])
        return size

    def intervalProb(ranges, totalSize):
        # Finds the probability of each range 
        totalSize = totalSize * 1.0
        i = 0
        probabilityList = []
        for interval in ranges:
            start = i
            i += interval/totalSize
            probabilityList.append((start, i))

        return probabilityList


    totalRangeSize = rangeSize(rangeList)
    rangeSizes = [x[1] -x[0] for x in rangeList]
    ranges = intervalProb(rangeSizes, totalRangeSize)
    
    # Find a random number and base it on probability of getting a range
    randProb = random.random()
    for i in xrange(len(ranges)):
        if (randProb >= ranges[i][0]) and (randProb <= ranges[i][1]):
            randList = rangeList[i]

    # Returns a random number from the list
    randNum = random.randint(randList[0], randList[1])
    return randNum




    




a = ArenaGame()
a.run()