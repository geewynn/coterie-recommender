# Kubeflow Recommendation Pipeline

## Preface
This project  explains the implementation technique for Collaborative-filtering workflow implementation for model training and deployment. Collaborative-filtering system operates by finding users with similar interests and provides recommendations to a user based on a similar interest accrued over time with another. This system will be designed to predict a user’s interest or suggest likely products the user might be interested in. At the end of this project, we will have a workflow process in place for building API for training and serving recommendation of products.

## Implementation Steps
1. Source of Data <br />
2. Transformation of Data<br />
3. Train Model<br /> 
4. Evaluation <br />


### Source of Data
Collaborative filtering is independent of the attribute of the users or the content. All that is needed, depending on the type of data, are the queries that will determine the recommendation to be made. <br />

### Transformation of Data
When the data has been pulled from github or other external source, the data is loaded using the read_csv function in pandas and then preprocessed establishing a 0-indexed set of unique IDs for users and items. The data is preprocessed to create two sparse ratings matrix from the data -- one for training and one for testing -- and prepared for matrix factorization. 

### Train Model
The model is trained using the  train function executing for the number of epochs or iterations. After a successful completion of the preferred number of iterations, the row and column factor tensors are evaluated in the session to produce numpy arrays for each factor. 

### Evaluation
For evaluation and to measure the performance of the model, there is the need to calculate the root mean square error (RMSE) or the mean square error (MSE) 
