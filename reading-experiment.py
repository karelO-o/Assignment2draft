from psychopy import visual, event, core, gui, data
import glob
import random
import statistics
import os
import pandas as pd

class ReadingExperiment:
    def __init__(self):
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
        self.logfile_path = f"logfiles/logfile_{self.participantInfo['PID']}_{date}.csv"
        
        # create folder for log if not exists
        os.makedirs("logfiles", exist_ok=True)
        
        # story variables
        self.story = """On a clear Saturday morning, Maya set out for a slow jog along the riverside path.
The air smelled faintly of wet grass, and bicycles drifted past like quiet birds.
She counted her breaths, matching them to the soft rhythm of her footsteps.
At the old footbridge she paused, watching sunlight scatter across the water.
A family unpacked breakfast nearby; a thermos hissed, and someone laughed.
Maya stretched, then started again along the path that curved through willows.
Past the square she slowed, noticing the scent of roasted coffee drifting from a tiny kiosk.
Children were chalking bright shapes on the paving stones, and a busker tuned a battered guitar.
Maya stopped to tie a loose shoelace and glanced at the notes for the concert pinned to a lamp post.
She thought about her own violin, stored away in a dusty case under her bed.
The sun was climbing higher, glinting off the windows of nearby apartments.
She began jogging again, feeling the steady beat of her pulse and the easy warmth of the morning settle into her muscles."""
        self.control_cond = self.story.split()
        self.surprise_cond = self.control_cond.copy()
        
        # control word that will be replaced in surprise_cond by surprise_word
        self.control_target = "grass,"
        self.surprise_target = "goobernator"
        # apply replace
        self.target_i = self.control_cond.index(self.control_target)
        self.surprise_cond[self.target_i] = self.surprise_target
        conds = [self.control_cond, self.surprise_cond]
        # choose randomly control or surprise cond
        self.random_index = random.randrange(len(conds))
        self.selected_cond = conds[self.random_index]
        
        # window and elements
        self.win = visual.Window(
            size=(1000, 700), units="pix", color="black", fullscr= False
        )
        self.stimulus = visual.TextStim(self.win, text="x", color="white", height=48, units="pix")
        self.clock = core.Clock()
        self.results = []
        
    def start_experiment(self):
        self.intro()
        for index, word in enumerate(self.selected_cond):
            self.round(index)
        # save data
        logfile = pd.DataFrame(self.results)
        logfile.to_csv(self.logfile_path, index=False)
        # add data about participant into another csv that collects that
        # if not exists, create new one
        self.participantsfile = []
        if os.path.exists("./logfiles/participants.csv"):
            self.participantsfile = pd.read_csv("./logfiles/participants.csv")
        else:
            self.participantsfile = pd.DataFrame()
        self.new_data = pd.DataFrame([self.participantInfo])
        self.combined_file = pd.concat([self.participantsfile, self.new_data])
        self.combined_file.to_csv("./logfiles/participants.csv", index=False)
        
        # say thank you
        self.outro()
        
    def round(self, index):
        self.show_text(index)
        self.wait_for_response(index)
        
    def show_text(self, i):
        self.win.callOnFlip(self.clock.reset)
        self.stimulus.text = self.selected_cond[i]
        self.stimulus.draw()
        self.win.flip()
        
    def wait_for_response(self, i):
        keys = event.waitKeys(
            keyList=["space", "escape"],
            timeStamped=self.clock
        )
        self.key, self.reaction_time = keys[0]
            
        if self.key == "escape":
            self.win.close()
            core.quit()
            
        # record data
        self.results.append({
            "participant": self.participantInfo["PID"],
            "condition": self.random_index,
            "word_index": i,
            "word": self.selected_cond[i],
            "is_surprising": int(
            self.random_index == 1 and i == self.target_i),
            "rt_ms": self.reaction_time * 1000
        })
        print(self.results)
    
    def intro(self):
        self.stimulus.text = 'You will read one story, one word at a time.\nPress Space for the next word.\nPress Escape to stop.\nPress any key to begin.'
        self.stimulus.draw()
        self.win.flip()
        
        event.waitKeys()
        self.stimulus.text = "x"
        self.stimulus.draw()
        self.win.flip()
        
        core.wait(0.6)
        
    def outro(self):
        self.stimulus.text = "That's it, thank you for your time! :)\nPress anything to close the program"
        self.stimulus.draw()
        self.win.flip()
        core.wait(1)
        
        event.waitKeys()

        
experiment = ReadingExperiment()
experiment.start_experiment()

core.quit()