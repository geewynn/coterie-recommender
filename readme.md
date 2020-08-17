# Kubeflow Recommendation Pipeline

## Mavencode
![](images/Logo_White.png)

[MavenCode](https://www.mavencode.com/) is a provider of consulting services and expertise for building and implementing large scale distributed reactive backend systems for processing massive large scale datasets. We are responsible for putting this open source project together. The **goal** is to create a community for the development of a recommenntdation system that would be applied in different use cases like ecommerce, health etc. 

## Project Overview
This project explains the implementation technique for Collaborative-filtering workflow implementation for model training and deployment. Collaborative-filtering system operates by finding users with similar interests and provides recommendations to a user based on a similar interest accrued over time with another. This system will be designed to predict a user’s interest or suggest likely products the user might be interested in. At the end of this project, we will have a workflow process in place for building API for training and serving recommendation of products.

## Project Outline
  1. Data Gathering
  2. Data transformation and Preprocessing
  3. Model Building and Training
  4. Kubeflow Pipeline
  5. Validation (Hyperparameter Tuning)
  6. Deployment
 
## Collaborative-filtering
Generally , a recommender system  filters information and  seeks to predict the preference of a user, such as a product, movie, song, etc. Recommender systems provide personalized information by learning and making predictions based on a user's past behaviors. With the collaborative filtering aprroach we are able anticipate a user's interest using the interactions and data collected by the system from other users. The idea is when you are about to see a movie or buy a book you are more likely to speak with a friend whom you beleive has a similar taste for recommendations on what to watch or buy.

**Assumptions**
1. Users give ratings to items purchased whether implicitly or explicitly.
2. Users tastes are correlated.

![](images/Collaborative%20filtering.PNG)

## WALS method for matrix factorization
A key issue with Collaborative filtering is the **sparsity problem** which can be solved using matrix factorization. Matrix factorization is a class of collaborative filtering algorithms used in recommender systems. It is a simple embedding model that works by decomposing the user-item interaction matrix UV into the product of two lower dimensionality rectangular matrices. Lets say a user as never rated a product before, the matrix entry is zero. What matrix factorization does is to get back the original matrix by performing a dot product of the user and item matrix. The Weighted alternating least squares (WALS) method downgrades unrated items/products so such items don't drown the total loss. It does this by weighting the loss.

![](images/matrix%20factorization.PNG)

## Kubeflow Pipeline
A [Kubeflow Pipeline](https://www.kubeflow.org/docs/pipelines/overview/pipelines-overview/) is a platform for building and deploying portable, scalable machine learning (ML) workflows based on Docker containers. After gathering the data, preprocesing and building the model, the kubeflow pipeline would be built to ensure the process is reusable and the Machine learning workflow is automated.
