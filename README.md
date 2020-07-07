# GiordanoLucioMasterThesis
This repository has been created for the master thesis developed at the Universidad Complutense de Madrid. 
The objective of the project was to understand the K210 capabilities and use it in a real-life application. 
The application consists on a system for person detection which is used to determine in real-time, how many people
there are in an environment and monitor if some of them are too close. The nodes of the architecture are MaixGo board
equipped with the Kendryte K210 which is able to run small neural network for object detection based on yolo v2.
The different nodes can infer, according to their architecture, neural networks with real time performances.
We decided to control the application through an online broker, ThingSpeak. ThingSpeak is a platform especially designed for Internet of Things applications, 
which allows to gather data and visualize them directly. It has been decided to use ThingSpeak because it also permits to define some functions to be triggered
when a certain events occurs, or a certain value is encountered so, useful to monitor the values sent on the broker by the boards.
When a certain number of people are seen while being too close, the React on the ThingSpeak platform is triggered and a message is sent to the person in charge of monitoring
by using a thingHTTP which calls a previously defined WebHook on the IFTTT platform.

\\image of the architecture here

The neural network trained for person detection, are based on the aXeleRate framework which permits to train different neural networks for object detection based on yolo v2.
The back-ends used for yolo v2 are mobileNets with alpha = 0.25, alpha = 0.50 and alpha = 0.75 and Tiny Yolo. The conversion of the mobilenet in order to be used on the K210
has been done by Sipeed, the K210 owner.

As explained in the Thesis, none of the famous datasets tried for person-detection returned good results as it was, so it has been decided to merge some of them and label
again most of them in order to best fit our needs. 
In particular, the datasets used are:
Pascal-voc dataset: it contains more than 5000 images, labelled with the 20 Pascal-Voc classes.
Inria-pedestrian dataset: it contains more than 600 images on which only pedestrian are labelled.
Penn-Fudan pedestrian dataset: it contains 170 images with around 340 labelled pedestrians.

The Pascal-voc dataset contains labels for 20 different classes, comprehending person. A parser in python has been written to extract only the classes on which we are interested,
in our case, person. The parser reads the xml files and deletes all the classes on which we are not interested. After having parsed all the labels, the images that do not
contain any person have been discarded, making it an only person dataset. After that work, the tool labelImg has been used to check the integrity of the data and fix the uncorrect labels.
The same work of correcting labels has been done also for the Inria and the fudan datasets which were meant to only detect pedestrian, but we are interested on all the person, not only the pedestrians.
Several neural networks have been trained using those datasets and the one returning better results in terms of accuracy and performances, 
is yolo v2 built using mobilenet with alpha = 0.50 as feature extractor, trained using the merged dataset which contains around 3000 images. 
For Testing purposes, a dataset has been created by taking photos on the streets of Madrid by using the camera sensor ov2640 equipped on the MaixGo board used for this work. It contains 130 images containing at least 1 person.

The prepared datasets can be obtained through these links: 
\link validation: https://drive.google.com/uc?id=1drwtvsCxHWzhTPTs4uvVWqBoWex7jli1
\link merged: https://drive.google.com/uc?id=1vLvbc08BKP2acOCi_6iVB4BouFR8Foca
\link inria-fudan: https://drive.google.com/uc?id=1okVY5_vJ6wLrS_SOKha9t0FzGUwMzTb9
\link https://drive.google.com/uc?id=1h4c2tYSP2YamTaLvJa3uAwPPD3tS4XTv

The folder "scripts" contains a set of Jupyter Notebook which are used on Google Drive through Google colaboratory, to train neural network using Google's GPU.

