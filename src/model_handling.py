# Create a class to store all our models
class ModelStorer():
    
    def __init__(self):
        self.models = {}
        self.model_scores = pd.DataFrame(columns=['model', 'dataset', 'metric', 'value'])

    def add_model(self, model):
        self.models[model.model_name] = model
        self.model_scores = self.model_scores.append(model.model_scores)

    def validate_models(self):
        for name, model in self.models.items():
            model.score_model_validate()

            model_data = model.model_scores
            val_filter = model_data['dataset']=='validate'
            self.model_scores = self.model_scores.append(model_data[val_filter])
            
    def print_scores(self, metric='accuracy_score'):
        print(self.model_scores[ self.model_scores['metric'] == metric])
    
    def return_scores(self):
        return self.model_scores

    def plot_models_roc_curves(self, dataset='train'):
        fig, ax = plt.subplots(figsize=(6,6))
        for name, model in self.models.items():
            model.plot_model_roc_curve(ax, dataset)
        fig.suptitle(f'Model ROC Curves for {dataset.title()} Data')
        plt.show()

    def plot_models_scores(self, dataset='train'):
        data = self.model_scores
        g = sns.FacetGrid(data[data['dataset']==dataset], col="metric", col_wrap=2, height=4)
        g.map(sns.barplot, "value", "model", order=list(self.models.keys()))
        g.fig.subplots_adjust(top=0.9)
        g.fig.suptitle(f'Model Metrics for {dataset.title()} Data')

    def plot_models_confusion_matricies(self, dataset='train'):
        num_models = len(self.models.keys())

        nrows = 2
        ncols = math.ceil(num_models/nrows)

        fig, axes = plt.subplots(
                        nrows=nrows,
                        ncols=ncols,
                        figsize=(ncols*3, nrows*3)
        )
        fig.suptitle(f'Model Confusion Matricies for {dataset.title()} Data')

        # Turn off all the axes in case there is nothing to plot
        [ax.axis('off') for ax in axes.ravel()]


        for i, (name, model) in enumerate(self.models.items()):
            # Logic for making rows and columns for matrices
            row = i // ncols
            col = i % ncols
            ax = axes[row, col]
            ax.set_title(name)
            ax.set_axis_on() # turn back on the axis
            model.plot_model_confusion_matrix(ax, dataset)

        plt.tight_layout()

    def clear_models(self):
        self.models = {}

    def remove_model(self, model_name):
        del self.models[model_name]


class SaveModel():
     def __init__(self, 
                    model, 
                    X_train, 
                    X_test, 
                    y_train, 
                    y_test, 
                    X_tt,
                    y_tt,
                    X_val,
                    y_val,
                    model_name='None'):
               
               self.model = model
               self.model_name = model_name
               self.X_train = X_train
               self.X_test = X_test
               self.y_train = y_train
               self.y_test = y_test
               self.X_tt = X_tt
               self.y_tt = y_tt
               self.X_val = X_val
               self.y_val = y_val

     def info(self):
          print(f'-------{self.model_name} Information-------')
          print(f'Model: {self.model}')
         
     def score_model_train_test(self):
          # Fit on training data
          self.model.fit(self.X_train, self.y_train)
          # Predict on training and test data
          ytrain_hat = self.model.predict(self.X_train)
          ytest_hat = self.model.predict(self.X_test)

          # Create the model scores on train and test data
          self.model_scores = pd.DataFrame([
                         [self.model_name, 'train', 'accuracy_score', accuracy_score(self.y_train, ytrain_hat)],
                         [self.model_name, 'train', 'recall_score', recall_score(self.y_train, ytrain_hat)],
                         [self.model_name, 'train', 'precision_score', precision_score(self.y_train, ytrain_hat)],
                         [self.model_name, 'train', 'f1_score', f1_score(self.y_train, ytrain_hat)],
                         [self.model_name, 'test', 'accuracy_score', accuracy_score(self.y_test, ytest_hat)],
                         [self.model_name, 'test', 'recall_score', recall_score(self.y_test, ytest_hat)],
                         [self.model_name, 'test', 'precision_score', precision_score(self.y_test, ytest_hat)],
                         [self.model_name, 'test', 'f1_score', f1_score(self.y_test, ytest_hat)]
                         ],
                         columns=['model', 'dataset', 'metric', 'value'])
          
     def score_model_validate(self):
          # Train on the full dataset
          self.model.fit(self.X_tt, self.y_tt)

          # Predict results for the validate dataset
          yval_hat = self.model.predict(self.X_val)

          # Add the scores to the model scores
          self.model_scores = self.model_scores.append(
               pd.DataFrame([
                         [self.model_name, 'validate', 'accuracy_score', accuracy_score(self.y_val, yval_hat)],
                         [self.model_name, 'validate', 'recall_score', recall_score(self.y_val, yval_hat)],
                         [self.model_name, 'validate', 'precision_score', precision_score(self.y_val, yval_hat)],
                         [self.model_name, 'validate', 'f1_score', f1_score(self.y_val, yval_hat)],
                         ],
                         columns=['model', 'dataset', 'metric', 'value'])
          )

     def get_data(self, dataset):
          if dataset == 'train':
               x = self.X_train
               y = self.y_train
          elif dataset == 'test':
               x = self.X_test
               y = self.y_test
          elif dataset == 'validate':
               x = self.X_val
               y = self.y_val

          return x, y

     def plot_model_roc_curve(self, ax, dataset='train'):
          (x, y) = self.get_data(dataset)
          
          plot_roc_curve(self.model, x,y, ax=ax, name=self.model_name)

     def plot_model_confusion_matrix(self, ax, dataset='train'):
          (x, y) = self.get_data(dataset)

          cm_display = plot_confusion_matrix(self.model, 
                                             x,
                                             y, 
                                             normalize='true', 
                                             cmap='plasma',
                                             ax=ax)
          cm_display.im_.set_clim(0, 1)
    
