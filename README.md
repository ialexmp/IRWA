# Information Retrieval and Web Analytics (IRWA)
## Group 
**Group:** G_201_4.

## Summary
Based on the learned from theoretical classes, the seminars, the lab exercises and our own research, we are asked to build using Python 3 a search engine implementing different indexing and ranking algorithms.
| Part | Topic | Delivery Date |
| --- | --- | --- |
| [Part 1](https://github.com/ialexmp/IRWA/tree/master/part-1)  | Text Processing and Exploratory Data Analysis | 21/10/2023 |
| [Part 2](https://github.com/ialexmp/IRWA/tree/master/part-2) | Indexing and Evaluation | 29/10/2023 |
| [Part 3](https://github.com/ialexmp/IRWA/tree/master/part-3) | Ranking | 14/11/2023
| [Part 4](https://github.com/ialexmp/IRWA/tree/master/part-4) | User Interface and Web Analytics  | 02/12/2023 |

## Project Instructions
### Part 1:
In this part of the project, you will find the initial steps. Among them, the importation of the different elements that will be used in the project, these documents are located in the Data folder. Furthermore, a character cleaning process for the tweets has been performed using the preprocess() function. For easier data analysis, a date format change has also been applied using preprocess_date().

Next, in the second section, we have conducted a series of studies to better understand the data. Some of the studies include: Word cloud, Histogram, Boxplot, ... The results of these studies can be observed [here](https://github.com/ialexmp/IRWA/blob/master/part-1/IRWA-2023-u189626-u186665-u186661-part-1.pdf).

Finally, it's worth mentioning that to execute this, you simply need to run each of the cells in order.

### Part 2:
In that case, the focus is on indexing and evaluation. Data preparation involves merging previous work into a new notebook, creating a new dataframe, and indexing tweets to construct inverted indexes. A custom function, "create_index," is developed for this purpose. A search engine, "search," is built to retrieve tweets for specific queries using keywords derived from word cloud analysis. The evaluation consists of two components: one involving a subset of the dataset and the other using expert judgment to assess document relevance. Various evaluation metrics are presented for different queries, comparing two cases (Case 1 and Case 2). The analysis also includes a two-dimensional scatter plot using the T-SNE algorithm to visualize relationships between tweets in the dataset, with a notable dense cluster of points suggesting similarities among tweets in that area and symmetrical distribution around the origin indicating balanced word embeddings.

### Part 3:
[In process...]

### Part 4: 
[In process...]
