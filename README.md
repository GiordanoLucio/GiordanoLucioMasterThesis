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

<img src="https://github.com/GiordanoLucio/GiordanoLucioMasterThesis/blob/master/images/architecture.JPG?raw=true" width=600>


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

<!-- <img src="https://github.com/GiordanoLucio/GiordanoLucioMasterThesis/blob/master/images/training.JPG?raw=true" width=600> -->

| Model Backend        | Dataset       | Epochs | mAp  | Fscore | Precision | Recall |
|----------------------|---------------|--------|------|--------|-----------|--------|
| MobileNet alpha=0.75 | mergedDataset | 300    | 0.35 | 0.66   | 0.75      | 0.59   |
| MobileNet alpha=0.75 | PascalVoc     | 300    | 0.17 | 0.098  | 0.375     | 0.056  |
| MobileNet alpha=0.75 | Inria         | 300    | 0.22 | 0.25   | 0.314     | 0.207  |
| MobileNet alpha=0.75 | InriaFudan    | 300    | 0.22 | 0.22   | 0.218     | 0.226  |
| MobileNet alpha=0.50 | mergedDataset | 300    | 0.35 | 0.66   | 0.74      | 0.60   |
| MobileNet alpha=0.25 | mergedDataset | 300    | 0.22 | 0.67   | 0.775     | 0.584  |
| Tiny Yolo            | mergedDataset | 300    | 0.23 | 0.559  | 0.65      | 0.490  |

For Testing purposes, a dataset has been created by taking photos on the streets of Madrid by using the camera sensor ov2640 equipped on the MaixGo board used for this work. It contains 130 images containing at least 1 person.

<img src="https://github.com/GiordanoLucio/GiordanoLucioMasterThesis/blob/master/images/testing.JPG?raw=true" width=600>

The prepared datasets can be obtained through these links: 

- Training_merged: https://drive.google.com/file/d/1vLvbc08BKP2acOCi_6iVB4BouFR8Foca/view?usp=sharing
- Training_inria-fudan: https://drive.google.com/file/d/1okVY5_vJ6wLrS_SOKha9t0FzGUwMzTb9/view?usp=sharing
- Training_fudan: https://drive.google.com/file/d/1UTUoGip8gCK3HN_QlFdDkfWbElEZNpYa/view?usp=sharing
- validation: https://drive.google.com/file/d/1drwtvsCxHWzhTPTs4uvVWqBoWex7jli1/view?usp=sharing
- testing: https://drive.google.com/file/d/1h4c2tYSP2YamTaLvJa3uAwPPD3tS4XTv/view?usp=sharing

For the training of the Network, a set of Jupyter Notebooks are provided. Those Notebooks are used on Google Drive through Google colaboratory, to train neural networks using Google's GPU.
The notebooks can be opened directly in colab by using these links:

- Training Yolo v2 Detection with TinyYolo as backend: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1Ti6EBcglbc51PYyQ45pwRaylU2v0sCvj?usp=sharing)

- Training Yolo v2 Detection with MobileNet with alpha=0.75 as backend: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1hWjQul1COpT5i0W0CbdbhJZWHdGxuzsk?usp=sharing)

- Training Yolo v2 Detection with MobileNet with alpha=0.50 as backend [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1bKf1seGavhgPVu8Q4ZbIfaIyT-zcdkxo?usp=sharing)


