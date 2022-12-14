# How Are You?
L'etichettatore semi-automatico per la generazione di dataset FER-2013 like.

---

Progetto del corso di Visione e Percezione, a.a. 2021/2022

**Docente** &nbsp;&nbsp;Domenico Daniele Bloisi

**Studente** &nbsp;Dario Satriani - 61196

---

## Dipendenze
1. [miniforge](https://github.com/conda-forge/miniforge)

## How To
Una volta installato [miniforge](https://github.com/conda-forge/miniforge), per eseguire l'applicativo è necessario creare il relativo ambiente Anaconda.

Per farlo è sufficiente, dalla cartella radice, eseguire il comando
```shell
conda env create -f conda-env/environment.yml

# Nel caso di MacOS con processore M1
# CONDA_SUBDIR=osx-64 conda env create --file=conda-env/environment.yml
```

A questo punto l'environment può essere attivato utilizzando il comando
```shell
conda activate satriani-vep
```

Il progetto può essere quindi avviato utilizzando il comando
```shell
python app/emotion_labeler/main.py
```
*Attenzione: al primo avvio l'applicazione potrebbe richiedere un po' di tempo in fase di inizializzazione*

---

*Nota:* Il procedimento è analogo per l'esecuizione dell'applicazione delle emoji ad eccezione dell'ultimo comando che diventa
```shell
python app/emoji_detector/main.py
```

Nel caso dell'applicazione "Video Emotion Detection" è necessario specificare il path assoluto del video che si vuole analizzare (obbligatorio) e il tipo di modello di MediaPipe da utilizzare (opzionale, il valore di default è 1)
```shell
python app/video_emotion_detection/main.py path_assoluto_del_video

# Volendo utilizzare il modello di detection 0
# python app/video_emotion_detection/main.py path_assoluto_del_video 0
```
## Riferimenti
**Dataset**  
<a href="https://www.kaggle.com/datasets/msambare/fer2013" target="_blank">FER-2013</a>  
  
**VGG-16**  
<a href="https://arxiv.org/pdf/1409.1556.pdf" target="_blank">
Karen Simonyan, Andrew Zisserman - VERY DEEP CONVOLUTIONAL NETWORKS FOR LARGE-SCALE
IMAGE RECOGNITION
</a>  
  
<a href="https://towardsdatascience.com/step-by-step-vgg16-implementation-in-keras-for-beginners-a833c686ae6c" target="_blank">Towards Data Science - VGG-16 overview</a>  
  
<a href="https://github.com/jhan15/facial_emotion_recognition" target="_blank">@jhan15 - Facial Emotion Recognition</a>  
  
**ResNetV2**  
<a href="https://arxiv.org/pdf/1602.07261v2.pdf" target="_blank">
Christian Szegedy, Sergey Ioffe, Vincent Vanhoucke, Alex Alemi - Inception-v4,
Inception-ResNet and the Impact of Residual Connections on Learning</a>  
  
<a href="https://keras.io/api/applications/resnet/#resnet50v2-function" target="_blank">Keras ResNet50V2</a>  
  
<a href="https://paperswithcode.com/method/inception-resnet-v2" target="_blank">Papers with Code - Inception-ResNet-v2</a>  
  
**DeepFace**  
<a href="https://github.com/serengil/deepface" target="_blank">DeepFace</a>
