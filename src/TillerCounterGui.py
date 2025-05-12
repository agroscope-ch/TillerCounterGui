import os
import re
import tkinter as tk
import numpy as np
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw

from TillerCounter import CTillerCounter
from config import IMG_WIDTH_LAPTOP, IMG_HEIGHT_LAPTOP, X_START, Y_START, USE_TWO_SCREENS
from config import SCALE_DESKTOP_SCREEN, OFFSET

class CTillerCounterGui(tk.Tk):
    def __init__(self):
       super().__init__()
       self.title("Agroscope Tiller Counter")
       self.geometry("2048x1024")
       self.orig_img_width = 0
       self.orig_img_height = 0
       self.img_width = int(IMG_WIDTH_LAPTOP*SCALE_DESKTOP_SCREEN)  # adapted to screen size: 924 for smaller screens. Factor 1.74 for desk screens (e.g. 1900 x 1200)
       self.img_height = int(IMG_HEIGHT_LAPTOP*SCALE_DESKTOP_SCREEN) # adapted to screen size: 612 for smaller screens. Factor 1.74 for desk screens (e.g. 1900 x 1200)
       self.img_x_start = X_START
       self.img_y_start = Y_START # 100
       self.r_man = 6
       self._color_auto_tillers_fill = (255, 0, 0, 128)
       self._color_auto_tillers_outl = (255, 255, 0, 1)
       self._color_man_tillers_outl = (255, 0, 255, 128)

       self.bind(sequence='<ButtonRelease-1>', func=self.OnLButtonUp)
       self.bind(sequence='<ButtonRelease-3>', func=self.OnRButtonUp)

       # Define tkinter variables (that are displayed)
       self.tkstring_filename = tk.StringVar()   # filename of the image, e.g. DSC_0005.jpg
       self.tkstring_dir_path = tk.StringVar()   # directory containing all images
       self.tki_r_min = tk.IntVar()              # rmin of Hooge
       self.tki_r_max = tk.IntVar()              # rmax of Hooge
       self.tki_tiller_cnt = tk.IntVar()         # total tiller counts (displayed top right)
       self.tki_min_dist = tk.IntVar()           # min distance for Hooge
       self.tki_param1 = tk.IntVar()             # param1 Hooge (check!)
       self.tki_param2 = tk.IntVar()             # param2 Hooge (check!)
       self.tki_show_detected = tk.IntVar()      # toggle the current auto and manually added/removed tiller detections
       self.tki_man_add = tk.IntVar()            # from checkbox (do I want to add? -> 1)
       self.tkcheck_detected = tk.Checkbutton(self, text='Show Detection', variable=self.tki_show_detected, # Checkboxes
                                           onvalue=1, offvalue=0, command=self.show_hide_detection)
       self.tkcheck_man_add = tk.Checkbutton(self, text='Manually Add', variable=self.tki_man_add, 
                                           onvalue=1, offvalue=0)

       self.create_widgets()

       self.TillerCounter = None
       self.dir_name = ""
       self.dir_list = ""
       self.current_image_orig = None
       self.current_image = None
       self.idx_img = 0
       self._curr_tillers = None
       self._curr_man_add_tillers = []
       self._original_tiller_cnt = 0
       self.FinalTillerCount = 0
       self._man_added_cnt = 0
       self._man_removed_cnt = 0

    def create_widgets(self):
        """
        Tkinter method that creates all widgets of the gui.
        """
        self.r_min_label                = tk.Label(self, text="Min radius(px): ")
        self.r_max_label                = tk.Label(self, text="Max radius(px): ")
        self.min_dist_label             = tk.Label(self, text="MinDist(px): ")
        self.filename_label             = tk.Label(self, text="File name: ")
        self.current_filename_label     = tk.Label(self, text="No file selected")
        self.tiller_count_label         = tk.Label(self, text="Tiller count: ")
        self.current_tiller_count_label = tk.Label(self, text="0")
        self.param1_label               = tk.Label(self, text="Param1: ")
        self.param2_label               = tk.Label(self, text="Param2: ")

        self.r_min_entry    = tk.Entry(self, textvariable=self.tki_r_min)
        self.r_max_entry    = tk.Entry(self, textvariable=self.tki_r_max)
        self.min_dist_entry = tk.Entry(self, textvariable=self.tki_min_dist)
        self.param1_entry = tk.Entry(self, textvariable=self.tki_param1)
        self.param2_entry = tk.Entry(self, textvariable=self.tki_param2)
        self.tki_r_min.set(14)
        self.tki_r_max.set(54)
        self.tki_min_dist.set(50)
        self.tki_param1.set(95)
        self.tki_param2.set(28)

        padx = 3
        pady = 3
        self.r_min_label.grid(row=1, column=0, padx=padx, pady=pady)
        self.r_min_entry.grid(row=1, column=1, padx=padx, pady=pady)
        self.r_max_label.grid(row=0, column=11, padx=padx, pady=pady)
        self.r_max_entry.grid(row=0, column=12, padx=padx, pady=pady)
        self.min_dist_label.grid(row=1, column=2, padx=padx, pady=pady)
        self.min_dist_entry.grid(row=1, column=3, padx=padx, pady=pady)
        self.param1_label.grid(row=1, column=4, padx=padx, pady=pady)
        self.param1_entry.grid(row=1, column=5, padx=padx, pady=pady)
        self.param2_label.grid(row=0, column=13, padx=padx, pady=pady)
        self.param2_entry.grid(row=0, column=14, padx=padx, pady=pady)

        self.filename_label.grid(row=0, column=0, padx=2*padx, pady=pady)
        self.current_filename_label.grid(row=0, column=1, padx=2*padx, pady=pady)
        self.tkcheck_detected.grid(row=0, column=2)
        self.tkcheck_man_add.grid(row=0, column=3)
        self.tiller_count_label.grid(row=0, column=5, padx=2*padx, pady=pady)
        self.current_tiller_count_label.grid(row=0, column=6, padx=2*padx, pady=pady)

        self.BBrowse = tk.Button(text="Browse", command=self.browse_button)
        self.BBrowse.grid(row=0, column=4)
        self.BBrowse = tk.Button(text="Apply", command=self.apply_Hooge_to_curr_img)
        self.BBrowse.grid(row=0, column=7)
        self.BStartLoad = tk.Button(text="Export", command=self.export)
        self.BStartLoad.grid(row=0, column=8)
        self.BStartLoad = tk.Button(text="Prev. image", command=self.prev_img)
        self.BStartLoad.grid(row=0, column=9)
        self.BStartLoad = tk.Button(text="Next image", command=self.next_img)
        self.BStartLoad.grid(row=0, column=10)

    def OnLButtonUp(self, event) -> None:
       """
       When user releases left button, add at the cursor's position a circle and add the tiller 
       to the list of manually added tillers. Update widget showing the cnts.
       """
       x = event.x # relative to top left corner of widget (mainframe)
       y = event.y 
       x_root = event.x_root  # relative to top left corner of screen 
       y_root = event.y_root

       if self._is_clk_in_img((x_root, y_root)):
          if self.tki_man_add.get() == 1:
             tiller = [0, 0, 0]
             tiller[0] = x #- self.ImgXStart
             tiller[1] = y #- self.ImgYStart
             tiller[2] = 10
             self._curr_man_add_tillers.append(tiller) # add new tiller to the list of manually added tillers
             self._add_man_tiller_to_curr_img(tiller)  # display new tiller in image
             self.current_tiller_count_label.config(text=str(len(self._curr_tillers) + len(self._curr_man_add_tillers))) # update cnt widget

    def OnRButtonUp(self, event) ->None:
       """
       When user releases left button, add at the cursor's position a circle and add the tiller 
       to the list of manually added tillers. Update widget showing the cnts.
       """
       if self.tki_man_add.get() == 1:
          x = event.x
          y = event.y
          self._remove_manual_tiller_from_curr_img(x, y) # removes tiller from 
          self.current_tiller_count_label.config(text=str(len(self._curr_tillers) + len(self._curr_man_add_tillers))) # update widget

    def browse_button(self, *args) -> None:
        self.dir_name = filedialog.askdirectory()
        self.dir_list = os.listdir(self.dir_name)
        self.dir_list.sort(key=lambda f: int(re.sub('\D', '', f)))
        self.tkstring_dir_path.set(self.dir_name)
        self.TillerCounter = CTillerCounter()
        self._show_start_img()

    def next_img(self) -> None:
        """ Loads next image and removes all detections. """
        if self.idx_img < len(self.dir_list) - 1:
          self.idx_img = self.idx_img + 1
          self.current_filename_label.config(text=self.dir_list[self.idx_img])
          self.current_tiller_count_label.config(text=str(0))
          self._curr_tillers = []
          self._curr_man_add_tillers = []
          self._man_removed_cnt = 0
          self._man_added_cnt = 0
          self._show_start_img()

    def prev_img(self) -> None:
      """ Loads prev image and removes all detections. """
      if self.idx_img > 0:
        self.idx_img = self.idx_img - 1
        self.current_filename_label.config(text=self.dir_list[self.idx_img])
        self.current_tiller_count_label.config(text=str(0))
        self._curr_tillers = []
        self._curr_man_add_tillers = []
        self._man_removed_cnt = 0
        self._man_added_cnt = 0
        self._show_start_img()

    def update_current_img(self):
        """ Updates the image after a new tiller has been added/removed"""
        self._draw_detected()
        self._show_current_image()

    def show_hide_detection(self):
        """ Toggle detections on/off """
        if self.tki_show_detected.get() == 1:
          self.update_current_img()
        else:
          self._show_start_img()

    def apply_Hooge_to_curr_img(self):
        Rmin = self.tki_r_min.get()
        Rmax = self.tki_r_max.get()
        MinDist = self.tki_min_dist.get()
        Param1 = self.tki_param1.get()
        Param2 = self.tki_param2.get()
        # calculates Tillers based on original image size
        self._curr_tillers = self.TillerCounter.auto_detect_tillers_in_curr_img(os.path.join(self.dir_name, self.dir_list[self.idx_img]), 
                                                                  Param1, Param2, Rmin, Rmax, MinDist)
        self.current_tiller_count_label.config(text=str(len(self._curr_tillers) + len(self._curr_man_add_tillers)))

        self._original_tiller_cnt = len(self._curr_tillers)
        self.update_current_img()
        self.tkcheck_detected.select()

        return None

    def export_img(self):
        """ Exports the actual image with circles indicating tiller positions """
        # Correct Image quality
        Test = self.dir_list[self.idx_img]
        Path = self.dir_name + Test 
        SplitPath = os.path.splitext(Path)
        FilenameWithoutExt = SplitPath[0]
        Filename = FilenameWithoutExt + "_cnt.jpg"
        self._draw_detected(bScaled = False) # -> draws on self._current_image_orig!
        self.current_image_orig.save(Filename) # original images is now annotated with all detected tillers!

    def export_all_tillers_pos(self):
       """ exports for a single image (current), all tiller positions to a file """
       Test = self.dir_list[self.idx_img]
       Path = self.dir_name + Test # + 
       SplitPath = os.path.splitext(Path)
       FilenameWithoutExt = SplitPath[0]
       Filename = FilenameWithoutExt + "_alltillers.txt"
       File = open(Filename, 'a')
       
       if os.stat(Filename).st_size == 0:
          Header = "X, Y, Radius\n"
          File.write(Header)# add header
       if self._curr_tillers != None:
          for Tiller in self._curr_tillers:
             Center = Tiller[0]
             X = Center[0]
             Y = Center[1]
             Radius = int(float(Tiller[1]) * (self.img_width / self.orig_img_height))
             TextToWrite = str(X) + ', ' + str(Y) + ',' + str(Radius) + '\n'
             File.write(TextToWrite)
       if self._curr_man_add_tillers != None:
           for Tiller in self._curr_man_add_tillers:
               (X, Y) = self._from_scaled_to_img(Tiller[0], Tiller[1])
               Radius = int(float(Tiller[2]) * (self.img_width / self.orig_img_height))
               TextToWrite = str(X) + ',' + str(Y) + ',' + str(Radius) + '\n'
               File.write(TextToWrite)
       File.close()


    def export_result(self):
      Filename = self.dir_name + "TillerCnts.txt"
      File = open(Filename, 'a')
      if os.stat(Filename).st_size == 0:
        Header = "Filename,Original Count,Manually Added,Manually Removed,Final Count\n"
        File.write(Header)# add header
      TextToWrite = self.dir_list[self.idx_img] + ', ' + str(self._original_tiller_cnt) + ',' + str(self._man_added_cnt) + ','  + str(self._man_removed_cnt) + ','+ str(len(self._curr_tillers) + len(self._curr_man_add_tillers)) + '\n'
      File.write(TextToWrite)
      File.close()

    def export(self):
      self.export_img()
      self.export_all_tillers_pos()
      self.export_result()

    def _is_clk_in_img(self, coord) -> bool:
        """ True if clk was in image showing tillers"""
        X = coord[0]
        Y = coord[1]
        # print(X)
        if USE_TWO_SCREENS:
          # check for your screen cofiguration
          if Y > self.img_y_start + OFFSET and X < self.img_width + IMG_WIDTH_LAPTOP*SCALE_DESKTOP_SCREEN+4*OFFSET: 
            return True
          else:
            return False
        else:
          if X > self.img_x_start and X < self.img_x_start + self.img_width and Y > self.img_y_start + OFFSET and Y < self.img_height + self.img_y_start + OFFSET:
            return True
          else:
            return False
        
    def _add_sample_name(self, *args):
        """ If user wants to add a sample name """
        self.samplename = self.tkstring_samplename.get()

    def _find_nearest_tiller(self, X, Y) -> tuple[int, int]:
         """ Calculate all Distances to all Tillers and returns nearest tiller (tuple of [id_min, dist(id_min)]). """
         Distance = []
         for tiller in self._curr_tillers:
           TempX = tiller[0][0]
           TempY = tiller[0][1]
           (TempXScaled, TempYScaled) = self._from_img_to_scaled(TempX, TempY)
           Distance.append(np.sqrt((TempXScaled - X) * (TempXScaled - X) +  (TempYScaled - Y) * (TempYScaled - Y)))
         return (np.argmin(Distance), Distance[np.argmin(Distance)])
    
    def _show_start_img(self):
        """ Called after directory is chosen: Shows scaled version of image """
        StartImgName = self.dir_list[self.idx_img]
        self.current_filename_label.config(text=self.dir_list[self.idx_img])
        self.samplename = StartImgName
        self.current_image_orig = Image.open(os.path.join(self.dir_name, StartImgName))
        self.orig_img_width = self.current_image_orig.size[0]
        self.orig_img_height = self.current_image_orig.size[1]
        self.current_image = self.current_image_orig.resize((self.img_width, self.img_height))
        self._show_current_image()

    def _show_current_image(self):
        """ Places the current image to the dialog. """
        Test = ImageTk.PhotoImage(self.current_image)
        label1 = tk.Label(image=Test)
        label1.image = Test
        # Position image
        label1.place(x=self.img_x_start, y=self.img_y_start)

    def _add_man_tiller_to_curr_img(self, Tiller):
        """ Draws "Tiller" into the image and adds the add_counter + 1. """
        Drawer = ImageDraw.Draw(self.current_image)
        X = Tiller[0] #+ self.ImgXStart
        Y = Tiller[1] #+ self.ImgYStart
        Drawer.point((X, Y), fill=self._color_man_tillers_outl)
        Drawer.ellipse([(X - self.r_man, Y - self.r_man), (X + self.r_man, Y + self.r_man)], fill = None, outline = self._color_man_tillers_outl ,width = 2)
        self._man_added_cnt = self._man_added_cnt + 1
        self._show_current_image()

    def _remove_manual_tiller_from_curr_img(self, X, Y):
        """ Removes tiller at X, Y if click is inside, from the image and adds to the rem_counter + 1. """
        (IdxNearestTiller, Distance) = self._find_nearest_tiller(X,Y)
        if Distance < (self.r_man + 4):
            del self._curr_tillers[IdxNearestTiller]          # removes tiller
            self._man_removed_cnt = self._man_removed_cnt + 1 # increases man_removed_cnt
            self._show_start_img()                            # replotting plain image
            self.update_current_img()                         # Redrawing of all tillers

    def _from_img_to_scaled(self, X, Y):
        """ Usually, original images needs to be scaled. orig -> scaled """
        XScaled = int(float(X) * (self.img_width / self.orig_img_width))
        YScaled = int(float(Y) * (self.img_height / self.orig_img_height))
        return (XScaled, YScaled)
  
    def _from_scaled_to_img(self, XScaled, YScaled):
      """ Usually, original images needs to be scaled. scaled -> orig """
      X = int(float(XScaled) * (self.orig_img_width / self.img_width))
      Y = int(float(YScaled) * (self.orig_img_height / self.img_height))
      return (X, Y)

    def _draw_detected(self, bScaled = True):
        """  Draw all detected tillers, automatic and manually added ones. """
        TillersScaled = []
        if bScaled == True:
          Drawer = ImageDraw.Draw(self.current_image)
          RminInt = 5
          Width = 2
        else:
          Drawer = ImageDraw.Draw(self.current_image_orig)
          RminInt = 15
          Width = 6
        if self._curr_tillers != None:
           for Tiller in self._curr_tillers:
             Center = Tiller[0]
             if bScaled == True:
               (X, Y) = self._from_img_to_scaled(Center[0], Center[1])
             else:
               X = Center[0]
               Y = Center[1]
             Radius = int(float(Tiller[1]) * (self.img_width / self.orig_img_height))
             CenterScaled = (X, Y)
             TillersScaled.append([CenterScaled, Radius])
             Drawer.point((X, Y), fill=self._color_auto_tillers_outl)
             Drawer.ellipse([(X - RminInt, Y - RminInt), (X + RminInt, Y + RminInt)], fill = None, outline = self._color_auto_tillers_outl ,width = Width)
        if self._curr_man_add_tillers != None:
           for Tiller in self._curr_man_add_tillers:
             if bScaled == True:
               X = Tiller[0]
               Y = Tiller[1]
             else:
               (X, Y) = self._from_scaled_to_img(Tiller[0], Tiller[1])
             Radius = int(float(Tiller[2]) * (self.img_width / self.orig_img_height))
             CenterScaled = (X, Y)
             TillersScaled.append([CenterScaled, Radius])
             Drawer.point((X, Y), fill=self._color_man_tillers_outl)
             Drawer.ellipse([(X - RminInt, Y - RminInt), (X + RminInt, Y + RminInt)], fill = None, outline = self._color_man_tillers_outl ,width = Width)


if __name__ == "__main__":
  app = CTillerCounterGui()
  app.mainloop()