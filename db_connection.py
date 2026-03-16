import pandas as pd
from Model.train_model_crypto import Models


model = Models(number_days= 15, name="btc")
X_train, y_train, X_test, y_test = model.clean_dataset()
model.train_model(True)
prediction = model.test_model()
r = model.eval_r_squared()
a = model.directional_accuracy()
print(r)
print(a)

