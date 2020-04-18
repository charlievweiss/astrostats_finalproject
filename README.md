TODOS:
- Write overview
- link to sources from paragraphs
- Write code overview

# Cosmic Ray Detection

## Table of Contents
- [Overview](#overview)
- [Code](#code)
- [Conclusions (Man or machine?)](#conclusions)
    * [Context](#context)
    * [K-means Algorithm Overview](#k-means-overview)
    * [K-means Performance](#k-means-performance)
    * [K-means Cluster Centers](#cluster-centers)
    * [Would edge detection work?](#edge-detection)
- [Poster](#poster)
- [References](#references)

<a name="overview"></a>
# Overview
TODO: Write this

<a name="code"></a>
# Code

<a name="conclusions"></a>
# Man or Machine? Which detects cosmic rays with more accuracy?
![Cosmic Rays vs. Not Cosmic Rays](https://github.com/charlievweiss/cosmic_ray_detection/blob/master/README_figures/CR_vs_NCR.png)

Given ~1000 6 x 6 pixel images of bright spots from
an image of space from the SAA database, k-means
(an unsupervised machine learning algorithm) can
predict the classification between cosmic rays and
non-cosmic rays with only 63% accuracy. So the answer to "Man or Machine" is:

Definitely Man.

<a name="context"></a>
## Context
![SAA Image](https://github.com/charlievweiss/cosmic_ray_detection/blob/master/README_figures/SAA_image1.png)

Cosmic rays have been integral to our understanding of the interstellar medium, physics, and the chemistry of the universe. From their discovery in 1912 by V.F. Hess to the construction of the identification of D mesons in 1971, the study of cosmic rays has informed our understanding of their high energy sources in the universe and the existence of new elementary particles, among many other important discoveries (Blumer, et. al. 2009). We can use cosmic rays to obtain more more detailed information about the physics of the interstellar medium than any other method can provide (Strong, et. al. 2007). Thus, cosmic rays are an incredible resource for many disciplines, and are more than worthy of further research. (Cox 2005, Nagano et. al 2000)

As sky surveys have developed technologically over time, the massive amounts of data available create a need for large-scale classification of cosmic rays versus other types of astronomical objects. More so, as our computational power increases, we have the ability to identify cosmic rays in an image in real-time, which allows us to study events that occur on a small enough timescale that they disappear by the time new measurements are taken. (Mahabal et. al. 2019, Djorgovski et. al. 2015). With this power, and the knowledge gained so far in the machine learning space, it is worth the time to apply machine learning algorithms in order to identify the locations of cosmic rays in any given image from a sky survey.

<a name="k-means-overview"></a>
## K-means Algorithm Overview
![K-means visualization](https://github.com/charlievweiss/cosmic_ray_detection/blob/master/README_figures/k_means_example.png)

[Image citation](https://nbviewer.jupyter.org/github/jakevdp/PythonDataScienceHandbook/blob/master/notebooks/05.11-K-Means.ipynb)

K-means is an unsupervised machine learning algorithm that splits data into distinct groups based on the items with the most similarity. Intuitively, if you see a graph with multiple groups of points, you would expect those to become clusters, as shown in the example graph above.

This is easy to visualize in 2D space. However, since I'm using 36 pixel images, each one has 36 dimensions. In order to visualize the similarities between them on a 2D graph, you have to apply Principle Component Analysis (PCA). PCA can reduce data to as few dimensions as you want by representing the data with vectors (called 'components') that represent the most important parts of the data. In this case, the first two components of the image set represent more than 50% of the original information, which gives us a pretty good glance at their similarity. Here's how similar the images are when represented by only their first 2 most important components:

![PC Curve](https://github.com/charlievweiss/cosmic_ray_detection/blob/master/README_figures/percent_retained.png) ![Images plotted with first 2 PCs](https://github.com/charlievweiss/cosmic_ray_detection/blob/master/README_figures/scatter_plot.png)

Intuitively, you can see that cosmic rays and non-cosmic rays DO NOT form obvious clusters. This probably means that k-means will have a hard time splitting them into accurate groups-- and it ended up performing about as badly as you'd expect:

![Accuracy score](https://github.com/charlievweiss/cosmic_ray_detection/blob/master/README_figures/Accuracy_score.png)

<a name="k-means-performance"></a>
## K-means Performance
![Pie Chart](https://github.com/charlievweiss/cosmic_ray_detection/blob/master/README_figures/pie_chart.png)

<a name="cluster-centers"></a>
## K-means Cluster Centers
![Cluster Centers](https://github.com/charlievweiss/cosmic_ray_detection/blob/master/README_figures/cluster_centers.png)

Above, you can see the cluster centers that the k-means algorithm created. Below, you can see the images closest to and farthest from the respective cluster centers. Interestingly enough, the True Labels of each of the images shown are "Not Cosmic Ray," which points to the extremely bad performance of the algorithm. 

![Distance in cluster](https://github.com/charlievweiss/cosmic_ray_detection/blob/master/README_figures/cluster_ex_with_labels.png)

<a name="edge-detection"></a>
## Would edge detection work? (No again!)

Since humans classify cosmic rays based on sharp edges in the image, I thought edge detection might also do a good job. To the right are three different methods of edge detection. (TODO: Explain what values mean in the image)

I decided to go with laplacian because it gives a gradient of edges, from soft to sharp. i thought if I could extract images with sharp edges, those would likely be ones with cosmic rays.

However, as you can see below, the values in the images after edge detection are also so similar between the classifications that it would be an even worse classification method than k-means.

![Edge detection methods](https://github.com/charlievweiss/cosmic_ray_detection/blob/master/README_figures/edge_detection_methods.png)
![Bar graph1](https://github.com/charlievweiss/cosmic_ray_detection/blob/master/README_figures/bar_max.png) ![Bar graph2](https://github.com/charlievweiss/cosmic_ray_detection/blob/master/README_figures/bar_mean.png)
![Bar graph3](https://github.com/charlievweiss/cosmic_ray_detection/blob/master/README_figures/bar_median.png) ![Bar graph4](https://github.com/charlievweiss/cosmic_ray_detection/blob/master/README_figures/bar_min.png)

<a name="poster"></a>
# Poster

![Poster](https://github.com/charlievweiss/cosmic_ray_detection/blob/master/README_figures/cosmic_ray_poster%20(2).ai)

<a name="references"></a>
# References

Blumer, J., Engel, R., & Horandel, J. R. (2009). Cosmic Rays from the Knee to the Highest 			Energies. ArXiv. Retrieved April 14, 2019, from https://arxiv.org/pdf/0904.0725.pdf.

Cox, D. P. (2005). The Three-Phase Interstellar Medium Revisted. Annu. Rev. Astron. 			Astrophys.doi:10.1146/annurev.astro.43.072103.150615

Djorgovski, S. G., Graham, M. J., Mahabal, A. A., Drake, A. J., Turmon, M., & Fuchs, T. (2015). 		Real-Time Data Mining of Massive Data Streams from Synoptic Sky Survesy. Future 		Generation Computer Systems. Retrieved April 14, 2019, from 						https://arxiv.org/pdf/1601.04385.pdf.

Mahabal, A., et. al.(2019). Machine Learning for the Zwicky Transient Facility. Astronomcal 		Society of the Pacific. Retrieved April 14, 2019, from 							https://arxiv.org/pdf/1902.01936.pdf.

Nagano, M., & Watson, A. A. (2000). Observations and implications of the ultrahigh-enegy 		cosmic rays. Reviews of Modern Physics,72(689). Retrieved April 14, 2019, from 			https://journals.aps.org/rmp/abstract/10.1103/RevModPhys.72.689.

Strong, A. W., Moskalenko, I. V., & Ptuskin, V. S. (2007). Cosmic-ray propagation and 			interactions in the Galaxy. ArXiv,1. Retrieved April 14, 2019, from 					https://ui.adsabs.harvard.edu/abs/2007ARNPS..57..285S/abstract.
