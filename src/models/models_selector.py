import logging
from sklearn.model_selection import train_test_split, GridSearchCV # type: ignore
from sklearn.linear_model import LogisticRegression # type: ignore
from sklearn.tree import DecisionTreeClassifier # type: ignore
from sklearn.ensemble import RandomForestClassifier # type: ignore
from sklearn.neighbors import KNeighborsClassifier # type: ignore
from sklearn.metrics import accuracy_score # type: ignore
import xgboost as xgb 

logger = logging.getLogger(__name__)

SEED = 42

MODELS = {
    'LogisticRegression': {
        'model': LogisticRegression(random_state=SEED, max_iter=10_000),
        'param_grid': {
            'C': [5, 10, 50, 100],
            'solver': ['liblinear']
        }
    },
    'DecisionTreeClassifier': {
        'model': DecisionTreeClassifier(random_state=SEED),
        'param_grid': {
            'max_depth': [None, 5, 10, 20], 
            'min_samples_split': [2, 10, 20]
        }
    },
    'RandomForestClassifier': {
        'model': RandomForestClassifier(random_state=SEED, n_jobs=3),
        'param_grid': {
            'n_estimators': [400, 600, 800],
            'max_depth': [5, 10, 20],
            'max_samples': [0.8],
            'max_features': ['sqrt']
        }
    },
    'XGBClassifier': {
        'model': xgb.XGBClassifier(random_state=SEED, eval_metric='logloss'),
        'param_grid': {
            'max_depth': [3, 6, 10],
            'learning_rate': [0.001, 0.01, 0.1],
            'n_estimators': [200, 400, 600]
        }
    },
    'KNeighborsClassifier': {
        'model': KNeighborsClassifier(n_jobs=3),
        'param_grid': {
            'n_neighbors': [3, 5, 7, 9],
            'weights': ['uniform', 'distance']
        }
    }
}

def train_test(df, seed):
    """
    Splits the dataset into training and testing sets.

    Parameters:
        df (pl.DataFrame): Input dataset.
        seed (int): Random seed for reproducibility.

    Returns:
        tuple: X_train, X_test, y_train, y_test
    """
    X = df.drop("target").to_numpy()
    y = df.select("target").to_numpy().flatten()
    return train_test_split(X, y, test_size=0.2, random_state=1)

def find_best_model(df, seed):
    """
    Evaluates multiple models using GridSearchCV and selects the best one based on accuracy.

    Parameters:
        df (pl.DataFrame): Input dataset.
        seed (int): Random seed for reproducibility.

    Returns:
        dict: Best model, its parameters, and accuracy score.
    """
    
    X_train, X_test, y_train, y_test = train_test(df, seed)

    best_model = None
    best_score = 0
    best_name = None

    for name, config in MODELS.items():
        logger.info(f"Training {name}...")
        grid_search = GridSearchCV(config['model'], config['param_grid'], cv=5, scoring='accuracy', verbose=1)
        grid_search.fit(X_train, y_train)

        model = grid_search.best_estimator_
        y_pred = model.predict(X_test)
        score = accuracy_score(y_test, y_pred)

        logger.info(f"{name} accuracy: {score:.4f}")

        if score > best_score:
            best_score = score
            best_model = model
            best_name = name

    return {
        'model_name': best_name,
        'best_model': best_model,
        'accuracy': best_score
    }

