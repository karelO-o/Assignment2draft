from psychopy import visual, event, core, gui, data
import glob
import random
import statistics
import os
import pandas as pd

class RabbitLionExperiment:
    def __init__(self, pathToImages, pathToFeedbackImages, numberOfRounds):
        # consent dialogue
        self.consent = gui.Dlg(
            title='Study information',
            labelButtonOK='OK',
            labelButtonCancel='Cancel' # button for declining to participate. 
        )
        self.consent.addText(
        'Workshop demonstration; not a real research study.\n'
        'Task: see a lion or burrow, then press an arrow key.\n'
        'Responses and times print in the Runner; no file is saved.\n'
        'Taking part is voluntary. Ask your instructor with questions.\n'
        'Choose OK if you provide informed consent to participant, or Cancel to decline participation in the study.')
        self.consent.show()
        if not self.consent.OK:
            core.quit()
        
        # info about participant dialogue
        self.participantInfo = {}
        self.box = gui.Dlg(title="The Fleeing Rabbit")
        self.box.addField("Native language", choices=["Danish", "English", "Slovak", "Czech", "Hungarian", "Other"])
        self.box.addField("If Other language, please specify")
        self.box.addField("Handedness", choices=["Right-handed", "Left-handed", "Both"])
        self.box.show()
        
        if self.box.OK:
            if self.box.data["Native language"] == "Other":
                self.participantInfo["Native language"] = self.box.data["If Other language, please specify"]
            else:
                self.participantInfo["Native language"] = self.box.data["Native language"]
            
            self.participantInfo["Handedness"] = self.box.data["Handedness"]
            self.participantInfo["PID"] = random.randint(10000, 99999)
        else:
            core.quit()
        
        # create path for log file
        date = data.getDateStr()
        logfile_path = f"logfiles/logfile_{self.participantInfo['PID']}_{date}.csv"
        
        # create folder for log if not exists
        os.makedirs("logfiles", exist_ok=True)
        
        # data from experiment array
        rows = []
        
        self.images = glob.glob(pathToImages)
        self.feedback_images = glob.glob(pathToFeedbackImages)
        random.shuffle(self.images)
        self.allowedKeys = ['left', 'right', 'escape']
        self.counter = 0
        self.currentKey = None
        self.currentAnswerValidity = None
        self.score = 0
        self.images_count = len(self.images)
        if numberOfRounds and self.images_count >= numberOfRounds:
            # cap limit to custom number of rounds
            self.images_count = numberOfRounds
        self.win = visual.Window(size=(1280, 720), fullscr=False,
                    color='black', checkTiming=False)
        self.img = visual.ImageStim(self.win, size=2)
        self.text = visual.TextStim(self.win,
                        color="white", height=0.1, pos=(0, 0))
        self.fixation = visual.TextStim(self.win,
                        text="+", color="white", height=0.1, pos=(0, 0))
        # Add timer
        self.stopwatch = core.Clock()
        # "Random" durations
        self.durations = [0.2, 0.4, 0.6, 0.7, 1, 1.2, 1.4]
        random.shuffle(self.durations)
        # Reaction times
        self.reactionTimes = []
        self.reactionTimesRabbit = []
        self.reactionTimesLion = []
        # random PID
        self.pid = f"P{random.randint(10000, 99999)}"
        
    def start_experiment(self):
        self.intro_screen()
        while self.counter < self.images_count:
            self.show_next_stimuli()
            self.catch_user_input()
            self.evaluate_answer()
            self.show_validity()
            self.counter += 1
            
        self.final_screen()
    
    def intro_screen(self):
        self.text.text = "Welcome!\nYou can press left or right arrow\nWhen you see shelter, press arrow pointing that direction\nWhen you lion, press arrow pointing to opposite direction\nWhen you see cross, focus on that\nYou can always quick by pressing ESC\nPress any key to start :)"
        self.text.draw()
        self.win.flip()
        event.waitKeys()
        # initial fixation
        self.fixation.draw()
        self.win.flip()
        core.wait(0.5)
        # added random waiting time
        core.wait(self.durations[0])
 
    def show_next_stimuli(self):
        self.img.image = self.images[self.counter]
        self.img.draw()
        self.win.flip()
        # reset timer for calculating reaction time
        self.stopwatch.reset()
        
    def catch_user_input(self):
        self.currentKey = event.waitKeys(keyList=self.allowedKeys)
        # catch reaction time and add that into array
        # also differenciate rabbit from lion task
        temp = self.stopwatch.getTime()
        self.reactionTimes.append(temp)
        if 'rabbit' in self.img.image:
            self.reactionTimesRabbit.append(temp)
        elif 'lion' in self.img.image:
            self.reactionTimesLion.append(temp)
    
    def evaluate_answer(self):
        if self.img.image.endswith('_L.jpg'):
            correct_key = 'left'
        else:
            correct_key = 'right'
        # emergency exit
        if self.currentKey[0] == "escape":
            self.win.close()
            core.quit()
        if(self.currentKey[0] == correct_key):
            self.currentAnswerValidity = True
            self.score += 1
        else:
            self.currentAnswerValidity = False
    
    def show_validity(self):
        # show feedback image
        if self.currentAnswerValidity == True:
            self.img.image = self.feedback_images[0]
        else:
            self.img.image = self.feedback_images[1]
        self.img.draw()
        self.win.flip()
        core.wait(1)
        # todo, do not show focus point between last round and end screen
        self.fixation.draw()
        self.win.flip()
        core.wait(0.5)
        # added random waiting time
        core.wait(self.durations[self.counter])
        
    def final_screen(self):
        self.text.text = f"Your Score: {self.score}\nAverage r. time: {round(statistics.mean(self.reactionTimes), 4)}\nAverage rabbit time: {round(statistics.mean(self.reactionTimesRabbit), 4)}\nAverage lion time: {round(statistics.mean(self.reactionTimesLion), 4)}\nAutomatically closing in 5 secs"
        self.text.draw()
        self.win.flip()
        core.wait(5)


experiment = RabbitLionExperiment(
    pathToImages="stimuli/stimulus*.jpg",
    pathToFeedbackImages="feedback/*.jpg",
    numberOfRounds=6
)

experiment.start_experiment()

core.quit()



