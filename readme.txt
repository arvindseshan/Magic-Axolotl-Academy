The name of my project is Magic Axolotl Academy. It is a spell casting game where a player uses different hand movements to cast various spells (—, |, u, n, ⚡, and ♥) and move the main character. The main character is Kimchee the Axolotl. The main enemies are smog monsters because the biggest threat to axolotls are urbanization and pollution, threatening their environment. Enemies can be defeated by performing the correct order of spells displayed over the enemy when a line of sight is established between the alxolotl and a monster. The idea for the game is based on the 2016 and 2020 Google Doodle called Magic Cat Academy (https://www.google.com/doodles/halloween-2020).

To run the game, open the file "TermProjectGame.py" in Visual Studio and run the code. Make sure that this file is in the same folder as all of the .txt, .png, .jpg, .py, .pkl, and .h5 files provided.

Note: the hand tracking is set to detect blue gloves. Any blue object you can hold in your hand should work. Just make sure that there are no large bluish-purple objects in the rest of the camera's view (e.g. a blue shirt or large blue object in background). As long as the object is smaller than the object you want to track, it should be fine. If you do not have a blue object that works with the default settings, I have provided hsv min and max sliderbars that appear over the displayed video feed. You can adjust these to track any color of your choice.

This project requires the following libraries/modules:
Image Utilities (imutils)
OpenCV (cv2)
NumPy (numpy)
cmu_112_graphics (file included in submission folder)
tensorflow
pickle
scikit-learn (sklearn)
random
time

Game Shortcuts:
when in main menu, press s to start game
press r to reset
press f to collect data for training gestures (default set to "u", but can be changed in the code by changing app.gestureToTrain in addStarted)
during the game, press p to pause and s to step
press g to end game
press w to enable and disable wall manipulation and click with mouse to add/remove walls
press t for testing mode (Displays best path that enemies and the player are taking. Displays scores for each cell in the game which tell the best spots to travel to to avoid monsters and maintain line of sight. Displays red or green lines from the player to each monster to tell whether the monster is in a direct line of sight and a red circle to tell where the line of sight is blocked. Enemies and the player are displayed as circles, indicating their intersection area for collision detection between enemy and player.)
press a to enable auto mode, which moves the axolotl automatically to the best position
