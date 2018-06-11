BBox-Label-Tool-For-RetinaNet
=============================

**Links**  
 ・[RetinaNet](https://github.com/fizyr/keras-retinanet)    
 ・[BBox-Label-Tool](https://github.com/puzzledqs/BBox-Label-Tool)  
 ・[BBox-Label-Tool-Python3.x](https://github.com/Tomonori12/BBox-Label-Tool-Python3.x)   

**abstract**　　   
    BBox-Label-Tool is a image annotation tool for object detection using machine learning.         
    RetinaNet is one of machine learning object detection algorithmes.      
    I optimized BBox-Label-Tool for RetinaNet.     

**features**    
 ・You can draw boxes with the class information.     
 ・You can specify the directory path of the image.    
 
**remarks**    
 ・Finally,you would get some csv files for each images.Please merge these by yourself.   
 ・you can add and change classes by changing source directly. Check the below code.

       self.classNames = ['copper','shilver','iron','gold','carbon','other']
      
 ・Basic functions is the same as original one. Check the below original description.




BBox-Label-Tool
===============

A simple tool for labeling object bounding boxes in images, implemented with Python Tkinter.

**Updates:**
- 2017.5.21 Check out the ```multi-class``` branch for a multi-class version implemented by @jxgu1016

**Screenshot:**
![Label Tool](./screenshot.png)

Data Organization
-----------------
LabelTool  
|  
|--main.py   *# source code for the tool*  
|  
|--Images/   *# direcotry containing the images to be labeled*  
|  
|--Labels/   *# direcotry for the labeling results*  
|  
|--Examples/  *# direcotry for the example bboxes*  

Environment
----------
- python 2.7
- python PIL (Pillow)

Run
-------
$ python main.py

Usage
-----
0. The current tool requires that **the images to be labeled reside in /Images/001, /Images/002, etc. You will need to modify the code if you want to label images elsewhere**.
1. Input a folder number (e.g, 1, 2, 5...), and click `Load`. The images in the folder, along with a few example results will be loaded.
2. To create a new bounding box, left-click to select the first vertex. Moving the mouse to draw a rectangle, and left-click again to select the second vertex.
  - To cancel the bounding box while drawing, just press `<Esc>`.
  - To delete a existing bounding box, select it from the listbox, and click `Delete`.
  - To delete all existing bounding boxes in the image, simply click `ClearAll`.
3. After finishing one image, click `Next` to advance. Likewise, click `Prev` to reverse. Or, input an image id and click `Go` to navigate to the speficied image.
  - Be sure to click `Next` after finishing a image, or the result won't be saved. 
